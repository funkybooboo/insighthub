"""Abstract vector store interface."""

from abc import ABC, abstractmethod

from src.infrastructure.rag.types import SearchResult


class VectorStore(ABC):
    """
    Abstract base class for vector store implementations.

    Vector stores persist embeddings and enable similarity search.
    """

    @abstractmethod
    def add(
        self,
        vectors: list[list[float]],
        ids: list[str],
        metadata: list[dict[str, str | int | float | bool]] | None = None,
    ) -> None:
        """
        Add vectors to the store.

        Args:
            vectors: List of embedding vectors
            ids: Unique identifiers for each vector
            metadata: Optional metadata for each vector
        """
        pass

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filter_metadata: dict[str, str | int | float | bool] | None = None,
    ) -> list[SearchResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: The query embedding
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of SearchResults with id, score, and metadata
        """
        pass

    @abstractmethod
    def delete(self, ids: list[str]) -> None:
        """
        Delete vectors by ID.

        Args:
            ids: List of vector IDs to delete
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all vectors from the store."""
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Get the number of vectors in the store.

        Returns:
            Total vector count
        """
        pass
