"""Database interfaces and implementations for InsightHub.

This module provides access to:
- Vector databases for similarity search (Qdrant)
- Graph databases for knowledge graphs (Neo4j)
"""

from shared.database.graph import GraphDatabase, Neo4jGraphDatabase
from shared.database.vector import QdrantVectorDatabase, VectorDatabase

__all__ = [
    "VectorDatabase",
    "QdrantVectorDatabase",
    "GraphDatabase",
    "Neo4jGraphDatabase",
]
