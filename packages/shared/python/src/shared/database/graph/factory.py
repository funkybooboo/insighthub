"""Factory for creating graph database instances."""

from enum import Enum

from shared.types.option import Nothing, Option, Some

from .graph_database import GraphDatabase
from .neo4j_graph_database import Neo4jGraphDatabase


class GraphDatabaseType(Enum):
    """Enum for graph database implementation types."""

    NEO4J = "neo4j"


def create_graph_database(
    db_type: str,
    uri: str | None = None,
    username: str | None = None,
    password: str | None = None,
    database: str | None = None,
) -> Option[GraphDatabase]:
    """
    Create a graph database instance based on configuration.

    Args:
        db_type: Type of graph database ("neo4j")
        uri: Database URI (required for neo4j)
        username: Authentication username (required for neo4j)
        password: Authentication password (required for neo4j)
        database: Database name (optional, defaults to "neo4j")

    Returns:
        Some(GraphDatabase) if creation succeeds, Nothing() if type unknown or params missing

    Note:
        Additional graph database providers (ArangoDB, etc.) can be
        added here when implemented.
    """
    try:
        db_enum = GraphDatabaseType(db_type)
    except ValueError:
        return Nothing()

    if db_enum == GraphDatabaseType.NEO4J:
        if uri is None or username is None or password is None:
            return Nothing()
        return Some(
            Neo4jGraphDatabase(
                uri=uri,
                username=username,
                password=password,
                database=database or "neo4j",
            )
        )

    return Nothing()
