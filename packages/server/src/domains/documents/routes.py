"""Document routes."""

import os
from pathlib import Path

from flask import Blueprint, Response, g, jsonify, request
from shared.exceptions import ValidationError
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from src.infrastructure.auth import get_current_user, require_auth

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")

# Configuration
UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", "uploads"))

# Ensure upload directory exists
UPLOAD_FOLDER.mkdir(exist_ok=True)


@documents_bp.route("/upload", methods=["POST"])
@require_auth
def upload_document() -> tuple[Response, int]:
    """
    Upload a document (PDF or TXT) to the system.

    Returns:
        JSON response with document ID and metadata

    Raises:
        ValidationError: If file validation fails
        DocumentProcessingError: If document processing fails
    """

    # Check if file is present in request
    if "file" not in request.files:
        raise ValidationError("No file part in request")

    file: FileStorage = request.files["file"]

    # Check if file is selected
    if not file.filename or file.filename == "":
        raise ValidationError("No file selected")

    filename = secure_filename(file.filename)
    file_path = UPLOAD_FOLDER / filename

    # Save file temporarily
    file.save(str(file_path))

    try:
        # Get authenticated user
        user = get_current_user()

        # Use service method that handles validation, upload, and DTO conversion
        with open(file_path, "rb") as f:
            response_dto = g.app_context.document_service.upload_document_with_user(
                user_id=user.id,
                filename=filename,
                file_obj=f,
            )

        # Determine status code based on duplicate flag
        status_code = 200 if "already exists" in response_dto.message else 201

        return jsonify(response_dto.to_dict()), status_code

    finally:
        # Clean up temp file
        if file_path.exists():
            os.remove(file_path)


@documents_bp.route("", methods=["GET"])
@require_auth
def list_documents() -> tuple[Response, int]:
    """
    List all uploaded documents.

    Returns:
        JSON response with list of documents
    """
    user = get_current_user()

    # Use service method that returns DTO
    response_dto = g.app_context.document_service.list_user_documents_as_dto(user.id)

    return jsonify(response_dto.to_dict()), 200


@documents_bp.route("/<int:doc_id>", methods=["DELETE"])
@require_auth
def delete_document(doc_id: int) -> tuple[Response, int]:
    """
    Delete a document by ID.

    Args:
        doc_id: The document ID to delete

    Returns:
        JSON response confirming deletion

    Raises:
        DocumentNotFoundError: If document does not exist
    """
    # Use service method that handles validation and deletion
    # Note: RAG removal is handled in service layer (see DocumentService.delete_document_with_validation)
    g.app_context.document_service.delete_document_with_validation(doc_id)

    return jsonify({"message": "Document deleted successfully"}), 200
