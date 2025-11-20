"""Text chunking interfaces for splitting documents into semantic segments."""

from abc import ABC, abstractmethod
from typing import Any

from shared.types.document import Document, Chunk


class Chunker(ABC):
    """
    Interface for splitting documents into smaller, meaningful chunks.
    
    Implementations should use different strategies:
    - Fixed-size character chunking
    - Sentence-based chunking  
    - Paragraph-based chunking
    - Semantic chunking using embeddings
    """

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """
        Split a document into chunks.

        Args:
            document: The document to chunk

        Returns:
            list[Chunk]: List of text chunks with metadata

        Raises:
            ChunkingError: If chunking fails
        """
        pass

    @abstractmethod
    def estimate_chunk_count(self, document: Document) -> int:
        """
        Estimate the number of chunks that will be created.

        Args:
            document: The document to analyze

        Returns:
            int: Estimated number of chunks
        """
        pass


class MetadataEnricher(ABC):
    """
    Interface for enriching chunks with additional metadata.
    
    Implementations can add:
    - Token counts
    - Language detection
    - Position information
    - Semantic metadata
    - Provenance information
    """

    @abstractmethod
    def enrich(self, chunk: Chunk) -> Chunk:
        """
        Enrich a chunk with additional metadata.

        Args:
            chunk: The chunk to enrich

        Returns:
            Chunk: Enriched chunk with additional metadata

        Raises:
            EnrichmentError: If enrichment fails
        """
        pass