"""
Base classes and enums for document chunking
"""

from abc import ABC, abstractmethod
from enum import Enum

from src.rag.types import Chunk, Document, Metadata


class ChunkingStrategy(Enum):
    """Available chunking strategies."""

    CHARACTER = "character"
    SENTENCE = "sentence"
    WORD = "word"
    SEMANTIC = "semantic"  # Future: semantic-based chunking


class BaseChunker(ABC):
    """
    Abstract base class for document chunkers.
    All chunking implementations should inherit from this class.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize the chunker.

        Args:
            chunk_size: Target size of each chunk (meaning depends on strategy)
            chunk_overlap: Amount of overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk_text(self, text: str, metadata: Metadata | None = None) -> list[Chunk]:
        """
        Split text into chunks.

        Args:
            text: The text to chunk
            metadata: Optional metadata to attach to all chunks

        Returns:
            List of chunk dictionaries with 'text' and 'metadata' keys
        """
        pass

    def chunk_documents(
        self,
        documents: list[Document],
        text_key: str = "text",
        metadata_key: str = "metadata",
    ) -> list[Chunk]:
        """
        Chunk multiple documents.

        Args:
            documents: List of document dictionaries
            text_key: Key containing the text to chunk
            metadata_key: Key containing metadata

        Returns:
            List of chunks with text and metadata
        """
        all_chunks = []

        for doc_idx, doc in enumerate(documents):
            text_value = doc.get(text_key, "")
            text = text_value if isinstance(text_value, str) else ""
            metadata_value = doc.get(metadata_key, {})
            metadata = metadata_value if isinstance(metadata_value, dict) else {}

            # Add document index to metadata
            doc_metadata = {**metadata, "document_index": doc_idx}

            chunks = self.chunk_text(text, doc_metadata)
            all_chunks.extend(chunks)

        return all_chunks

    def _add_metadata_to_chunks(
        self, chunks: list[str], base_metadata: Metadata | None = None
    ) -> list[Chunk]:
        """
        Helper method to add metadata to chunk strings.

        Args:
            chunks: List of text chunks
            base_metadata: Base metadata to include in all chunks

        Returns:
            List of Chunk dictionaries with text and metadata
        """
        result: list[Chunk] = []
        metadata = base_metadata or {}

        for i, chunk_text in enumerate(chunks):
            chunk_metadata: Metadata = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "text": chunk_text,
            }
            result.append({"text": chunk_text, "metadata": chunk_metadata})

        return result

    @property
    @abstractmethod
    def strategy(self) -> ChunkingStrategy:
        """Return the chunking strategy used by this chunker."""
        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(chunk_size={self.chunk_size}, "
            f"overlap={self.chunk_overlap})"
        )
