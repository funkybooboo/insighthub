"""Vector database interface for storing and retrieving vector embeddings."""

from abc import ABC, abstractmethod
from typing import Optional

from src.infrastructure.types.common import FilterDict, MetadataDict
from src.infrastructure.types.retrieval import RetrievalResult


class VectorDatabase(ABC):
    """
    Abstract interface for vector database operations.

    Implementations may use Qdrant, Pinecone, Weaviate, FAISS, etc.
    Provides CRUD operations for vectors and similarity search.

    Example:
        db = QdrantVectorDatabase(url="http://localhost:6333", collection="docs")
        db.upsert("chunk_1", [0.1, 0.2, ...], {"source": "document.pdf"})
        results = db.similarity_search([0.1, 0.2, ...], top_k=5)
    """

    @abstractmethod
    def upsert(self, id: str, vector: list[float], metadata: MetadataDict) -> None:
        """
        Insert or update a vector.

        Args:
            id: Unique identifier for the vector
            vector: Vector embedding
            metadata: Associated metadata
        """
        pass

    @abstractmethod
    def upsert_batch(self, items: list[tuple[str, list[float], MetadataDict]]) -> None:
        """
        Batch upsert multiple vectors.

        Args:
            items: List of (id, vector, metadata) tuples
        """
        pass

    @abstractmethod
    def similarity_search(
        self,
        vector: list[float],
        top_k: int = 10,
        filters: Optional[FilterDict] = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve top-k most similar vectors.

        Args:
            vector: Query vector
            top_k: Number of results to retrieve
            filters: Optional metadata filters

        Returns:
            List of retrieval results with scores
        """
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """
        Delete a vector by its ID.

        Args:
            id: Vector identifier to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def delete_batch(self, ids: list[str]) -> int:
        """
        Delete multiple vectors by ID.

        Args:
            ids: List of vector identifiers to delete

        Returns:
            Number of vectors deleted
        """
        pass

    @abstractmethod
    def exists(self, id: str) -> bool:
        """
        Check if a vector exists.

        Args:
            id: Vector identifier

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    def get(self, id: str) -> Optional[tuple[list[float], MetadataDict]]:
        """
        Retrieve a vector and its metadata by ID.

        Args:
            id: Vector identifier

        Returns:
            Tuple of (vector, metadata) if found, None otherwise
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Delete all vectors from the database."""
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Get total number of vectors.

        Returns:
            Vector count
        """
        pass
