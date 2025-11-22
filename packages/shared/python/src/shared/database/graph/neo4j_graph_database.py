"""Neo4j graph database implementation."""

from types import TracebackType
from typing import Any

from neo4j import Driver
from neo4j import GraphDatabase as Neo4jDriver
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from shared.logger import create_logger
from shared.types.graph import GraphEdge, GraphNode

from .graph_database import GraphDatabase

logger = create_logger(__name__)


class Neo4jGraphDatabase(GraphDatabase):
    """
    Neo4j implementation of GraphDatabase.

    Provides full CRUD operations for nodes and edges using the Neo4j Python driver.
    Supports Cypher queries for complex graph operations.

    Example:
        db = Neo4jGraphDatabase(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="password"
        )
        db.connect()
        node = GraphNode(id="person_1", labels=["Person"], properties={"name": "Alice"})
        db.create_node(node)
        db.disconnect()
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
        database: str = "neo4j",
    ) -> None:
        """
        Initialize Neo4j graph database.

        Args:
            uri: Neo4j connection URI (bolt:// or neo4j://)
            username: Database username
            password: Database password
            database: Database name
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.database = database
        self._driver: Driver | None = None

    def connect(self) -> None:
        """
        Establish connection to Neo4j.

        Raises:
            ConnectionError: If connection fails
        """
        try:
            self._driver = Neo4jDriver.driver(self.uri, auth=(self.username, self.password))
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {self.uri}")
        except ServiceUnavailable as e:
            raise ConnectionError(f"Failed to connect to Neo4j at {self.uri}: {e}")
        except Exception as e:
            raise ConnectionError(f"Neo4j connection error: {e}")

    def disconnect(self) -> None:
        """Close connection to Neo4j."""
        if self._driver:
            self._driver.close()
            self._driver = None
            logger.info("Disconnected from Neo4j")

    def is_connected(self) -> bool:
        """Check if database connection is active."""
        if not self._driver:
            return False
        try:
            self._driver.verify_connectivity()
            return True
        except Exception:
            return False

    def _get_session(self) -> Any:
        """Get a database session."""
        if not self._driver:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._driver.session(database=self.database)

    # Node operations

    def create_node(self, node: GraphNode) -> GraphNode:
        """
        Create a new node in the graph.

        Args:
            node: Node to create

        Returns:
            Created node

        Raises:
            ValueError: If node with same ID already exists
        """
        labels_str = ":".join(node.labels) if node.labels else "Node"
        properties = {**node.properties, "_id": node.id}

        query = f"""
        CREATE (n:{labels_str} $props)
        RETURN n
        """

        with self._get_session() as session:
            try:
                session.run(query, props=properties)
                logger.debug(f"Created node: {node.id}")
                return node
            except Neo4jError as e:
                logger.error(f"Failed to create node {node.id}: {e}")
                raise

    def get_node(self, node_id: str) -> GraphNode | None:
        """
        Retrieve a node by ID.

        Args:
            node_id: Unique node identifier

        Returns:
            Node if found, None otherwise
        """
        query = """
        MATCH (n {_id: $node_id})
        RETURN n, labels(n) as labels
        """

        with self._get_session() as session:
            result = session.run(query, node_id=node_id)
            record = result.single()

            if not record:
                return None

            node_data = dict(record["n"])
            labels = record["labels"]
            node_id_value = node_data.pop("_id", node_id)

            return GraphNode(
                id=node_id_value,
                labels=labels,
                properties=node_data,
            )

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
        query = """
        MATCH (n {_id: $node_id})
        SET n += $props
        RETURN n
        """

        with self._get_session() as session:
            result = session.run(query, node_id=node.id, props=node.properties)
            if not result.single():
                raise ValueError(f"Node not found: {node.id}")

            logger.debug(f"Updated node: {node.id}")
            return node

    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node and its relationships.

        Args:
            node_id: ID of node to delete

        Returns:
            True if deleted, False if not found
        """
        query = """
        MATCH (n {_id: $node_id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """

        with self._get_session() as session:
            result = session.run(query, node_id=node_id)
            record = result.single()
            deleted = record["deleted"] > 0 if record else False

            if deleted:
                logger.debug(f"Deleted node: {node_id}")
            return deleted

    def node_exists(self, node_id: str) -> bool:
        """
        Check if a node exists.

        Args:
            node_id: Node identifier

        Returns:
            True if exists, False otherwise
        """
        query = """
        MATCH (n {_id: $node_id})
        RETURN count(n) > 0 as exists
        """

        with self._get_session() as session:
            result = session.run(query, node_id=node_id)
            record = result.single()
            return bool(record["exists"]) if record else False

    # Edge operations

    def create_edge(self, edge: GraphEdge) -> GraphEdge:
        """
        Create an edge between two nodes.

        Args:
            edge: Edge to create

        Returns:
            Created edge

        Raises:
            ValueError: If source or target node does not exist
        """
        properties = {**edge.properties, "_id": edge.id}

        query = f"""
        MATCH (source {{_id: $source_id}})
        MATCH (target {{_id: $target_id}})
        CREATE (source)-[r:{edge.label} $props]->(target)
        RETURN r
        """

        with self._get_session() as session:
            try:
                result = session.run(
                    query,
                    source_id=edge.source,
                    target_id=edge.target,
                    props=properties,
                )
                if not result.single():
                    raise ValueError(
                        f"Source or target node not found: {edge.source}, {edge.target}"
                    )

                logger.debug(f"Created edge: {edge.id}")
                return edge
            except Neo4jError as e:
                logger.error(f"Failed to create edge {edge.id}: {e}")
                raise

    def get_edge(self, edge_id: str) -> GraphEdge | None:
        """
        Retrieve an edge by ID.

        Args:
            edge_id: Unique edge identifier

        Returns:
            Edge if found, None otherwise
        """
        query = """
        MATCH (source)-[r {_id: $edge_id}]->(target)
        RETURN r, type(r) as label, source._id as source_id, target._id as target_id
        """

        with self._get_session() as session:
            result = session.run(query, edge_id=edge_id)
            record = result.single()

            if not record:
                return None

            edge_data = dict(record["r"])
            edge_id_value = edge_data.pop("_id", edge_id)

            return GraphEdge(
                id=edge_id_value,
                source=record["source_id"],
                target=record["target_id"],
                label=record["label"],
                properties=edge_data,
            )

    def delete_edge(self, edge_id: str) -> bool:
        """
        Delete an edge.

        Args:
            edge_id: ID of edge to delete

        Returns:
            True if deleted, False if not found
        """
        query = """
        MATCH ()-[r {_id: $edge_id}]->()
        DELETE r
        RETURN count(r) as deleted
        """

        with self._get_session() as session:
            result = session.run(query, edge_id=edge_id)
            record = result.single()
            deleted = record["deleted"] > 0 if record else False

            if deleted:
                logger.debug(f"Deleted edge: {edge_id}")
            return deleted

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
        if relationship_type:
            query = f"""
            MATCH (source {{_id: $source_id}})-[r:{relationship_type}]->(target {{_id: $target_id}})
            RETURN r, type(r) as label
            """
        else:
            query = """
            MATCH (source {_id: $source_id})-[r]->(target {_id: $target_id})
            RETURN r, type(r) as label
            """

        edges: list[GraphEdge] = []
        with self._get_session() as session:
            result = session.run(query, source_id=source_id, target_id=target_id)
            for record in result:
                edge_data = dict(record["r"])
                edge_id = edge_data.pop("_id", "")
                edges.append(
                    GraphEdge(
                        id=edge_id,
                        source=source_id,
                        target=target_id,
                        label=record["label"],
                        properties=edge_data,
                    )
                )
        return edges

    # Query operations

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
        rel_pattern = f":{relationship_type}" if relationship_type else ""

        if direction == "out":
            query = f"""
            MATCH (n {{_id: $node_id}})-[{rel_pattern}]->(neighbor)
            RETURN neighbor, labels(neighbor) as labels
            """
        elif direction == "in":
            query = f"""
            MATCH (n {{_id: $node_id}})<-[{rel_pattern}]-(neighbor)
            RETURN neighbor, labels(neighbor) as labels
            """
        else:  # both
            query = f"""
            MATCH (n {{_id: $node_id}})-[{rel_pattern}]-(neighbor)
            RETURN DISTINCT neighbor, labels(neighbor) as labels
            """

        neighbors: list[GraphNode] = []
        with self._get_session() as session:
            result = session.run(query, node_id=node_id)
            for record in result:
                node_data = dict(record["neighbor"])
                neighbor_id = node_data.pop("_id", "")
                neighbors.append(
                    GraphNode(
                        id=neighbor_id,
                        labels=record["labels"],
                        properties=node_data,
                    )
                )
        return neighbors

    def get_node_edges(self, node_id: str, direction: str = "both") -> list[GraphEdge]:
        """
        Get all edges connected to a node.

        Args:
            node_id: Node ID
            direction: "in", "out", or "both"

        Returns:
            List of connected edges
        """
        if direction == "out":
            query = """
            MATCH (n {_id: $node_id})-[r]->(target)
            RETURN r, type(r) as label, n._id as source_id, target._id as target_id
            """
        elif direction == "in":
            query = """
            MATCH (source)-[r]->(n {_id: $node_id})
            RETURN r, type(r) as label, source._id as source_id, n._id as target_id
            """
        else:  # both
            query = """
            MATCH (n {_id: $node_id})-[r]-(other)
            WITH r, type(r) as label, startNode(r)._id as source_id, endNode(r)._id as target_id
            RETURN DISTINCT r, label, source_id, target_id
            """

        edges: list[GraphEdge] = []
        with self._get_session() as session:
            result = session.run(query, node_id=node_id)
            for record in result:
                edge_data = dict(record["r"])
                edge_id = edge_data.pop("_id", "")
                edges.append(
                    GraphEdge(
                        id=edge_id,
                        source=record["source_id"],
                        target=record["target_id"],
                        label=record["label"],
                        properties=edge_data,
                    )
                )
        return edges

    def find_nodes_by_label(
        self, label: str, properties: dict[str, Any] | None = None
    ) -> list[GraphNode]:
        """
        Find nodes by label and optional property filters.

        Args:
            label: Node label to search for
            properties: Property filters (optional)

        Returns:
            List of matching nodes
        """
        if properties:
            # Build property filter string
            prop_filters = " AND ".join([f"n.{k} = ${k}" for k in properties.keys()])
            query = f"""
            MATCH (n:{label})
            WHERE {prop_filters}
            RETURN n, labels(n) as labels
            """
            params = properties
        else:
            query = f"""
            MATCH (n:{label})
            RETURN n, labels(n) as labels
            """
            params = {}

        nodes: list[GraphNode] = []
        with self._get_session() as session:
            result = session.run(query, **params)
            for record in result:
                node_data = dict(record["n"])
                node_id = node_data.pop("_id", "")
                nodes.append(
                    GraphNode(
                        id=node_id,
                        labels=record["labels"],
                        properties=node_data,
                    )
                )
        return nodes

    def execute_query(self, query: str, parameters: dict[str, Any] | None = None) -> Any:
        """
        Execute a raw Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Query results as list of records
        """
        with self._get_session() as session:
            result = session.run(query, **(parameters or {}))
            return [dict(record) for record in result]

    # Bulk operations

    def create_nodes_batch(self, nodes: list[GraphNode]) -> list[GraphNode]:
        """
        Create multiple nodes in a single transaction.

        Args:
            nodes: List of nodes to create

        Returns:
            List of created nodes
        """
        if not nodes:
            return []

        with self._get_session() as session:
            with session.begin_transaction() as tx:
                for node in nodes:
                    labels_str = ":".join(node.labels) if node.labels else "Node"
                    properties = {**node.properties, "_id": node.id}
                    query = f"CREATE (n:{labels_str} $props)"
                    tx.run(query, props=properties)
                tx.commit()

        logger.info(f"Batch created {len(nodes)} nodes")
        return nodes

    def create_edges_batch(self, edges: list[GraphEdge]) -> list[GraphEdge]:
        """
        Create multiple edges in a single transaction.

        Args:
            edges: List of edges to create

        Returns:
            List of created edges
        """
        if not edges:
            return []

        with self._get_session() as session:
            with session.begin_transaction() as tx:
                for edge in edges:
                    properties = {**edge.properties, "_id": edge.id}
                    query = f"""
                    MATCH (source {{_id: $source_id}})
                    MATCH (target {{_id: $target_id}})
                    CREATE (source)-[r:{edge.label} $props]->(target)
                    """
                    tx.run(
                        query,
                        source_id=edge.source,
                        target_id=edge.target,
                        props=properties,
                    )
                tx.commit()

        logger.info(f"Batch created {len(edges)} edges")
        return edges

    def clear(self) -> None:
        """Delete all nodes and edges from the database."""
        query = "MATCH (n) DETACH DELETE n"

        with self._get_session() as session:
            session.run(query)
            logger.info("Cleared all nodes and edges from database")

    # Statistics

    def get_node_count(self) -> int:
        """Get total number of nodes."""
        query = "MATCH (n) RETURN count(n) as count"

        with self._get_session() as session:
            result = session.run(query)
            record = result.single()
            return int(record["count"]) if record else 0

    def get_edge_count(self) -> int:
        """Get total number of edges."""
        query = "MATCH ()-[r]->() RETURN count(r) as count"

        with self._get_session() as session:
            result = session.run(query)
            record = result.single()
            return int(record["count"]) if record else 0

    def __enter__(self) -> "Neo4jGraphDatabase":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit."""
        self.disconnect()
