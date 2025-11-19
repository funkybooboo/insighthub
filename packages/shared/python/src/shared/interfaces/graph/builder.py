"""Graph builder interface for Graph RAG."""

from abc import ABC, abstractmethod
from typing import Any

from shared.types import Document, GraphEdge, GraphNode


class GraphBuilder(ABC):
    """
    Constructs knowledge graphs from documents.

    Orchestrates the full pipeline:
    - Entity extraction
    - Relation extraction
    - Graph construction
    - Community detection / clustering
    """

    @abstractmethod
    def build_graph(self, documents: list[Document]) -> tuple[list[GraphNode], list[GraphEdge]]:
        """
        Build a knowledge graph from documents.

        Args:
            documents: List of documents to process

        Returns:
            Tuple of (nodes, edges) representing the constructed graph
        """
        raise NotImplementedError

    @abstractmethod
    def apply_clustering(
        self, nodes: list[GraphNode], edges: list[GraphEdge]
    ) -> dict[str, Any]:
        """
        Apply clustering algorithm (e.g., Leiden) to detect communities.

        Args:
            nodes: Graph nodes
            edges: Graph edges

        Returns:
            Dictionary with clustering results (community assignments, etc.)
        """
        raise NotImplementedError

    @abstractmethod
    def merge_graphs(
        self,
        graph1: tuple[list[GraphNode], list[GraphEdge]],
        graph2: tuple[list[GraphNode], list[GraphEdge]],
    ) -> tuple[list[GraphNode], list[GraphEdge]]:
        """
        Merge two graphs, resolving duplicate entities.

        Args:
            graph1: First graph (nodes, edges)
            graph2: Second graph (nodes, edges)

        Returns:
            Merged graph (nodes, edges)
        """
        raise NotImplementedError
