"""
Base RAG Interface
Common interface for different RAG implementations (vector, graph, hybrid)
"""

from abc import ABC, abstractmethod
from enum import Enum

from src.rag.types import Document, JsonValue, LLMGenerator, Metadata, SearchResult, Stats


class RAGType(Enum):
    """Types of RAG implementations."""

    VECTOR = "vector"
    GRAPH = "graph"
    HYBRID = "hybrid"


class BaseRAG(ABC):
    """
    Abstract base class for RAG systems.
    Provides a common interface for vector, graph, and hybrid RAG implementations.
    """

    @abstractmethod
    def add_documents(
        self,
        documents: list[Document],
        text_key: str = "text",
        metadata_key: str = "metadata",
        batch_size: int = 100,
        **kwargs: JsonValue,
    ) -> int:
        """
        Add documents to the RAG system.

        Args:
            documents: List of documents to add
            text_key: Key containing document text
            metadata_key: Key containing document metadata
            **kwargs: Implementation-specific parameters

        Returns:
            Number of items added (chunks, nodes, etc.)
        """
        pass

    @abstractmethod
    def retrieve(
        self, query: str, top_k: int = 5, filter: Metadata | None = None, **kwargs: JsonValue
    ) -> list[SearchResult]:
        """
        Retrieve relevant items for a query.

        Args:
            query: The query text
            top_k: Number of results to return
            filter: Optional metadata filter
            **kwargs: Implementation-specific parameters

        Returns:
            List of retrieved items with scores and metadata
        """
        pass

    @abstractmethod
    def query(
        self,
        query: str,
        top_k: int = 5,
        filter: Metadata | None = None,
        llm_generator: LLMGenerator | None = None,
        return_context: bool = False,
        **kwargs: JsonValue,
    ) -> dict[str, str | list[SearchResult]]:
        """
        Full RAG query: retrieve relevant items and optionally generate a response.

        Args:
            query: The query text
            top_k: Number of items to retrieve
            filter: Optional metadata filter
            llm_generator: Optional function that takes (query, context) and generates a response
            return_context: Whether to return the retrieved context
            **kwargs: Implementation-specific parameters

        Returns:
            Dictionary containing query results and optional generated answer
        """
        pass

    @abstractmethod
    def clear(self):
        """Clear all data from the RAG system."""
        pass

    @abstractmethod
    def get_stats(self) -> Stats:
        """
        Get statistics about the RAG system.

        Returns:
            Dictionary with system statistics
        """
        pass

    @property
    @abstractmethod
    def rag_type(self) -> RAGType:
        """
        Get the type of RAG implementation.

        Returns:
            RAGType enum value
        """
        pass
