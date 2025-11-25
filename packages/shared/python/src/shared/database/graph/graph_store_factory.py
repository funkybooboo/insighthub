"""Factory for creating graph store instances."""

from typing import Optional

from .graph_store import GraphStore
from .neo4j_graph_store import Neo4jGraphStore


def create_graph_store(
    store_type: str,
    **kwargs: str,
) -> Optional[GraphStore]:
    """
    Create a graph store instance based on configuration.

    Args:
        store_type: Type of graph store (e.g., "neo4j")
        **kwargs: Store-specific configuration

    Returns:
        GraphStore if creation succeeds, None if type unknown
    """
    if store_type == "neo4j":
        uri = kwargs.get("uri", "bolt://localhost:7687")
        username = kwargs.get("username", "neo4j")
        password = kwargs.get("password", "password")
        database = kwargs.get("database", "neo4j")
        return Neo4jGraphStore(uri, username, password, database)
    return None