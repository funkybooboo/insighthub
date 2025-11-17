"""
Abstract graph store interface.
"""

from abc import ABC, abstractmethod

from src.infrastructure.rag.types import MetadataValue, SearchResult


class GraphStore(ABC):
    """
    Abstract base class for graph database implementations.

    Graph stores persist nodes and edges and support traversal + search.
    """

    @abstractmethod
    def add_nodes(
        self,
        ids: list[str],
        labels: list[list[str]] | None = None,
        properties: list[dict[str, MetadataValue]] | None = None,
    ) -> None:
        """
        Add nodes to the graph.

        All lists must have equal length.
        """
        ...

    @abstractmethod
    def delete_nodes(self, ids: list[str]) -> None:
        """
        Delete nodes by ID. Unknown IDs should be ignored.
        """
        ...

    @abstractmethod
    def add_edges(
        self,
        source_ids: list[str],
        target_ids: list[str],
        rel_types: list[str],
        properties: list[dict[str, MetadataValue]] | None = None,
    ) -> None:
        """
        Add edges between nodes. Parallel lists must match length.
        """
        ...

    @abstractmethod
    def delete_edges(
        self,
        source_ids: list[str],
        target_ids: list[str],
        rel_types: list[str],
    ) -> None:
        """Delete edges by (source, target, type) triple."""
        ...

    @abstractmethod
    def search(
        self,
        start_node_id: str | None = None,
        query: str | None = None,
        limit: int = 10,
        filter_properties: dict[str, MetadataValue] | None = None,
    ) -> list[SearchResult]:
        """
        Search the graph via traversal or query text.

        Implementations must define precedence if both `start_node_id`
        and `query` are provided.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove all nodes + edges."""
        ...

    @abstractmethod
    def count_nodes(self) -> int:
        """Return total number of nodes."""
        ...

    @abstractmethod
    def count_edges(self) -> int:
        """Return total number of edges."""
        ...
