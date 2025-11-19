"""Chunker interface for Vector RAG."""

from abc import ABC, abstractmethod

from shared.types import Chunk, Document


class Chunker(ABC):
    """
    Splits Document content into smaller, semantically meaningful chunks.

    Implementations can use different strategies:
    - Sentence-based chunking
    - Character-based with overlap
    - Semantic chunking using embeddings
    """

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """
        Chunk the document into a list of Chunk objects.

        Args:
            document: Document to split into chunks

        Returns:
            List of Chunk objects
        """
        raise NotImplementedError


class MetadataEnricher(ABC):
    """
    Enriches chunks with additional metadata.

    Examples: token count, language detection, content type, hash.
    """

    @abstractmethod
    def enrich(self, chunk: Chunk) -> Chunk:
        """
        Add or modify metadata for a chunk.

        Args:
            chunk: Chunk to enrich

        Returns:
            Enriched Chunk object
        """
        raise NotImplementedError
