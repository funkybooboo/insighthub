"""Dummy Embedding provider implementation for testing."""

from collections.abc import Iterable

from returns.result import Result, Success

from src.infrastructure.rag.steps.vector_rag.embedding.vector_embedder import (
    EmbeddingError,
    VectorEmbeddingEncoder,
)


class DummyEmbeddingProvider(VectorEmbeddingEncoder):
    """
    Dummy Embedding provider for testing purposes.
    """

    def __init__(self, dimension: int = 4):
        self._dimension = dimension

    def encode(self, texts: Iterable[str]) -> Result[list[list[float]], EmbeddingError]:
        """
        Encode a list of texts into dummy embeddings.

        Args:
            texts: An iterable of strings to encode.

        Returns:
            Result containing a list of lists of floats, where each inner list is a dummy embedding.
        """
        return Success([[0.1] * self._dimension for _ in texts])

    def encode_one(self, text: str) -> Result[list[float], EmbeddingError]:
        """
        Encode a single text into a dummy vector.

        Args:
            text: Text string to encode

        Returns:
            Result containing a dummy vector embedding.
        """
        result = self.encode([text])
        return result.map(lambda embeddings: embeddings[0])

    def get_dimension(self) -> int:
        """
        Get the dimension of the embeddings produced by this provider.
        """
        return self._dimension

    def get_model_name(self) -> str:
        """
        Get the name of the embedding model.
        """
        return "dummy"
