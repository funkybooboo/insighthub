"""Factory for creating vector store instances."""

from enum import Enum
from typing import Optional

from .qdrant_vector_store import QdrantVectorStore
from .vector_store import VectorStore


class VectorStoreType(Enum):
    """Enum for vector store implementation types."""

    QDRANT = "qdrant"


class VectorStoreFactory:
    """Factory class for creating vector stores."""

    @staticmethod
    def create_vector_store(store_type: str, **kwargs) -> VectorStore:
        """Create a vector store instance.

        Args:
            store_type: Type of vector store to create
            **kwargs: Additional configuration (url, collection_name, vector_size, api_key)

        Returns:
            VectorStore instance

        Raises:
            ValueError: If store_type is not supported or required parameters are missing
        """
        return create_vector_store(
            store_type=store_type,
            url=kwargs.get("url") or kwargs.get("host", "localhost"),
            collection_name=kwargs.get("collection_name", "document"),
            vector_size=kwargs.get("vector_size", 768),
            api_key=kwargs.get("api_key"),
        )

    @staticmethod
    def create(store_type: str, **kwargs) -> VectorStore:
        """Create a vector store instance. Alias for create_vector_store.

        Args:
            store_type: Type of vector store to create
            **kwargs: Additional configuration

        Returns:
            VectorStore instance
        """
        return VectorStoreFactory.create_vector_store(store_type, **kwargs)


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


def create_vector_store(
    store_type: str,
    url: Optional[str] = None,
    collection_name: Optional[str] = None,
    vector_size: Optional[int] = None,
    api_key: Optional[str] = None,
) -> VectorStore:
    """
    Create a vector store instance based on configuration.

    Args:
        store_type: Type of vector store ("qdrant")
        url: Store URL (required for qdrant)
        collection_name: Collection/index name (required for qdrant)
        vector_size: Dimension of vectors (required for qdrant)
        api_key: API key for authentication (optional)

    Returns:
        VectorStore instance

    Raises:
        ValueError: If store_type is not supported or required parameters are missing

    Example:
        store = create_vector_store(
            store_type="qdrant",
            url="http://localhost:6333",
            collection_name="document",
            vector_size=384
        )
        store.add(vectors, ids, payloads)
        results = store.search(query_embedding, top_k=5)

    Note:
        Additional vector store providers (Pinecone, Weaviate, FAISS) can be
        added here when implemented.
    """
    try:
        store_enum = VectorStoreType(store_type)
    except ValueError:
        available = [e.value for e in VectorStoreType]
        raise ValueError(
            f"Unsupported vector store type: {store_type}. "
            f"Available types: {', '.join(available)}"
        )

    if store_enum == VectorStoreType.QDRANT:
        if url is None:
            raise ValueError("url is required for Qdrant vector store")
        if collection_name is None:
            raise ValueError("collection_name is required for Qdrant vector store")
        if vector_size is None:
            raise ValueError("vector_size is required for Qdrant vector store")

        return QdrantVectorStore(
            url=url,
            collection_name=collection_name,
            vector_size=vector_size,
            api_key=api_key,
        )

    raise ValueError(f"Unsupported vector store type: {store_type}")
