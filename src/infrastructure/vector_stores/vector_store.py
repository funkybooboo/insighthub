"""Vector store interface for storing and retrieving vector embeddings."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from src.infrastructure.types.common import FilterDict, MetadataDict
from src.infrastructure.types.document import Chunk


class VectorStore(ABC):
    """
    Interface for vector database operations.

    Implementations should support different vector databases:
    - Qdrant
    - Pinecone
    - In-memory (for testing)
    """

    @abstractmethod
    def add(self, vectors: List[List[float]], ids: List[str], payloads: List[MetadataDict]) -> None:
        """
        Add vectors to the vector store.

        Args:
            vectors: List of vector embeddings
            ids: List of unique IDs for the vectors
            payloads: List of metadata payloads for the vectors

        Raises:
            VectorStoreError: If adding vectors fails
        """
        pass

    @abstractmethod
    def search(
        self, query_embedding: List[float], top_k: int = 5, filters: Optional[FilterDict] = None
    ) -> List[Tuple[Chunk, float]]:
        """
        Search for similar chunks in the vector store.

        Args:
            query_embedding: The embedding of the query
            top_k: The number of similar chunks to return
            filters: Optional filters for the search

        Returns:
            A list of tuples, where each tuple contains a chunk and its similarity score.

        Raises:
            VectorStoreError: If searching fails
        """
        pass

    @abstractmethod
    def delete(self, filters: FilterDict) -> int:
        """
        Delete vectors from the vector store based on metadata filters.

        Args:
            filters: A dictionary of metadata key-value pairs to match.

        Returns:
            The number of vectors deleted.

        Raises:
            VectorStoreError: If deleting vectors fails.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear the vector store.

        Raises:
            VectorStoreError: If clearing fails
        """
        pass
