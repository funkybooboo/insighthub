"""Document repository module."""

from shared.repositories.document.document_repository import DocumentRepository
from shared.repositories.document.factory import create_document_repository
from shared.repositories.document.sql_document_repository import SqlDocumentRepository

__all__ = [
    "DocumentRepository",
    "SqlDocumentRepository",
    "create_document_repository",
]
