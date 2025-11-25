"""Chunk repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from shared.models.chunk import Chunk


class ChunkRepository(ABC):
    """Interface for Chunk repository operations."""

    @abstractmethod
    def get_by_id(self, chunk_id: UUID) -> Optional[Chunk]:
        """
        Get chunk by ID.

        Args:
            chunk_id: Chunk UUID

        Returns:
            Chunk if found, None if not found
        """
        pass

    @abstractmethod
    def get_by_document(self, document_id: int) -> List[Chunk]:
        """
        Get all chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            List of chunks ordered by chunk_index
        """
        pass

    @abstractmethod
    def get_by_document_and_index(self, document_id: int, chunk_index: int) -> Optional[Chunk]:
        """
        Get chunk by document ID and chunk index.

        Args:
            document_id: Document ID
            chunk_index: Chunk index within the document

        Returns:
            Chunk if found, None if not found
        """
        pass

    @abstractmethod
    def create(
        self,
        document_id: int,
        chunk_index: int,
        chunk_text: str,
        embedding: Optional[List[float]] = None,
        metadata: Optional[dict] = None,
    ) -> Chunk:
        """
        Create a new chunk.

        Args:
            document_id: Document ID
            chunk_index: Index of this chunk within the document
            chunk_text: The chunk text content
            embedding: Optional vector embedding
            metadata: Optional metadata dictionary

        Returns:
            Created chunk
        """
        pass

    @abstractmethod
    def update_embedding(self, chunk_id: UUID, embedding: List[float]) -> Optional[Chunk]:
        """
        Update chunk embedding.

        Args:
            chunk_id: Chunk UUID
            embedding: Vector embedding

        Returns:
            Updated chunk if found, None if not found
        """
        pass

    @abstractmethod
    def delete_by_document(self, document_id: int) -> int:
        """
        Delete all chunks for a document.

        Args:
            document_id: Document ID

        Returns:
            Number of chunks deleted
        """
        pass