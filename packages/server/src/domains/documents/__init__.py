"""Documents domain - handles document uploads and management."""

from shared.models import Document
from shared.repositories import DocumentRepository, SqlDocumentRepository

from . import commands
from .routes import documents_bp
from .service import DocumentService, DocumentUploadResult

__all__ = [
    "Document",
    "DocumentRepository",
    "SqlDocumentRepository",
    "DocumentService",
    "DocumentUploadResult",
    "documents_bp",
    "commands",
]
