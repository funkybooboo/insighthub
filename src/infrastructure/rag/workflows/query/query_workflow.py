"""Base interface for query workflows.

All RAG implementations (Vector RAG, Graph RAG) must implement this interface
for retrieval workflows.
"""

from typing import Optional

from abc import ABC, abstractmethod

from src.infrastructure.types.common import FilterDict
from src.infrastructure.types.rag import ChunkData


class QueryWorkflowError(Exception):
    """Error during query workflow execution."""

    def __init__(self, message: str, step: str) -> None:
        """Initialize workflow error.

        Args:
            message: Error message
            step: Workflow step where error occurred
        """
        self.message = message
        self.step = step
        super().__init__(f"[{step}] {message}")


class QueryWorkflow(ABC):
    """
    Base interface for query/retrieval workflows.

    All RAG implementations must provide a query workflow that:
    1. Accepts a user query
    2. Retrieves relevant context using their specific approach
    3. Returns ranked results as ChunkData

    Workers execute workflows by calling execute() in background threads.
    """

    @abstractmethod
    def execute(
        self,
        query_text: str,
        top_k: int = 5,
        filters: Optional[FilterDict]= None,
    ) -> list[ChunkData]:
        """
        Execute the query workflow for context retrieval.

        Args:
            query_text: User's query text
            top_k: Number of results to return
            filters: Optional filters (workspace_id, document_id, etc.)

        Returns:
            List of relevant chunks/entities with scores

        Raises:
            QueryWorkflowError: If any step in the pipeline fails

        Implementation Notes:
            - Vector RAG: embed query -> vector search -> rerank -> return chunks
            - Graph RAG: extract entities -> graph traversal -> community search -> return chunks
        """
        pass
