"""Vector storage interface for storing and retrieving vector embeddings."""

from abc import ABC, abstractmethod
from typing import Any, List

from shared.types.retrieval import RetrievalResult


class VectorIndex(ABC):
    """
    Interface for storing and retrieving vector embeddings.
    
    Implementations should support different vector databases:
    - Qdrant
    - Pinecone
    - Weaviate
    - FAISS
    """

    @abstractmethod
    def upsert(self, id: str, vector: List[float], metadata: dict[str, Any]) -> None:
        """
        Insert or update a vector in the store.

        Args:
            id: Unique identifier for the vector
            vector: Vector embedding
            metadata: Associated metadata

        Raises:
            VectorStoreError: If operation fails
        """
        pass

    @abstractmethod
    def upsert_many(self, items: List[tuple[str, List[float], dict[str, Any]]]) -> None:
        """
        Batch upsert multiple vectors.

        Args:
            items: List of (id, vector, metadata) tuples

        Raises:
            VectorStoreError: If operation fails
        """
        pass

    @abstractmethod
    def similarity_search(self, vector: List[float], top_k: int = 10, filters: dict[str, Any] | None = None) -> List[RetrievalResult]:
        """
        Retrieve top-k most similar vectors.

        Args:
            vector: Query vector
            top_k: Number of results to retrieve
            filters: Optional metadata filters

        Returns:
            List[RetrievalResult]: Similar vectors with scores

        Raises:
            VectorStoreError: If operation fails
        """
        pass

    @abstractmethod
    def delete(self, id: str) -> None:
        """
        Delete a vector by its ID.

        Args:
            id: Vector identifier to delete

        Raises:
            VectorStoreError: If operation fails
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear all vectors from the store.

        Raises:
            VectorStoreError: If operation fails
        """
        pass