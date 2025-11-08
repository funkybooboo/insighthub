"""Document routes."""

import os
from pathlib import Path

from flask import Blueprint, Response, g, jsonify, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")

# Configuration
UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", "uploads"))
ALLOWED_EXTENSIONS = {"txt", "pdf"}

# Ensure upload directory exists
UPLOAD_FOLDER.mkdir(exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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

    # Validate file type
    if not file or not file.filename or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDF and TXT files are allowed"}), 400

    filename = secure_filename(file.filename)
    file_path = UPLOAD_FOLDER / filename

    # Save file temporarily
    file.save(str(file_path))

    try:
        # Get user
        user = g.app_context.user_service.get_or_create_default_user()

        # Process document upload using service orchestration method
        with open(file_path, "rb") as f:
            result = g.app_context.document_service.process_document_upload(
                user_id=user.id,
                filename=filename,
                file_obj=f,
            )

        # Prepare response based on whether it was a duplicate
        message = (
            "Document already exists" if result.is_duplicate else "Document uploaded successfully"
        )
        status_code = 200 if result.is_duplicate else 201

        return (
            jsonify(
                {
                    "message": message,
                    "document": {
                        "id": result.document.id,
                        "filename": result.document.filename,
                        "file_size": result.document.file_size,
                        "mime_type": result.document.mime_type,
                        "text_length": result.text_length,
                        "created_at": result.document.created_at.isoformat(),
                    },
                }
            ),
            status_code,
        )

    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

    finally:
        # Clean up temp file
        if file_path.exists():
            os.remove(file_path)


@documents_bp.route("", methods=["GET"])
def list_documents() -> tuple[Response, int]:
    """
    List all uploaded documents.

    Returns:
        JSON response with list of documents
    """
    try:
        user = g.app_context.user_service.get_or_create_default_user()
        documents = g.app_context.document_service.list_user_documents(user.id)

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
        # Check if document exists
        document = g.app_context.document_service.get_document_by_id(doc_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404

        # Delete document (service handles blob storage cleanup)
        g.app_context.document_service.delete_document(doc_id, delete_from_storage=True)

        # TODO: Remove from RAG system
        # rag_system.remove_document(doc_id)

        return jsonify({"message": "Document deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Error deleting document: {str(e)}"}), 500
