"""Embedding generation interfaces for converting text to vector representations."""

from abc import ABC, abstractmethod
from typing import Any, Iterable


class EmbeddingEncoder(ABC):
    """
    Interface for generating vector embeddings from text.
    
    Implementations should support different embedding models:
    - Local models (Ollama, Sentence Transformers)
    - API-based models (OpenAI, Claude)
    - Custom models
    """

    @abstractmethod
    def encode(self, texts: Iterable[str]) -> list[list[float]]:
        """
        Encode multiple texts into vectors.

        Args:
            texts: Iterable of text strings to encode

        Returns:
            list[list[float]]: List of vector embeddings

        Raises:
            EmbeddingError: If encoding fails
        """
        pass

    @abstractmethod
    def encode_one(self, text: str) -> list[float]:
        """
        Encode a single text into a vector.

        Args:
            text: Text string to encode

        Returns:
            list[float]: Vector embedding

        Raises:
            EmbeddingError: If encoding fails
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.

        Returns:
            int: Dimension of the vectors
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the embedding model.

        Returns:
            str: Model name
        """
        pass