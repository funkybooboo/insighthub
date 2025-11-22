"""Document repository interface."""

from abc import ABC, abstractmethod

from shared.models.document import Document
from shared.types.option import Option


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
        chunk_count: int | None = None,
        rag_collection: str | None = None,
    ) -> Document:
        """
        Create a new document.

        Args:
            user_id: Owner user ID
            filename: Original filename
            file_path: Storage path
            file_size: File size in bytes
            mime_type: MIME type
            content_hash: SHA-256 hash of content
            chunk_count: Number of chunks (optional)
            rag_collection: RAG collection name (optional)

        Returns:
            Created document
        """
        pass

    @abstractmethod
    def get_by_id(self, document_id: int) -> Option[Document]:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Some(Document) if found, Nothing() if not found
        """
        pass

    @abstractmethod
    def get_by_user(self, user_id: int, skip: int, limit: int) -> list[Document]:
        """
        Get documents by user ID with pagination.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of documents
        """
        pass

    @abstractmethod
    def get_by_content_hash(self, content_hash: str) -> Option[Document]:
        """
        Get document by content hash.

        Args:
            content_hash: SHA-256 hash

        Returns:
            Some(Document) if found, Nothing() if not found
        """
        pass

    @abstractmethod
    def update(self, document_id: int, **kwargs: str | int) -> Option[Document]:
        """
        Update document fields.

        Args:
            document_id: Document ID
            **kwargs: Fields to update

        Returns:
            Some(Document) if found and updated, Nothing() if not found
        """
        pass

    @abstractmethod
    def delete(self, document_id: int) -> bool:
        """
        Delete document by ID.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        pass
