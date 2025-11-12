"""Abstract RAG interface defining the core RAG operations."""

from abc import ABC, abstractmethod

from infrastructure.rag.types import Document, QueryResult, RagStats, RetrievalResult


class Rag(ABC):
    """
    Abstract base class for RAG implementations.

    All RAG systems (Vector, Graph) must implement this interface.
    """

    @abstractmethod
    def add_documents(self, documents: list[Document], batch_size: int = 100) -> int:
        """
        Ingest and process documents into the RAG system.

        Args:
            documents: List of documents with 'text' and optional metadata
            batch_size: Number of documents to process in each batch

        Returns:
            Number of chunks/nodes created
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """
        Retrieve relevant chunks/nodes for a query without generation.

        Args:
            query: The search query
            top_k: Number of results to return

        Returns:
            List of retrieved chunks with metadata and scores
        """
        pass

    @abstractmethod
    def query(
        self,
        query: str,
        top_k: int = 5,
        generate_answer: bool = True,
    ) -> QueryResult:
        """
        Full RAG pipeline: retrieve context and optionally generate answer.

        Args:
            query: The user query
            top_k: Number of chunks to retrieve
            generate_answer: Whether to generate an LLM answer

        Returns:
            QueryResult with chunks, optional answer, and stats
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all data from the RAG system."""
        pass

    @abstractmethod
    def get_stats(self) -> RagStats:
        """
        Get system statistics.

        Returns:
            RagStats with counts and configuration
        """
        pass
