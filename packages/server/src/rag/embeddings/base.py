"""
Simple Embedding Interface
Minimal wrapper around embedding models
"""

from abc import ABC, abstractmethod

from src.rag.types import Vector


class EmbeddingModel(ABC):
    """
    Abstract base class for embedding models.
    """

    @abstractmethod
    def embed(self, texts: str | list[str]) -> list[Vector]:
        """
        Generate embeddings for text(s).

        Args:
            texts: Single text or list of texts

        Returns:
            List of embedding vectors
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimensionality of the embeddings.

        Returns:
            Embedding dimension
        """
        pass
