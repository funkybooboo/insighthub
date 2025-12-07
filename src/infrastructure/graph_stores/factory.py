"""Factory for creating graph store instances.

This module provides a factory for creating graph store implementations
based on configuration.
"""

from src.infrastructure.graph_stores.graph_store import GraphStore
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


class GraphStoreFactory:
    """Factory for creating graph store instances."""

    @staticmethod
    def create(store_type: str, **config) -> GraphStore:
        """Create a graph store instance.

        Args:
            store_type: Type of graph store ("neo4j")
            **config: Configuration parameters for the graph store

        Returns:
            GraphStore instance

        Raises:
            ValueError: If store_type is not recognized
            ImportError: If required dependencies for the store type are not installed

        Example:
            >>> store = GraphStoreFactory.create(
            ...     "neo4j",
            ...     uri="bolt://localhost:7687",
            ...     username="neo4j",
            ...     password="password"
            ... )
        """
        if store_type == "neo4j":
            try:
                from src.infrastructure.graph_stores.neo4j_graph_store import Neo4jGraphStore
            except ImportError as e:
                raise ImportError(
                    "Neo4j dependencies not installed. " "Install with: pip install neo4j"
                ) from e

            uri = config.get("uri", "bolt://localhost:7687")
            username = config.get("username", "neo4j")
            password = config.get("password", "password")

            logger.info(f"Creating Neo4j graph store with URI: {uri}")
            return Neo4jGraphStore(uri=uri, username=username, password=password)

        raise ValueError(f"Unknown graph store type: {store_type}")
