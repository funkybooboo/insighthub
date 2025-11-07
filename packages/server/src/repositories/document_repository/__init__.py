"""Document repository module."""

from .document_repository import DocumentRepository
from .sql_document_repository import SqlDocumentRepository

__all__ = ["DocumentRepository", "SqlDocumentRepository"]
