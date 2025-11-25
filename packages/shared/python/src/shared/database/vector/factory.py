"""Factory for creating vector database instances."""

from enum import Enum
from typing import Optional

from .qdrant_vector_database import QdrantVectorDatabase
from .qdrant_vector_store import QdrantVectorStore
from .vector_database import VectorDatabase
from .vector_store import VectorStore


class VectorDatabaseType(Enum):
    """Enum for vector database implementation types."""

    QDRANT = "qdrant"


def create_vector_database(
    db_type: str,
    url: str | None = None,
    collection_name: str | None = None,
    vector_size: int | None = None,
    api_key: str | None = None,
) -> Optional[VectorDatabase]:
    """
    Create a vector database instance based on configuration.

    Args:
        db_type: Type of vector database ("qdrant")
        url: Database URL (required for qdrant)
        collection_name: Collection/index name (required for qdrant)
        vector_size: Dimension of vectors (required for qdrant)
        api_key: API key for authentication (optional)

    Returns:
        VectorDatabase if creation succeeds, None if type unknown or params missing

    Note:
        Additional vector database providers (Pinecone, Weaviate, FAISS) can be
        added here when implemented.
    """
    try:
        db_enum = VectorDatabaseType(db_type)
    except ValueError:
        return None

    if db_enum == VectorDatabaseType.QDRANT:
        if url is None or collection_name is None or vector_size is None:
            return None
        return QdrantVectorDatabase(
            url=url,
            collection_name=collection_name,
            vector_size=vector_size,
            api_key=api_key,
        )

    return None


def create_vector_store(
    db_type: str,
    url: str | None = None,
    collection_name: str | None = None,
    vector_size: int | None = None,
    api_key: str | None = None,
) -> Optional[VectorStore]:
    """
    Create a vector store instance (high-level interface).

    This creates a VectorStore that works with Chunk objects,
    wrapping the lower-level VectorDatabase implementation.

    Args:
        db_type: Type of vector database ("qdrant")
        url: Database URL (required for qdrant)
        collection_name: Collection/index name (required for qdrant)
        vector_size: Dimension of vectors (required for qdrant)
        api_key: API key for authentication (optional)

    Returns:
        VectorStore if creation succeeds, None if type unknown or params missing

    Example:
        store = create_vector_store(
            db_type="qdrant",
            url="http://localhost:6333",
            collection_name="documents",
            vector_size=384
        )
        store.add(chunks)
        results = store.search(query_embedding, top_k=5)
    """
    # Create underlying database
    database = create_vector_database(
        db_type=db_type,
        url=url,
        collection_name=collection_name,
        vector_size=vector_size,
        api_key=api_key,
    )

    if database is None:
        return None

    # Wrap in VectorStore adapter
    try:
        db_enum = VectorDatabaseType(db_type)
    except ValueError:
        return None

    if db_enum == VectorDatabaseType.QDRANT:
        return QdrantVectorStore(database)  # type: ignore  # database is QdrantVectorDatabase

    return None
