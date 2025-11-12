"""Abstract embedding model interface."""

from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    """
    Abstract base class for embedding models.

    Embedding models convert text into dense vector representations.
    """

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        pass

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a single query string.

        Args:
            query: Query text to embed

        Returns:
            Embedding vector as list of floats
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimensionality of the embedding vectors.

        Returns:
            Vector dimension (e.g., 768, 1536)
        """
        pass
