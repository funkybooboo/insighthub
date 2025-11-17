"""
Abstract vector store interface.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from typing import Literal

from src.infrastructure.rag.types import PrimitiveValue, SearchResult


class VectorStore(ABC):
    """
    Abstract base class for vector store implementations.

    A vector store handles:
    - Persistent storage of embedding vectors
    - Efficient similarity search
    - Optional metadata filtering
    """

    @abstractmethod
    def add(
        self,
        vectors: Sequence[Sequence[float]],
        ids: Sequence[str],
        metadata: Sequence[dict[str, PrimitiveValue]] | None = None,
    ) -> Sequence[str]:
        """
        Add vectors to the database.

        Returns the stored IDs (may be modified/generated).
        """
        ...

    @abstractmethod
    def search(
        self,
        query_vector: Sequence[float],
        top_k: int = 5,
        filter_metadata: dict[str, PrimitiveValue] | None = None,
        metric: Literal["cosine", "euclidean", "dot"] = "cosine",
    ) -> list[SearchResult]:
        """Perform similarity search."""
        ...

    @abstractmethod
    def delete(self, ids: Iterable[str]) -> None:
        """Delete vectors by ID. Unknown IDs ignored."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all vectors + metadata."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the number of stored vectors."""
        ...
