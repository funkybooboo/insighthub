"""Documents repository module."""

from .document_repository import DocumentRepository
from .factory import create_document_repository
from .in_memory_document_repository import InMemoryDocumentRepository

__all__ = ["DocumentRepository", "InMemoryDocumentRepository", "create_document_repository"]
