"""Base interface for remove RAG resources workflows.

All RAG implementations (Vector RAG, Graph RAG) must implement this interface
for workspace resource deletion workflows.
"""

from abc import ABC, abstractmethod

from src.infrastructure.types.result import Result


class RemoveRagResourcesWorkflowError(Exception):
    """Error during remove RAG resources workflow execution."""

    def __init__(self, message: str, step: str) -> None:
        """Initialize workflow error.

        Args:
            message: Error message
            step: Workflow step where error occurred
        """
        self.message = message
        self.step = step
        super().__init__(f"[{step}] {message}")


class RemoveRagResourcesWorkflow(ABC):
    """
    Base interface for workspace RAG resource removal workflows.

    All RAG implementations must provide a remove resources workflow that:
    1. Deletes storage resources (collections, databases, etc.)
    2. Cleans up indexes and schemas
    3. Removes any associated configurations
    4. Returns success/failure status

    Workers execute workflows by calling execute() in background threads.
    """

    @abstractmethod
    def execute(
        self,
        workspace_id: str,
    ) -> Result[bool, RemoveRagResourcesWorkflowError]:
        """
        Execute the remove RAG resources workflow for workspace deletion.

        Args:
            workspace_id: Unique workspace identifier

        Returns:
            Result containing success status (True), or error

        Implementation Notes:
            - Vector RAG: delete Qdrant collection
            - Graph RAG: delete Neo4j database
        """
        pass
