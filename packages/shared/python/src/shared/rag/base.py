"""Abstract base classes for RAG systems and components."""

from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Dict, List, Optional, Protocol

from shared.types.document import Document
from shared.types.retrieval import RetrievalResult


class RAGSystem(ABC):
    """
    Abstract base class for RAG (Retrieval-Augmented Generation) systems.

    This defines the interface that all RAG systems must implement,
    allowing for easy extension and swapping of different RAG approaches.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this RAG system."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of this RAG system."""
        pass

    @abstractmethod
    def index(self, file: BinaryIO, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """
        Index a document for retrieval.

        Args:
            file: The document file to index
            metadata: Optional metadata for the document

        Returns:
            The indexed document
        """
        pass

    @abstractmethod
    def query(self, query: str, top_k: int = 5, **kwargs) -> List[RetrievalResult]:
        """
        Query the RAG system for relevant information.

        Args:
            query: The search query
            top_k: Number of results to return
            **kwargs: Additional query parameters

        Returns:
            List of retrieval results
        """
        pass

    @abstractmethod
    def delete(self, document_id: str) -> bool:
        """
        Delete a document from the RAG system.

        Args:
            document_id: ID of document to delete

        Returns:
            True if successfully deleted
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the RAG system.

        Returns:
            Health status information
        """
        pass


class RAGIndexer(ABC):
    """
    Abstract base class for document indexing components.

    Handles the document ingestion and preprocessing pipeline.
    """

    @abstractmethod
    def index(self, file: BinaryIO, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """
        Index a document.

        Args:
            file: The document file to index
            metadata: Optional metadata

        Returns:
            The indexed document
        """
        pass


class RAGRetriever(ABC):
    """
    Abstract base class for retrieval components.

    Handles querying and retrieving relevant information.
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5, **kwargs) -> List[RetrievalResult]:
        """
        Retrieve relevant information for a query.

        Args:
            query: The search query
            top_k: Number of results to return
            **kwargs: Additional retrieval parameters

        Returns:
            List of retrieval results
        """
        pass


class RAGGenerator(ABC):
    """
    Abstract base class for generation components.

    Handles generating responses using retrieved context.
    """

    @abstractmethod
    def generate(self, query: str, context: List[RetrievalResult], **kwargs) -> str:
        """
        Generate a response using query and context.

        Args:
            query: The original query
            context: Retrieved context documents
            **kwargs: Additional generation parameters

        Returns:
            Generated response
        """
        pass


class RAGConfig(Protocol):
    """
    Protocol for RAG system configuration.

    Defines the interface that configuration objects must implement.
    """

    @property
    def system_type(self) -> str:
        """Type of RAG system (vector, graph, hybrid, etc.)."""
        ...

    @property
    def components(self) -> Dict[str, Any]:
        """Component configurations."""
        ...

    def validate(self) -> bool:
        """Validate the configuration."""
        ...


class WorkerFactory(ABC):
    """
    Abstract factory for creating workers.

    Allows different RAG systems to define their own worker creation logic.
    """

    @abstractmethod
    def create_indexing_workers(self, config: RAGConfig) -> List['Worker']:
        """
        Create workers for the indexing pipeline.

        Args:
            config: RAG system configuration

        Returns:
            List of indexing workers
        """
        pass

    @abstractmethod
    def create_query_workers(self, config: RAGConfig) -> List['Worker']:
        """
        Create workers for the query pipeline.

        Args:
            config: RAG system configuration

        Returns:
            List of query workers
        """
        pass

    @abstractmethod
    def create_maintenance_workers(self, config: RAGConfig) -> List['Worker']:
        """
        Create workers for maintenance operations.

        Args:
            config: RAG system configuration

        Returns:
            List of maintenance workers
        """
        pass


# Forward reference for Worker (avoiding circular imports)
class Worker(Protocol):
    """Protocol for worker classes."""

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process a message."""
        ...

    def start(self) -> None:
        """Start the worker."""
        ...

    def stop(self) -> None:
        """Stop the worker."""
        ...