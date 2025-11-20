"""Vector retrieval interface for high-level vector search operations."""

from abc import ABC, abstractmethod
from typing import Any, List

from shared.types.retrieval import RetrievalResult


class VectorRetriever(ABC):
    """
    High-level interface for retrieving vectors from a vector store.
    
    This provides a more convenient API than the raw VectorIndex,
    handling query processing and result formatting.
    """

    @abstractmethod
    def retrieve(self, query_vector: List[float], k: int = 10, filters: dict[str, Any] | None = None) -> List[RetrievalResult]:
        """
        Retrieve top-k most similar vectors to the query vector.

        Args:
            query_vector: Query embedding vector
            k: Number of results to retrieve
            filters: Optional metadata filters

        Returns:
            List[RetrievalResult]: Retrieved vectors with scores

        Raises:
            RetrievalError: If retrieval fails
        """
        pass

    @abstractmethod
    def retrieve_by_ids(self, ids: List[str]) -> List[RetrievalResult]:
        """
        Retrieve vectors by their IDs.

        Args:
            ids: List of vector IDs to retrieve

        Returns:
            List[RetrievalResult]: Retrieved vectors

        Raises:
            RetrievalError: If retrieval fails
        """
        pass