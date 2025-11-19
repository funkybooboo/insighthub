"""Vector storage interface for Vector RAG."""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from shared.types import RetrievalResult


class VectorIndex(ABC):
    """
    Abstract vector storage interface.

    Responsibilities:
    - Upsert vector + metadata
    - Similarity search
    - Delete vectors by ID
    """

    @abstractmethod
    def upsert(self, id: str, vector: list[float], metadata: dict[str, Any]) -> None:
        """
        Insert or update a vector in the store.

        Args:
            id: Unique identifier for the vector
            vector: Vector embedding
            metadata: Metadata associated with the vector
        """
        raise NotImplementedError

    @abstractmethod
    def upsert_many(
        self, items: Iterable[tuple[str, list[float], dict[str, Any]]]
    ) -> None:
        """
        Batch upsert multiple vectors.

        Args:
            items: Iterable of (id, vector, metadata) tuples
        """
        raise NotImplementedError

    @abstractmethod
    def similarity_search(
        self, vector: list[float], top_k: int = 10, filters: dict[str, Any] | None = None
    ) -> list[RetrievalResult]:
        """
        Retrieve the top-k most similar vectors.

        Args:
            vector: Query vector
            top_k: Number of results to retrieve
            filters: Optional metadata filters

        Returns:
            List of RetrievalResult objects
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: str) -> None:
        """
        Delete a vector by its ID.

        Args:
            id: Vector identifier to delete
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Remove all vectors and metadata."""
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Return the number of stored vectors."""
        raise NotImplementedError
