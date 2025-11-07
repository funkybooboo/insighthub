"""Document routes."""

import os
from pathlib import Path

from flask import Blueprint, Response, g, jsonify, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from src.context import AppContext, create_app_context

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")

# Configuration
UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", "uploads"))
ALLOWED_EXTENSIONS = {"txt", "pdf"}

# Ensure upload directory exists
UPLOAD_FOLDER.mkdir(exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_app_context() -> AppContext:
    """Get application context from Flask g object."""
    if not hasattr(g, "app_context"):
        g.app_context = create_app_context(g.db)
    return g.app_context


@documents_bp.route("/upload", methods=["POST"])
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
            # Get services from context
            ctx = get_app_context()

            # Get user
            user = ctx.user_service.get_or_create_default_user()

            # Determine mime type
            extension = filename.rsplit(".", 1)[1].lower()
            mime_type = "application/pdf" if extension == "pdf" else "text/plain"

            # Open file for processing
            with open(file_path, "rb") as f:
                # Check for duplicates
                content_hash = ctx.document_service.calculate_file_hash(f)
                existing_doc = ctx.document_service.get_document_by_hash(content_hash)
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

                # Extract text for RAG processing
                f.seek(0)
                text = ctx.document_service.extract_text(f, filename)

                # Upload document to blob storage and database
                f.seek(0)
                document = ctx.document_service.upload_document(
                    user_id=user.id, filename=filename, file_obj=f, mime_type=mime_type
                )

            # TODO: Integrate with RAG system here
            # rag_system.add_documents([{"text": text, "metadata": {...}}])
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
                            "text_length": len(text),
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


@documents_bp.route("", methods=["GET"])
def list_documents() -> tuple[Response, int]:
    """
    List all uploaded documents.

    Returns:
        JSON response with list of documents
    """
    try:
        ctx = get_app_context()

        user = ctx.user_service.get_or_create_default_user()
        documents = ctx.document_service.list_user_documents(user.id)

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


@documents_bp.route("/<int:doc_id>", methods=["DELETE"])
def delete_document(doc_id: int) -> tuple[Response, int]:
    """
    Delete a document by ID.

    Args:
        doc_id: The document ID to delete

    Returns:
        JSON response confirming deletion
    """
    try:
        ctx = get_app_context()

        # Check if document exists
        document = ctx.document_service.get_document_by_id(doc_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404

        # Delete document (including file)
        ctx.document_service.delete_document(doc_id, delete_from_storage=True)

        # TODO: Remove from RAG system
        # rag_system.remove_document(doc_id)

        return jsonify({"message": "Document deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Error deleting document: {str(e)}"}), 500
