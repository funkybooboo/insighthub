"""
Base Vector Store Interface
"""

from abc import ABC, abstractmethod

from src.rag.types import Metadata, SearchResult, Stats, Vector


class VectorStore(ABC):
    """
    Abstract base class for vector stores.
    """

    @abstractmethod
    def add(self, vectors: list[Vector], ids: list[str], metadata: list[Metadata]) -> None:
        """
        Add vectors to the store.

        Args:
            vectors: List of embedding vectors
            ids: List of unique IDs for each vector
            metadata: List of metadata dictionaries
        """
        pass

    @abstractmethod
    def search(
        self, query_vector: Vector, top_k: int = 5, filter: Metadata | None = None
    ) -> list[SearchResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: The query embedding
            top_k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of matches with id, score, and metadata
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """Delete all vectors from the store."""
        pass

    @abstractmethod
    def get_stats(self) -> Stats:
        """Get store statistics."""
        pass
