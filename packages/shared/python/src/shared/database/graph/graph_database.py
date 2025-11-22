"""Graph database interface for knowledge graph operations."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from shared.types.common import PropertiesDict
from shared.types.graph import GraphEdge, GraphNode

if TYPE_CHECKING:
    from shared.types.common import PayloadDict


class GraphDatabase(ABC):
    """
    Abstract interface for graph database operations.

    Implementations may use Neo4j, ArangoDB, or other graph databases.
    Provides CRUD operations for nodes and edges, plus graph queries.

    Example:
        db = Neo4jGraphDatabase(uri="bolt://localhost:7687", ...)
        node = GraphNode(id="person_1", labels=["Person"], properties={"name": "Alice"})
        db.create_node(node)
        neighbors = db.get_neighbors("person_1", relationship_type="KNOWS")
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to the graph database.

        Raises:
            ConnectionError: If connection fails
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the graph database."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if database connection is active.

        Returns:
            True if connected, False otherwise
        """
        pass

    # Node operations

    @abstractmethod
    def create_node(self, node: GraphNode) -> GraphNode:
        """
        Create a new node in the graph.

        Args:
            node: Node to create

        Returns:
            Created node with any database-generated fields

        Raises:
            ValueError: If node with same ID already exists
        """
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> GraphNode | None:
        """
        Retrieve a node by ID.

        Args:
            node_id: Unique node identifier

        Returns:
            Node if found, None otherwise
        """
        pass

    @abstractmethod
    def update_node(self, node: GraphNode) -> GraphNode:
        """
        Update an existing node.

        Args:
            node: Node with updated properties

        Returns:
            Updated node

        Raises:
            ValueError: If node does not exist
        """
        pass

    @abstractmethod
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and its relationships.

        Args:
            node_id: ID of node to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def node_exists(self, node_id: str) -> bool:
        """
        Check if a node exists.

        Args:
            node_id: Node identifier

        Returns:
            True if exists, False otherwise
        """
        pass

    # Edge operations

    @abstractmethod
    def create_edge(self, edge: GraphEdge) -> GraphEdge:
        """
        Create an edge between two nodes.

        Args:
            edge: Edge to create

        Returns:
            Created edge with any database-generated fields

        Raises:
            ValueError: If source or target node does not exist
        """
        pass

    @abstractmethod
    def get_edge(self, edge_id: str) -> GraphEdge | None:
        """
        Retrieve an edge by ID.

        Args:
            edge_id: Unique edge identifier

        Returns:
            Edge if found, None otherwise
        """
        pass

    @abstractmethod
    def delete_edge(self, edge_id: str) -> bool:
        """
        Delete an edge.

        Args:
            edge_id: ID of edge to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def get_edges_between(
        self, source_id: str, target_id: str, relationship_type: str | None = None
    ) -> list[GraphEdge]:
        """
        Get edges between two nodes.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            relationship_type: Filter by relationship type (optional)

        Returns:
            List of matching edges
        """
        pass

    # Query operations

    @abstractmethod
    def get_neighbors(
        self,
        node_id: str,
        relationship_type: str | None = None,
        direction: str = "both",
    ) -> list[GraphNode]:
        """
        Get neighboring nodes.

        Args:
            node_id: Starting node ID
            relationship_type: Filter by relationship type (optional)
            direction: "in", "out", or "both"

        Returns:
            List of neighboring nodes
        """
        pass

    @abstractmethod
    def get_node_edges(self, node_id: str, direction: str = "both") -> list[GraphEdge]:
        """
        Get all edges connected to a node.

        Args:
            node_id: Node ID
            direction: "in", "out", or "both"

        Returns:
            List of connected edges
        """
        pass

    @abstractmethod
    def find_nodes_by_label(
        self, label: str, properties: PropertiesDict | None = None
    ) -> list[GraphNode]:
        """
        Find nodes by label and optional property filters.

        Args:
            label: Node label to search for
            properties: Property filters (optional)

        Returns:
            List of matching nodes
        """
        pass

    @abstractmethod
    def execute_query(
        self, query: str, parameters: PropertiesDict | None = None
    ) -> list["PayloadDict"]:
        """
        Execute a raw query in the database's native query language.

        Args:
            query: Query string (Cypher for Neo4j, AQL for ArangoDB, etc.)
            parameters: Query parameters

        Returns:
            Query results as list of dictionaries
        """
        pass

    # Bulk operations

    @abstractmethod
    def create_nodes_batch(self, nodes: list[GraphNode]) -> list[GraphNode]:
        """
        Create multiple nodes in a single operation.

        Args:
            nodes: List of nodes to create

        Returns:
            List of created nodes
        """
        pass

    @abstractmethod
    def create_edges_batch(self, edges: list[GraphEdge]) -> list[GraphEdge]:
        """
        Create multiple edges in a single operation.

        Args:
            edges: List of edges to create

        Returns:
            List of created edges
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Delete all nodes and edges from the database."""
        pass

    # Statistics

    @abstractmethod
    def get_node_count(self) -> int:
        """Get total number of nodes."""
        pass

    @abstractmethod
    def get_edge_count(self) -> int:
        """Get total number of edges."""
        pass
