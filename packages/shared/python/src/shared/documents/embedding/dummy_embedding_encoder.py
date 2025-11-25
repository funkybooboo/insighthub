"""Dummy embedding encoder for testing."""

from collections.abc import Iterable

from shared.documents.embedding.vector_embedding_encoder import VectorEmbeddingEncoder
from shared.types.result import Ok


class DummyEmbeddingEncoder(VectorEmbeddingEncoder):
    """Dummy embedding encoder that returns fixed vectors for testing."""

    def __init__(self, dimension: int = 384) -> None:
        """Initialize with fixed dimension."""
        self._dimension = dimension

    def encode(self, texts: Iterable[str]) -> Ok[list[list[float]]]:
        """Return fixed vectors for each text."""
        return Ok([[0.1] * self._dimension for _ in texts])

    def encode_one(self, text: str) -> Ok[list[float]]:
        """Return fixed vector for single text."""
        return Ok([0.1] * self._dimension)

    def get_dimension(self) -> int:
        """Return the fixed dimension."""
        return self._dimension

    def get_model_name(self) -> str:
        """Return dummy model name."""
        return "dummy-embedding-model"
