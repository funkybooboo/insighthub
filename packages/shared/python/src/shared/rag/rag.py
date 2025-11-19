"""
Abstract RAG interface defining the core RAG operations.
"""

from abc import ABC, abstractmethod

from src.infrastructure.rag.types import Document, QueryResult, RagStats, RetrievalResult


class Rag(ABC):
    """
    Abstract base class for Retrieval-Augmented Generation (RAG) systems.

    All RAG systems (vector-based, graph-based) should implement this interface.
    """

    @abstractmethod
    def add_documents(self, documents: list[Document], batch_size: int = 100) -> int:
        """
        Ingest and process documents into the RAG system.

        Args:
            documents: List of documents with 'text' and optional metadata.
            batch_size: Number of documents to process per batch.

        Returns:
            Total number of chunks or nodes created.
        """
        ...

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """
        Retrieve relevant chunks or nodes for a query without generation.

        Args:
            query: The search query.
            top_k: Maximum number of results to return.

        Returns:
            List of retrieved chunks with metadata and relevance scores.
        """
        ...

    @abstractmethod
    def query(
        self,
        query: str,
        top_k: int = 5,
        generate_answer: bool = True,
    ) -> QueryResult:
        """
        Full RAG pipeline: retrieve context and optionally generate an LLM answer.

        Args:
            query: The user query.
            top_k: Number of chunks to retrieve.
            generate_answer: Whether to generate an answer from retrieved context.

        Returns:
            QueryResult containing retrieved chunks, optional answer, and stats.
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """
        Clear all documents and internal state from the RAG system.
        """
        ...

    @abstractmethod
    def get_stats(self) -> RagStats:
        """
        Retrieve system statistics.

        Returns:
            RagStats including counts, configuration, and other relevant metrics.
        """
        ...
