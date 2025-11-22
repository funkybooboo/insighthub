"""Factory for creating vector database instances."""

from enum import Enum

from shared.types.option import Nothing, Option, Some

from .qdrant_vector_database import QdrantVectorDatabase
from .vector_database import VectorDatabase


class VectorDatabaseType(Enum):
    """Enum for vector database implementation types."""

    QDRANT = "qdrant"


def create_vector_database(
    db_type: str,
    url: str | None = None,
    collection_name: str | None = None,
    vector_size: int | None = None,
    api_key: str | None = None,
) -> Option[VectorDatabase]:
    """
    Create a vector database instance based on configuration.

    Args:
        db_type: Type of vector database ("qdrant")
        url: Database URL (required for qdrant)
        collection_name: Collection/index name (required for qdrant)
        vector_size: Dimension of vectors (required for qdrant)
        api_key: API key for authentication (optional)

    Returns:
        Some(VectorDatabase) if creation succeeds, Nothing() if type unknown or params missing

    Note:
        Additional vector database providers (Pinecone, Weaviate, FAISS) can be
        added here when implemented.
    """
    try:
        db_enum = VectorDatabaseType(db_type)
    except ValueError:
        return Nothing()

    if db_enum == VectorDatabaseType.QDRANT:
        if url is None or collection_name is None or vector_size is None:
            return Nothing()
        return Some(
            QdrantVectorDatabase(
                url=url,
                collection_name=collection_name,
                vector_size=vector_size,
                api_key=api_key,
            )
        )

    return Nothing()
