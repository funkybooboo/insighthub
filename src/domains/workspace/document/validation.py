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


def _validate_path_security(file_path: Path) -> Result[None, ValidationError]:
    """Validate that file path is not in a sensitive system directory.

    Args:
        file_path: Resolved file path to check

    Returns:
        Success if path is safe, Failure with ValidationError if in sensitive location
    """
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
        if _is_in_sensitive_path(file_path, sensitive):
            return Failure(
                ValidationError(
                    f"Cannot upload files from system directory: {sensitive}",
                    field="file_path",
                )
            )

    if _is_windows_system_path(file_path):
        return Failure(
            ValidationError("Cannot upload files from system directory", field="file_path")
        )

    return Success(None)


def _is_in_sensitive_path(file_path: Path, sensitive: str) -> bool:
    """Check if file path is in a sensitive directory."""
    try:
        return file_path.is_relative_to(sensitive)
    except ValueError:
        return False


def _is_windows_system_path(file_path: Path) -> bool:
    """Check if file path is in Windows system directory."""
    if not file_path.parts or len(file_path.parts) == 0:
        return False

    first_part = str(file_path.parts[0]).lower()
    return "windows" in first_part and "system32" in str(file_path).lower()


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
    security_check = _validate_path_security(file_path)
    if isinstance(security_check, Failure):
        return security_check

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
