"""Graph store interface for storing and retrieving graph data."""

from abc import ABC, abstractmethod
from typing import List

from shared.types.graph import Graph, Node, Relationship


class GraphStore(ABC):
    """
    Interface for graph database operations.

    Implementations should support different graph databases:
    - Neo4j
    - In-memory (for testing)
    """

    @abstractmethod
    def add_graph(self, graph: Graph) -> None:
        """
        Add a graph to the store.

        Args:
            graph: The graph to add.

        Raises:
            GraphStoreError: If adding the graph fails.
        """
        pass

    @abstractmethod
    def get_neighbors(self, node: Node) -> List[Node]:
        """
        Get the neighbors of a node.

        Args:
            node: The node to get the neighbors of.

        Returns:
            A list of neighboring nodes.

        Raises:
            GraphStoreError: If getting the neighbors fails.
        """
        pass

    @abstractmethod
    def get_all_nodes(self) -> List[Node]:
        """
        Get all nodes in the graph.

        Returns:
            A list of all nodes.

        Raises:
            GraphStoreError: If getting all nodes fails.
        """
        pass

    @abstractmethod
    def get_all_relationships(self) -> List[Relationship]:
        """
        Get all relationships in the graph.

        Returns:
            A list of all relationships.

        Raises:
            GraphStoreError: If getting all relationships fails.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear the graph store.

        Raises:
            GraphStoreError: If clearing fails.
        """
        pass
