"""Document domain exceptions."""

from src.infrastructure.errors.base import DomainException, NotFoundError, ValidationError


class DocumentNotFoundError(NotFoundError):
    """Raised when a document is not found."""

    def __init__(self, document_id: int):
        """
        Initialize document not found error.

        Args:
            document_id: The document ID that was not found
        """
        super().__init__("Document", document_id)


class InvalidFileTypeError(ValidationError):
    """Raised when an uploaded file has an invalid type."""

    def __init__(self, filename: str, allowed_extensions: set[str]):
        """
        Initialize invalid file type error.

        Args:
            filename: The filename that was rejected
            allowed_extensions: Set of allowed file extensions
        """
        extensions_str = ", ".join(sorted(allowed_extensions)).upper()
        message = f"Invalid file type for '{filename}'. Only {extensions_str} files are allowed"
        super().__init__(message)
        self.filename = filename
        self.allowed_extensions = allowed_extensions


class DocumentUploadError(DomainException):
    """Raised when document upload fails."""

    def __init__(self, message: str):
        """
        Initialize document upload error.

        Args:
            message: Description of upload failure
        """
        super().__init__(message, status_code=500)


class DocumentProcessingError(DomainException):
    """Raised when document processing fails (e.g., text extraction)."""

    def __init__(self, filename: str, reason: str):
        """
        Initialize document processing error.

        Args:
            filename: The filename being processed
            reason: Reason for processing failure
        """
        message = f"Failed to process document '{filename}': {reason}"
        super().__init__(message, status_code=422)
        self.filename = filename
        self.reason = reason
