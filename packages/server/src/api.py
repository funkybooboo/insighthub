"""
Flask REST API for InsightHub RAG system.

This module provides a loosely coupled REST API interface for document upload
and chat interactions with the RAG system.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, Response, g, jsonify, request
from flask_cors import CORS
from pypdf import PdfReader
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from src.db.repository import (
    ChatMessageRepository,
    ChatSessionRepository,
    DocumentRepository,
    UserRepository,
)
from src.db.session import get_db, init_db

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration from environment variables
UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", "uploads"))
ALLOWED_EXTENSIONS = {"txt", "pdf"}
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Initialize database
try:
    init_db()
except Exception as e:
    print(f"Warning: Could not initialize database: {e}")


def get_db_session() -> Any:
    """Get database session for the current request."""
    if "db" not in g:
        g.db = next(get_db())
    return g.db


@app.teardown_appcontext
def close_db(error: Any) -> None:
    """Close database session at the end of the request."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text content from a PDF file."""
    reader = PdfReader(str(file_path))
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n".join(text_parts)


def extract_text_from_txt(file_path: Path) -> str:
    """Extract text content from a TXT file."""
    with open(file_path, encoding="utf-8") as f:
        return f.read()


def process_uploaded_file(file_path: Path, filename: str) -> dict[str, Any]:
    """Process an uploaded file and extract its text content."""
    extension = filename.rsplit(".", 1)[1].lower()

    if extension == "pdf":
        text = extract_text_from_pdf(file_path)
    elif extension == "txt":
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

    return {"filename": filename, "text": text, "type": extension}


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_or_create_default_user(db: Any) -> Any:
    """Get or create a default user for demo purposes."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_username("demo_user")
    if not user:
        user = user_repo.create(
            username="demo_user", email="demo@insighthub.local", full_name="Demo User"
        )
    return user


@app.route("/heartbeat", methods=["GET"])
def heartbeat() -> tuple[str, int]:
    """Simple heartbeat endpoint that returns 200 OK."""
    return "", 200


@app.route("/health", methods=["GET"])
def health() -> tuple[Response, int]:
    """Health check endpoint with status information."""
    return jsonify({"status": "healthy"}), 200


@app.route("/api/upload", methods=["POST"])
def upload_document() -> tuple[Response, int]:
    """
    Upload a document (PDF or TXT) to the system.

    Returns:
        JSON response with document ID and metadata
    """
    # Check if file is present in request
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file: FileStorage = request.files["file"]

    # Check if file is selected
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Validate file
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = UPLOAD_FOLDER / filename

        # Save file
        file.save(str(file_path))

        try:
            # Get database session and user
            db = get_db_session()
            user = get_or_create_default_user(db)

            # Calculate file hash
            content_hash = calculate_file_hash(file_path)

            # Check if document already exists
            doc_repo = DocumentRepository(db)
            existing_doc = doc_repo.get_by_content_hash(content_hash)
            if existing_doc:
                return (
                    jsonify(
                        {
                            "message": "Document already exists",
                            "document": {
                                "id": existing_doc.id,
                                "filename": existing_doc.filename,
                                "file_size": existing_doc.file_size,
                                "created_at": existing_doc.created_at.isoformat(),
                            },
                        }
                    ),
                    200,
                )

            # Process file
            document_data = process_uploaded_file(file_path, filename)

            # Get file size and mime type
            file_size = file_path.stat().st_size
            extension = filename.rsplit(".", 1)[1].lower()
            mime_type = "application/pdf" if extension == "pdf" else "text/plain"

            # Create document in database
            document = doc_repo.create(
                user_id=user.id,
                filename=filename,
                file_path=str(file_path),
                file_size=file_size,
                mime_type=mime_type,
                content_hash=content_hash,
            )

            # TODO: Integrate with RAG system here
            # rag_system.add_documents([{"text": document_data["text"], "metadata": {...}}])
            # Update document with chunk_count and rag_collection after RAG processing

            return (
                jsonify(
                    {
                        "message": "Document uploaded successfully",
                        "document": {
                            "id": document.id,
                            "filename": document.filename,
                            "file_size": document.file_size,
                            "mime_type": document.mime_type,
                            "text_length": len(document_data["text"]),
                            "created_at": document.created_at.isoformat(),
                        },
                    }
                ),
                201,
            )

        except Exception as e:
            # Clean up file on error
            if file_path.exists():
                os.remove(file_path)
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500

    return jsonify({"error": "Invalid file type. Only PDF and TXT files are allowed"}), 400


@app.route("/api/chat", methods=["POST"])
def chat() -> tuple[Response, int]:
    """
    Handle chat messages and return responses from the RAG system.

    Expected JSON payload:
        {
            "message": "User's question",
            "session_id": "optional-session-id",
            "rag_type": "vector" (optional, defaults to vector)
        }

    Returns:
        JSON response with answer and relevant context
    """
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"]
    session_id = data.get("session_id")
    rag_type = data.get("rag_type", "vector")

    try:
        # Get database session and user
        db = get_db_session()
        user = get_or_create_default_user(db)

        # Get or create chat session
        session_repo = ChatSessionRepository(db)
        if session_id:
            session = session_repo.get_by_id(int(session_id))
            if not session:
                return jsonify({"error": "Session not found"}), 404
        else:
            # Create new session with first message as title
            title = user_message[:50] + "..." if len(user_message) > 50 else user_message
            session = session_repo.create(user_id=user.id, title=title, rag_type=rag_type)

        # Store user message
        message_repo = ChatMessageRepository(db)
        message_repo.create(session_id=session.id, role="user", content=user_message)

        # TODO: Integrate with RAG system here
        # results = rag_system.query(user_message, top_k=5)
        # answer = results["answer"]
        # context = results["context"]

        # For now, return a mock response
        mock_answer = f"This is a mock response to: {user_message}"
        mock_context = [
            {
                "text": "Sample context chunk 1",
                "score": 0.85,
                "metadata": {"source": "document_1"},
            },
            {
                "text": "Sample context chunk 2",
                "score": 0.78,
                "metadata": {"source": "document_2"},
            },
        ]

        # Store assistant response with metadata
        metadata_json = json.dumps(
            {"context_chunks": len(mock_context), "rag_type": rag_type}
        )
        message_repo.create(
            session_id=session.id, role="assistant", content=mock_answer, metadata=metadata_json
        )

        # Get document count
        doc_repo = DocumentRepository(db)
        documents = doc_repo.get_by_user(user.id)

        response = {
            "answer": mock_answer,
            "context": mock_context,
            "session_id": session.id,
            "documents_count": len(documents),
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Error processing chat: {str(e)}"}), 500


@app.route("/api/documents", methods=["GET"])
def list_documents() -> tuple[Response, int]:
    """
    List all uploaded documents.

    Returns:
        JSON response with list of documents
    """
    try:
        db = get_db_session()
        user = get_or_create_default_user(db)

        doc_repo = DocumentRepository(db)
        documents = doc_repo.get_by_user(user.id)

        docs_list = [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_size": doc.file_size,
                "mime_type": doc.mime_type,
                "chunk_count": doc.chunk_count,
                "created_at": doc.created_at.isoformat(),
            }
            for doc in documents
        ]

        return jsonify({"documents": docs_list, "count": len(docs_list)}), 200

    except Exception as e:
        return jsonify({"error": f"Error listing documents: {str(e)}"}), 500


@app.route("/api/documents/<int:doc_id>", methods=["DELETE"])
def delete_document(doc_id: int) -> tuple[Response, int]:
    """
    Delete a document by ID.

    Args:
        doc_id: The document ID to delete

    Returns:
        JSON response confirming deletion
    """
    try:
        db = get_db_session()
        doc_repo = DocumentRepository(db)

        # Find document
        document = doc_repo.get_by_id(doc_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404

        # Delete file
        file_path = Path(document.file_path)
        if file_path.exists():
            os.remove(file_path)

        # Delete from database
        doc_repo.delete(doc_id)

        # TODO: Remove from RAG system
        # rag_system.remove_document(doc_id)

        return jsonify({"message": "Document deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Error deleting document: {str(e)}"}), 500


@app.route("/api/sessions", methods=["GET"])
def list_sessions() -> tuple[Response, int]:
    """
    List all chat sessions for the current user.

    Returns:
        JSON response with list of chat sessions
    """
    try:
        db = get_db_session()
        user = get_or_create_default_user(db)

        session_repo = ChatSessionRepository(db)
        sessions = session_repo.get_by_user(user.id)

        sessions_list = [
            {
                "id": session.id,
                "title": session.title,
                "rag_type": session.rag_type,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
            }
            for session in sessions
        ]

        return jsonify({"sessions": sessions_list, "count": len(sessions_list)}), 200

    except Exception as e:
        return jsonify({"error": f"Error listing sessions: {str(e)}"}), 500


@app.route("/api/sessions/<int:session_id>/messages", methods=["GET"])
def get_session_messages(session_id: int) -> tuple[Response, int]:
    """
    Get all messages for a specific chat session.

    Args:
        session_id: The chat session ID

    Returns:
        JSON response with list of messages
    """
    try:
        db = get_db_session()
        message_repo = ChatMessageRepository(db)

        messages = message_repo.get_by_session(session_id)

        messages_list = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "metadata": json.loads(msg.extra_metadata) if msg.extra_metadata else None,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in messages
        ]

        return jsonify({"messages": messages_list, "count": len(messages_list)}), 200

    except Exception as e:
        return jsonify({"error": f"Error getting messages: {str(e)}"}), 500


def run_server(host: str | None = None, port: int | None = None, debug: bool | None = None) -> None:
    """
    Run the Flask development server.

    Args:
        host: Host to bind to (defaults to FLASK_HOST env var or 0.0.0.0)
        port: Port to listen on (defaults to FLASK_PORT env var or 5000)
        debug: Enable debug mode (defaults to FLASK_DEBUG env var or True)
    """
    server_host = host or os.getenv("FLASK_HOST", "0.0.0.0")
    server_port = port or int(os.getenv("FLASK_PORT", "5000"))
    server_debug = (
        debug if debug is not None else os.getenv("FLASK_DEBUG", "True").lower() == "true"
    )

    app.run(host=server_host, port=server_port, debug=server_debug)


if __name__ == "__main__":
    run_server()
