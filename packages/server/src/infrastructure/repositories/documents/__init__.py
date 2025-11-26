"""Documents repository module."""

from .document_repository import DocumentRepository
from .in_memory_document_repository import InMemoryDocumentRepository
from .factory import create_document_repository

__all__ = ["DocumentRepository", "InMemoryDocumentRepository", "create_document_repository"]