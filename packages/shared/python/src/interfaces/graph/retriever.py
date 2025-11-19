"""Graph retrieval interface for Graph RAG."""

from abc import ABC, abstractmethod
from typing import Any

from shared.types import RetrievalResult


class GraphRetriever(ABC):
    """
    High-level interface for graph-based retrieval.

    Combines graph traversal, community detection, and relevance scoring
    to retrieve contextually relevant subgraphs.
    """

    @abstractmethod
    def retrieve(
        self, query: str, k: int = 10, filters: dict[str, Any] | None = None
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant graph nodes/subgraphs for a query.

        Args:
            query: User query text
            k: Number of results to retrieve
            filters: Optional filters on node/edge properties

        Returns:
            List of RetrievalResult objects with graph context
        """
        raise NotImplementedError

    @abstractmethod
    def retrieve_by_entity(
        self, entity_name: str, k: int = 10
    ) -> list[RetrievalResult]:
        """
        Retrieve context around a specific entity.

        Args:
            entity_name: Entity name to search for
            k: Number of results to retrieve

        Returns:
            List of RetrievalResult objects
        """
        raise NotImplementedError

    @abstractmethod
    def retrieve_community(
        self, query: str, k: int = 3
    ) -> list[RetrievalResult]:
        """
        Retrieve entire communities relevant to the query.

        Args:
            query: User query text
            k: Number of communities to retrieve

        Returns:
            List of RetrievalResult objects representing communities
        """
        raise NotImplementedError
