"""Document repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.infrastructure.models import Document


class DocumentRepository(ABC):
    """Interface for Document repository operations."""

    @abstractmethod
    def create(
        self,
        workspace_id: int,
        filename: str,
        file_size: int,
        mime_type: str,
        chunk_count: int = 0,
        processing_status: str = "processing",
        processing_error: str | None = None,
        file_path: str | None = None,
        content_hash: str | None = None,
        rag_collection: str | None = None,
        parsed_text: str | None = None,
    ) -> Document:
        """Create a new document."""
        pass

    @abstractmethod
    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID."""
        pass

    @abstractmethod
    def get_by_content_hash(self, content_hash: str) -> Optional[Document]:
        """Get document by content hash."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get documents by users ID with pagination."""
        pass

    @abstractmethod
    def get_by_workspace(
        self, workspace_id: int, limit: int = 50, offset: int = 0
    ) -> list[Document]:
        """Get documents for a workspace."""
        pass

    @abstractmethod
    def update(self, document_id: int, **kwargs) -> Optional[Document]:
        """Update document fields."""
        pass

    @abstractmethod
    def update_status(
        self,
        document_id: int,
        status: str,
        error: str | None = None,
        chunk_count: int | None = None,
    ) -> bool:
        """Update document processing status."""
        pass

    @abstractmethod
    def count_by_workspace(self, workspace_id: int, status_filter: str | None = None) -> int:
        """Count documents in workspace with optional status filter."""
        pass

    @abstractmethod
    def delete(self, document_id: int) -> bool:
        """Delete a document."""
        pass
