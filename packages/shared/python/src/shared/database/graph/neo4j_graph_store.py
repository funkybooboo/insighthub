"""Neo4j implementation of GraphStore."""

from typing import List

from shared.database.graph.graph_store import GraphStore
from shared.database.graph.neo4j_graph_database import Neo4jGraphDatabase
from shared.types.graph import Graph, GraphEdge, GraphNode


class Neo4jGraphStore(GraphStore):
    """Neo4j implementation of the GraphStore interface."""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        username: str = "neo4j",
        password: str = "password",
        database: str = "neo4j",
    ):
        """
        Initialize Neo4j graph store.

        Args:
            uri: Neo4j connection URI
            username: Database username
            password: Database password
            database: Database name
        """
        self.db = Neo4jGraphDatabase(uri, username, password, database)

    def add_graph(self, graph: Graph) -> None:
        """
        Add a graph to the store.

        For now, we expect graph to be a dict with 'nodes' and 'edges' keys.
        This is a temporary implementation until the Graph type is properly defined.
        """
        # Connect to database
        self.db.connect()

        try:
            # Extract nodes and edges from graph
            nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
            edges = graph.get("edges", []) if isinstance(graph, dict) else []

            # Create nodes in batch
            if nodes:
                graph_nodes = []
                for node_data in nodes:
                    if isinstance(node_data, dict):
                        node = GraphNode(
                            id=node_data.get("id", ""),
                            labels=node_data.get("labels", ["Node"]),
                            properties=node_data.get("properties", {})
                        )
                        graph_nodes.append(node)
                self.db.create_nodes_batch(graph_nodes)

            # Create edges in batch
            if edges:
                graph_edges = []
                for edge_data in edges:
                    if isinstance(edge_data, dict):
                        edge = GraphEdge(
                            id=edge_data.get("id", ""),
                            source=edge_data.get("source", ""),
                            target=edge_data.get("target", ""),
                            label=edge_data.get("label", "RELATED"),
                            properties=edge_data.get("properties", {})
                        )
                        graph_edges.append(edge)
                self.db.create_edges_batch(graph_edges)

        finally:
            self.db.disconnect()

    def get_neighbors(self, node: GraphNode) -> List[GraphNode]:
        """Get the neighbors of a node."""
        self.db.connect()
        try:
            return self.db.get_neighbors(node.id)
        finally:
            self.db.disconnect()

    def get_all_nodes(self) -> List[GraphNode]:
        """Get all nodes in the graph."""
        self.db.connect()
        try:
            # Use a Cypher query to get all nodes
            query = "MATCH (n) RETURN n, labels(n) as labels"
            results = self.db.execute_query(query)

            nodes = []
            for record in results:
                node_data = dict(record["n"])
                node_id = node_data.pop("_id", "")
                labels = record["labels"]
                nodes.append(GraphNode(
                    id=node_id,
                    labels=labels,
                    properties=node_data
                ))
            return nodes
        finally:
            self.db.disconnect()

    def get_all_relationships(self) -> List[GraphEdge]:
        """Get all relationships in the graph."""
        self.db.connect()
        try:
            # Use a Cypher query to get all relationships
            query = """
            MATCH (source)-[r]->(target)
            RETURN r, type(r) as label, source._id as source_id, target._id as target_id
            """
            results = self.db.execute_query(query)

            edges = []
            for record in results:
                edge_data = dict(record["r"])
                edge_id = edge_data.pop("_id", "")
                edges.append(GraphEdge(
                    id=edge_id,
                    source=record["source_id"],
                    target=record["target_id"],
                    label=record["label"],
                    properties=edge_data
                ))
            return edges
        finally:
            self.db.disconnect()

    def clear(self) -> None:
        """Clear the graph store."""
        self.db.connect()
        try:
            self.db.clear()
        finally:
            self.db.disconnect()