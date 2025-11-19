"""
Abstract embedding model interface for RAG systems using strict type definitions.
"""

from abc import ABC, abstractmethod

from src.infrastructure.rag.types import MetadataValue


class EmbeddingModel(ABC):
    """
    Abstract base class for embedding models.

    Embedding models convert text into dense vector representations.
    """

    @abstractmethod
    def embed(
        self, texts: list[str], metadata: list[dict[str, MetadataValue]] | None = None
    ) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed.
            metadata: Optional list of metadata dictionaries associated with each text.

        Returns:
            List of embedding vectors, each as a list of floats.
        """
        ...

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a single query string.

        Args:
            query: Query text to embed.

        Returns:
            Embedding vector as a list of floats.
        """
        ...

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimensionality of the embedding vectors.

        Returns:
            Vector dimension (e.g., 768, 1536).
        """
        ...
