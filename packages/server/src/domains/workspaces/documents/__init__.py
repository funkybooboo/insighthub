"""Workspace documents domain."""

from shared.models import Document
from shared.repositories import DocumentRepository, SqlDocumentRepository

from .routes import documents_bp
from .service import DocumentService, DocumentUploadResult
from .status import DocumentStatusData, broadcast_document_status, emit_wikipedia_fetch_status

__all__ = [
    "Document",
    "DocumentRepository",
    "SqlDocumentRepository",
    "DocumentService",
    "DocumentUploadResult",
    "documents_bp",
    "DocumentStatusData",
    "broadcast_document_status",
    "emit_wikipedia_fetch_status",
]
