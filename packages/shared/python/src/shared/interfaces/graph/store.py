"""Graph storage interface for Graph RAG."""

from abc import ABC, abstractmethod
from typing import Any

from shared.types import GraphEdge, GraphNode, RetrievalResult


class GraphStore(ABC):
    """
    Abstract graph database storage interface.

    Implementations may use:
    - Neo4j
    - PostgreSQL with graph extensions
    - ArangoDB
    - In-memory graph structures
    """

    @abstractmethod
    def add_node(self, node: GraphNode) -> None:
        """
        Add a node to the graph.

        Args:
            node: Graph node to add
        """
        raise NotImplementedError

    @abstractmethod
    def add_nodes(self, nodes: list[GraphNode]) -> None:
        """
        Batch add multiple nodes.

        Args:
            nodes: List of nodes to add
        """
        raise NotImplementedError

    @abstractmethod
    def add_edge(self, edge: GraphEdge) -> None:
        """
        Add an edge to the graph.

        Args:
            edge: Graph edge to add
        """
        raise NotImplementedError

    @abstractmethod
    def add_edges(self, edges: list[GraphEdge]) -> None:
        """
        Batch add multiple edges.

        Args:
            edges: List of edges to add
        """
        raise NotImplementedError

    @abstractmethod
    def get_node(self, node_id: str) -> GraphNode | None:
        """
        Retrieve a node by ID.

        Args:
            node_id: Node identifier

        Returns:
            GraphNode if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def get_neighbors(
        self, node_id: str, max_depth: int = 1, edge_filter: dict[str, Any] | None = None
    ) -> list[GraphNode]:
        """
        Get neighboring nodes.

        Args:
            node_id: Starting node ID
            max_depth: Maximum traversal depth
            edge_filter: Optional filter on edge properties

        Returns:
            List of neighboring nodes
        """
        raise NotImplementedError

    @abstractmethod
    def query_subgraph(
        self, node_ids: list[str], max_depth: int = 2
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        """
        Extract a subgraph around specified nodes.

        Args:
            node_ids: Starting node IDs
            max_depth: Maximum traversal depth

        Returns:
            Tuple of (nodes, edges) in the subgraph
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Remove all nodes and edges."""
        raise NotImplementedError

    @abstractmethod
    def count_nodes(self) -> int:
        """Return the number of nodes in the graph."""
        raise NotImplementedError

    @abstractmethod
    def count_edges(self) -> int:
        """Return the number of edges in the graph."""
        raise NotImplementedError
