"""Factory for creating vector database instances."""

from enum import Enum

from .qdrant_vector_database import QdrantVectorDatabase
from .qdrant_vector_store import QdrantVectorStore
from .vector_database import VectorDatabase
from .vector_store import VectorStore


class VectorDatabaseType(Enum):
    """Enum for vector database implementation types."""

    QDRANT = "qdrant"


class VectorStoreFactory:
    """Factory class for creating vector stores."""

    @staticmethod
    def create_vector_store(store_type: str, **kwargs) -> VectorStore:
        """Create a vector store instance. Alias for create_vector_store function.

        Args:
            store_type: Type of vector store to create
            **kwargs: Additional configuration (url, collection_name, vector_size, api_key)

        Returns:
            VectorStore instance

        Raises:
            ValueError: If store_type is not supported or required parameters are missing
        """
        return create_vector_store(
            db_type=store_type,
            url=kwargs.get("url") or kwargs.get("host", "localhost"),
            collection_name=kwargs.get("collection_name", "document"),
            vector_size=kwargs.get("vector_size", 768),
            api_key=kwargs.get("api_key"),
        )


AVAILABLE_VECTOR_STORES = {
    "qdrant": {
        "label": "Qdrant",
        "description": "Open-source vector similarity search engine",
    },
}


def get_available_vector_stores() -> list[dict[str, str]]:
    """Get list of available vector store implementations."""
    return [
        {
            "value": key,
            "label": info["label"],
            "description": info["description"],
        }
        for key, info in AVAILABLE_VECTOR_STORES.items()
    ]


def create_vector_database(
    db_type: str,
    url: str | None = None,
    collection_name: str | None = None,
    vector_size: int | None = None,
    api_key: str | None = None,
) -> VectorDatabase:
    """
    Create a vector database instance based on configuration.

    Args:
        db_type: Type of vector database ("qdrant")
        url: Database URL (required for qdrant)
        collection_name: Collection/index name (required for qdrant)
        vector_size: Dimension of vectors (required for qdrant)
        api_key: API key for authentication (optional)

    Returns:
        VectorDatabase instance

    Raises:
        ValueError: If db_type is not supported or required parameters are missing

    Note:
        Additional vector database providers (Pinecone, Weaviate, FAISS) can be
        added here when implemented.
    """
    try:
        db_enum = VectorDatabaseType(db_type)
    except ValueError:
        available = [e.value for e in VectorDatabaseType]
        raise ValueError(
            f"Unsupported vector database type: {db_type}. "
            f"Available types: {', '.join(available)}"
        )

    if db_enum == VectorDatabaseType.QDRANT:
        if url is None:
            raise ValueError("url is required for Qdrant vector database")
        if collection_name is None:
            raise ValueError("collection_name is required for Qdrant vector database")
        if vector_size is None:
            raise ValueError("vector_size is required for Qdrant vector database")

        return QdrantVectorDatabase(
            url=url,
            collection_name=collection_name,
            vector_size=vector_size,
            api_key=api_key,
        )

    raise ValueError(f"Unsupported vector database type: {db_type}")


def create_vector_store(
    db_type: str,
    url: str | None = None,
    collection_name: str | None = None,
    vector_size: int | None = None,
    api_key: str | None = None,
) -> VectorStore:
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
        VectorStore instance

    Raises:
        ValueError: If db_type is not supported or required parameters are missing

    Example:
        store = create_vector_store(
            db_type="qdrant",
            url="http://localhost:6333",
            collection_name="document",
            vector_size=384
        )
        store.add(chunks)
        results = store.search(query_embedding, top_k=5)
    """
    # Create underlying database (raises ValueError if invalid)
    database = create_vector_database(
        db_type=db_type,
        url=url,
        collection_name=collection_name,
        vector_size=vector_size,
        api_key=api_key,
    )

    # Wrap in VectorStore adapter
    try:
        db_enum = VectorDatabaseType(db_type)
    except ValueError:
        available = [e.value for e in VectorDatabaseType]
        raise ValueError(
            f"Unsupported vector database type: {db_type}. "
            f"Available types: {', '.join(available)}"
        )

    if db_enum == VectorDatabaseType.QDRANT:
        # database is guaranteed to be QdrantVectorDatabase since we created it above
        if not isinstance(database, QdrantVectorDatabase):
            raise TypeError("Expected QdrantVectorDatabase but got different type")
        return QdrantVectorStore(database)

    raise ValueError(f"Unsupported vector database type: {db_type}")
