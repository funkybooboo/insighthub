"""RAG system interfaces and types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from src.infrastructure.types.common import MetadataDict


@dataclass
class ChunkData:
    """Data returned from RAG query for a single chunk."""

    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: MetadataDict


@dataclass
class QueryResult:
    """Result from a RAG query."""

    chunks: list[ChunkData]
    query: str
    workspace_id: Optional[str] = None


class RagSystem(ABC):
    """
    Abstract base class for RAG system implementations.

    Defines the interface that all RAG systems must implement,
    whether Vector RAG, Graph RAG, or hybrid approaches.
    """

    @abstractmethod
    def query(
        self,
        query_text: str,
        workspace_id: Optional[int] = None,
        top_k: int = 5,
    ) -> list[QueryResult]:
        """
        Query the RAG system for relevant context.

        Args:
            query_text: The user's query
            workspace_id: Optional workspace to filter results
            top_k: Number of results to return

        Returns:
            List of query results with chunks and scores
        """
        pass
