"""Embedding encoder interface for Vector RAG."""

from abc import ABC, abstractmethod
from collections.abc import Iterable


class EmbeddingEncoder(ABC):
    """
    Encodes text into vector representations for similarity search.

    Implementations may call:
    - Remote APIs (OpenAI, Cohere)
    - Local models (Sentence Transformers, Ollama)
    """

    @abstractmethod
    def encode(self, texts: Iterable[str]) -> list[list[float]]:
        """
        Batch-encode multiple strings into vectors.

        Args:
            texts: Iterable of strings to encode

        Returns:
            List of embedding vectors (one per text)
        """
        raise NotImplementedError

    @abstractmethod
    def encode_one(self, text: str) -> list[float]:
        """
        Encode a single string into a vector.

        Args:
            text: Input string

        Returns:
            Vector representation of the text
        """
        raise NotImplementedError

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimensionality of the embedding vectors.

        Returns:
            Vector dimension (e.g., 768, 1536)
        """
        raise NotImplementedError
