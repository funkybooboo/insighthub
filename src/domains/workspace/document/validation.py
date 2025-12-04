"""Document input validation."""

from pathlib import Path

from returns.result import Failure, Result, Success

from src.domains.workspace.document.dtos import (
    DeleteDocumentRequest,
    ShowDocumentRequest,
    UploadDocumentRequest,
)
from src.infrastructure.types import ValidationError
from src.infrastructure.validation import validate_positive_id


def validate_upload_document(
    request: UploadDocumentRequest,
) -> Result[UploadDocumentRequest, ValidationError]:
    """Validate document upload input.

    Args:
        request: Raw user input request

    Returns:
        Result with cleaned UploadDocumentRequest or ValidationError
    """
    # Use infrastructure utility for ID validation
    workspace_id_result = validate_positive_id(request.workspace_id, "workspace_id")
    if isinstance(workspace_id_result, Failure):
        return Failure(workspace_id_result.failure())

    # Validate filename
    if not request.filename or not request.filename.strip():
        return Failure(ValidationError("Filename cannot be empty", field="filename"))

    filename = request.filename.strip()
    if len(filename) > 255:
        return Failure(ValidationError("Filename too long (max 255 characters)", field="filename"))

    # Validate file_path
    if not request.file_path or not request.file_path.strip():
        return Failure(ValidationError("File path cannot be empty", field="file_path"))

    file_path = Path(request.file_path.strip()).resolve()

    # Check file exists
    if not file_path.exists():
        return Failure(ValidationError(f"File not found: {file_path}", field="file_path"))

    # Security: Prevent uploading system files or files from sensitive directories
    sensitive_paths = [
        "/etc",
        "/sys",
        "/proc",
        "/dev",
        "/boot",
        "/root",
        "/var/log",
    ]

    for sensitive in sensitive_paths:
        try:
            if file_path.is_relative_to(sensitive):
                return Failure(
                    ValidationError(
                        f"Cannot upload files from system directory: {sensitive}",
                        field="file_path",
                    )
                )
        except ValueError:
            # is_relative_to raises ValueError on Windows for incompatible paths
            pass

    # Check for common system file patterns on Windows
    if file_path.parts and len(file_path.parts) > 0:
        first_part = str(file_path.parts[0]).lower()
        if "windows" in first_part and "system32" in str(file_path).lower():
            return Failure(
                ValidationError("Cannot upload files from system directory", field="file_path")
            )

    # Must be a regular file
    if not file_path.is_file():
        return Failure(
            ValidationError(
                "Path must be a regular file, not a directory or special file", field="file_path"
            )
        )

    return Success(
        UploadDocumentRequest(
            workspace_id=request.workspace_id,
            filename=filename,
            file_path=str(file_path),
        )
    )


def validate_show_document(
    request: ShowDocumentRequest,
) -> Result[ShowDocumentRequest, ValidationError]:
    """Validate show document input.

    Returns:
        Result with ShowDocumentRequest or ValidationError
    """
    # Use infrastructure utility for ID validation
    document_id_result = validate_positive_id(request.document_id, "document_id")
    if isinstance(document_id_result, Failure):
        return Failure(document_id_result.failure())

    workspace_id_result = validate_positive_id(request.workspace_id, "workspace_id")
    if isinstance(workspace_id_result, Failure):
        return Failure(workspace_id_result.failure())

    return Success(request)


def validate_delete_document(
    request: DeleteDocumentRequest,
) -> Result[DeleteDocumentRequest, ValidationError]:
    """Validate delete document input.

    Returns:
        Result with DeleteDocumentRequest or ValidationError
    """
    # Use infrastructure utility for ID validation
    document_id_result = validate_positive_id(request.document_id, "document_id")
    if isinstance(document_id_result, Failure):
        return Failure(document_id_result.failure())

    workspace_id_result = validate_positive_id(request.workspace_id, "workspace_id")
    if isinstance(workspace_id_result, Failure):
        return Failure(workspace_id_result.failure())

    return Success(request)
