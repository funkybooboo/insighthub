"""Base interface for create RAG resources workflows.

All RAG implementations (Vector RAG, Graph RAG) must implement this interface
for workspace resource provisioning workflows.
"""

from abc import ABC, abstractmethod
from typing import Optional

from returns.result import Result


class CreateRagResourcesWorkflowError(Exception):
    """Error during create RAG resources workflow execution."""

    def __init__(self, message: str, step: str) -> None:
        """Initialize workflow error.

        Args:
            message: Error message
            step: Workflow step where error occurred
        """
        self.message = message
        self.step = step
        super().__init__(f"[{step}] {message}")


class CreateRagResourcesWorkflow(ABC):
    """
    Base interface for workspace RAG resource creation workflows.

    All RAG implementations must provide a create resources workflow that:
    1. Creates necessary storage resources (collections, databases, etc.)
    2. Initializes indexes and schemas
    3. Sets up any required configurations
    4. Returns success/failure status

    Workers execute workflows by calling execute() in background threads.
    """

    @abstractmethod
    def execute(
        self,
        workspace_id: str,
        config: Optional[dict[str, str | int | float | bool]] = None,
    ) -> Result[bool, CreateRagResourcesWorkflowError]:
        """
        Execute the create RAG resources workflow for workspace setup.

        Args:
            workspace_id: Unique workspace identifier
            config: Optional configuration parameters for resource creation

        Returns:
            Result containing success status (True), or error

        Implementation Notes:
            - Vector RAG: create Qdrant collection with proper vector dimensions
            - Graph RAG: create Neo4j database and initialize schema
        """
        pass
