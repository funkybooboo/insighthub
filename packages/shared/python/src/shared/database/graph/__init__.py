"""Graph database for knowledge graphs and relationships."""

from shared.database.graph.graph_database import GraphDatabase
from shared.database.graph.neo4j_graph_database import Neo4jGraphDatabase

__all__ = ["GraphDatabase", "Neo4jGraphDatabase"]
