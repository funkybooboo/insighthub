"""Base interface for remove document workflows.

All RAG implementations (Vector RAG, Graph RAG) must implement this interface
for document removal workflows.
"""

from abc import ABC, abstractmethod

from returns.result import Result


class RemoveDocumentWorkflowError(Exception):
    """Error during remove document workflow execution."""

    def __init__(self, message: str, step: str) -> None:
        """Initialize workflow error.

        Args:
            message: Error message
            step: Workflow step where error occurred
        """
        self.message = message
        self.step = step
        super().__init__(f"[{step}] {message}")


class RemoveDocumentWorkflow(ABC):
    """
    Base interface for document removal workflows.

    All RAG implementations must provide a remove document workflow that:
    1. Accepts document identifier
    2. Removes all associated chunks/entities from storage
    3. Returns the number of chunks/entities removed

    Workers execute workflows by calling execute() in background threads.
    """

    @abstractmethod
    def execute(
        self,
        document_id: str,
        workspace_id: str,
    ) -> Result[int, RemoveDocumentWorkflowError]:
        """
        Execute the remove document workflow for document deletion.

        Args:
            document_id: Unique document identifier
            workspace_id: Workspace identifier for filtering

        Returns:
            Result containing number of chunks/entities removed, or error

        Implementation Notes:
            - Vector RAG: query chunks by document_id -> delete from vector store
            - Graph RAG: query entities by document_id -> delete nodes and relationships
        """
        pass
