"""Abstract chunker interface for document chunking strategies."""

from abc import ABC, abstractmethod

from infrastructure.rag.types import Chunk, ChunkerConfig


class Chunker(ABC):
    """
    Abstract base class for document chunking strategies.

    Chunkers split documents into smaller pieces for embedding and retrieval.
    """

    @abstractmethod
    def chunk(
        self, text: str, metadata: dict[str, str | int | float | bool] | None = None
    ) -> list[Chunk]:
        """
        Split text into chunks with metadata.

        Args:
            text: The document text to chunk
            metadata: Optional metadata to attach to all chunks

        Returns:
            List of chunks with text and metadata
        """
        pass

    @abstractmethod
    def get_config(self) -> ChunkerConfig:
        """
        Get chunker configuration.

        Returns:
            ChunkerConfig with strategy, chunk_size, and overlap
        """
        pass
