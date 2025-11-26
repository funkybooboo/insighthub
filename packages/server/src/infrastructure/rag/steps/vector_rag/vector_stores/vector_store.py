"""Vector store interface for storing and retrieving vector embeddings."""

from abc import ABC, abstractmethod
from typing import List, Tuple

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
    def add(self, chunks: List[Chunk]) -> None:
        """
        Add chunks to the vector store.

        Args:
            chunks: List of chunks to add

        Raises:
            VectorStoreError: If adding chunks fails
        """
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Chunk, float]]:
        """
        Search for similar chunks in the vector store.

        Args:
            query_embedding: The embedding of the query
            top_k: The number of similar chunks to return

        Returns:
            A list of tuples, where each tuple contains a chunk and its similarity score.

        Raises:
            VectorStoreError: If searching fails
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
