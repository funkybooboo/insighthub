"""Document repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.models import Document


class DocumentRepository(ABC):
    """Interface for Document repository operations."""

    @abstractmethod
    def create(
        self,
        user_id: int,
        filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        content_hash: str,
        chunk_count: Optional[int] = None,
        rag_collection: Optional[str] = None,
    ) -> Document:
        """Create a new document."""
        pass

    @abstractmethod
    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get documents by user ID with pagination."""
        pass

    @abstractmethod
    def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        pass

    @abstractmethod
    def update(self, document_id: int, **kwargs: str | int) -> Optional[Document]:
        """Update document fields."""
        pass

    @abstractmethod
    def delete(self, document_id: int) -> bool:
        """Delete document by ID."""
        pass
