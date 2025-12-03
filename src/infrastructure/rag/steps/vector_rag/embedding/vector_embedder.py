"""Embedding generation interfaces for converting text to vector representations."""

from abc import ABC, abstractmethod
from collections.abc import Iterable

from returns.result import Result

from src.infrastructure.types.common import HealthStatus


class EmbeddingError(Exception):
    """Error type for embedding failures."""

    def __init__(self, message: str, code: str = "EMBEDDING_ERROR") -> None:
        """
        Initialize embedding error.

        Args:
            message: Error message
            code: Error code for categorization
        """
        self.message = message
        self.code = code

    def __str__(self) -> str:
        """Return string representation."""
        return f"[{self.code}] {self.message}"


class VectorEmbeddingEncoder(ABC):
    """
    Interface for generating vector embeddings from text.

    Implementations should support different embedding models:
    - Local models (Ollama, Sentence Transformers)
    - API-based models (OpenAI, Claude)
    - Custom models
    """

    @abstractmethod
    def encode(self, texts: Iterable[str]) -> Result[list[list[float]], EmbeddingError]:
        """
        Encode multiple texts into vectors.

        Args:
            texts: Iterable of text strings to encode

        Returns:
            Result containing list of vector embeddings, or EmbeddingError on failure
        """
        pass

    @abstractmethod
    def encode_one(self, text: str) -> Result[list[float], EmbeddingError]:
        """
        Encode a single text into a vector.

        Args:
            text: Text string to encode

        Returns:
            Result containing vector embedding, or EmbeddingError on failure
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            Dimension of the vectors
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the embedding model.

        Returns:
            Model name
        """
        pass

    def health_check(self) -> HealthStatus:
        """
        Check if the embedding service is available.

        Returns:
            Health status dictionary
        """
        return {"status": "healthy", "provider": "unknown"}
