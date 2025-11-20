"""Vector store implementations for Qdrant and in-memory storage."""

from typing import Any, List, Dict

from shared.interfaces.vector.store import VectorIndex
from shared.types.retrieval import RetrievalResult


class QdrantVectorStore(VectorIndex):
    """
    Qdrant vector database implementation.
    
    Provides persistent vector storage with:
    - Collection management
    - Metadata filtering
    - Similarity search
    """

    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "documents"):
        """
        Initialize Qdrant vector store.

        Args:
            host: Qdrant host
            port: Qdrant port
            collection_name: Collection name
        """
        self.host = host
        self.port = port
        self.collection_name = collection_name
        # TODO: Initialize Qdrant client
        self.client = None

    def _get_client(self):
        """Get or create Qdrant client."""
        # TODO: Implement Qdrant client initialization
        from qdrant_client import QdrantClient
        return QdrantClient(host=self.host, port=self.port)

    def upsert(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        """
        Insert or update a vector in Qdrant.

        Args:
            id: Unique identifier for the vector
            vector: Vector embedding
            metadata: Associated metadata

        Raises:
            VectorStoreError: If operation fails
        """
        # TODO: Implement Qdrant upsert
        pass

    def similarity_search(self, vector: List[float], top_k: int = 10, filters: Dict[str, Any] | None = None) -> List[RetrievalResult]:
        """
        Search for similar vectors in Qdrant.

        Args:
            vector: Query vector
            top_k: Number of results to retrieve
            filters: Optional metadata filters

        Returns:
            List[RetrievalResult]: Similar vectors with scores

        Raises:
            VectorStoreError: If operation fails
        """
        # TODO: Implement Qdrant similarity search
        pass

    def delete(self, id: str) -> None:
        """
        Delete a vector by its ID.

        Args:
            id: Vector identifier to delete

        Raises:
            VectorStoreError: If operation fails
        """
        # TODO: Implement Qdrant deletion
        pass

    def clear(self) -> None:
        """
        Clear all vectors from the collection.

        Raises:
            VectorStoreError: If operation fails
        """
        # TODO: Implement Qdrant collection clearing
        pass


class InMemoryVectorStore(VectorIndex):
    """
    In-memory vector store for testing and development.
    
    Stores vectors in a simple Python dictionary.
    """

    def __init__(self):
        """
        Initialize in-memory vector store.
        """
        self._vectors: Dict[str, List[float]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def upsert(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        """
        Insert or update a vector in memory.

        Args:
            id: Unique identifier for the vector
            vector: Vector embedding
            metadata: Associated metadata

        Raises:
            VectorStoreError: If operation fails
        """
        self._vectors[id] = {
            "vector": vector,
            "metadata": metadata
        }

    def similarity_search(self, vector: List[float], top_k: int = 10, filters: Dict[str, Any] | None = None) -> List[RetrievalResult]:
        """
        Search for similar vectors in memory.

        Args:
            vector: Query vector
            top_k: Number of results to retrieve
            filters: Optional metadata filters

        Returns:
            List[RetrievalResult]: Similar vectors with scores

        Raises:
            VectorStoreError: If operation fails
        """
        # Simple cosine similarity implementation
        results = []
        query_norm = self._normalize_vector(vector)
        
        for vector_id, stored_vector in self._vectors.items():
            stored_norm = self._normalize_vector(stored_vector)
            similarity = self._cosine_similarity(query_norm, stored_norm)
            
            results.append(RetrievalResult(
                id=vector_id,
                score=similarity,
                source="memory",
                payload={
                    "vector": stored_vector,
                    "metadata": self._metadata[vector_id]
                }
            ))
        
        # Sort by similarity and return top-k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """
        Normalize a vector for cosine similarity calculation.
        """
        import math
        norm = math.sqrt(sum(x * x for x in vector))
        if norm == 0:
            return vector
        return [x / norm for x in vector]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        """
        return sum(a * b for a, b in zip(vec1, vec2))

    def delete(self, id: str) -> None:
        """
        Delete a vector by its ID.

        Args:
            id: Vector identifier to delete

        Raises:
            VectorStoreError: If operation fails
        """
        if id in self._vectors:
            del self._vectors[id]
            del self._metadata[id]

    def clear(self) -> None:
        """
        Clear all vectors from memory.
        """
        self._vectors.clear()
        self._metadata.clear()