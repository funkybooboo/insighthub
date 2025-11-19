"""Vector retriever interface for Vector RAG."""

from abc import ABC, abstractmethod
from typing import Any

from shared.types import RetrievalResult


class VectorRetriever(ABC):
    """
    High-level interface for retrieving top-k vectors from a VectorIndex.

    This wraps VectorIndex with additional logic like filtering, reranking hints, etc.
    """

    @abstractmethod
    def retrieve(
        self, query_vector: list[float], k: int = 10, filters: dict[str, Any] | None = None
    ) -> list[RetrievalResult]:
        """
        Retrieve top-k relevant chunks from the vector store.

        Args:
            query_vector: Query embedding vector
            k: Number of results to retrieve
            filters: Optional metadata filters

        Returns:
            List of RetrievalResult objects
        """
        raise NotImplementedError
