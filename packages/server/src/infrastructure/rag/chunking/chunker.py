"""
Refined abstract Chunker interface for document chunking in RAG systems.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from src.infrastructure.rag.types import Chunk, ChunkerConfig, PrimitiveValue


class Chunker(ABC):
    """
    Abstract base class for document chunking strategies.

    Chunkers split documents into smaller pieces for embedding and retrieval.
    """

    @abstractmethod
    def chunk(self, text: str, metadata: dict[str, PrimitiveValue] | None = None) -> list[Chunk]:
        """
        Split text into chunks with metadata.

        Args:
            text: The document text to chunk.
            metadata: Optional metadata to attach to all chunks.

        Returns:
            List of chunks with text, optional ID, and metadata.
        """
        ...

    @abstractmethod
    def chunk_generator(
        self, text: str, metadata: dict[str, PrimitiveValue] | None = None
    ) -> Iterator[Chunk]:
        """
        Generator version of chunking for large documents.

        Args:
            text: The document text to chunk.
            metadata: Optional metadata to attach to all chunks.

        Yields:
            Chunks one by one to save memory.
        """
        ...

    @abstractmethod
    def get_config(self) -> ChunkerConfig:
        """
        Get chunker configuration.

        Returns:
            ChunkerConfig with strategy, chunk_size, overlap, and optional extra options.
        """
        ...
