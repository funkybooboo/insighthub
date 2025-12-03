"""Base interface for add document workflows.

All RAG implementations (Vector RAG, Graph RAG) must implement this interface
for document ingestion workflows.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO

from returns.result import Result

from src.infrastructure.types.common import MetadataDict


class AddDocumentWorkflowError(Exception):
    """Error during add document workflow execution."""

    def __init__(self, message: str, step: str) -> None:
        """Initialize workflow error.

        Args:
            message: Error message
            step: Workflow step where error occurred
        """
        self.message = message
        self.step = step
        super().__init__(f"[{step}] {message}")


class AddDocumentWorkflow(ABC):
    """
    Base interface for document addition workflows.

    All RAG implementations must provide an add document workflow that:
    1. Accepts raw document content
    2. Processes it through their specific pipeline
    3. Indexes the processed content
    4. Returns the number of chunks/entities indexed

    Workers execute workflows by calling execute() in background threads.
    """

    @abstractmethod
    def execute(
        self,
        raw_document: BinaryIO,
        document_id: str,
        workspace_id: str,
        metadata: MetadataDict | None = None,
    ) -> Result[int, AddDocumentWorkflowError]:
        """
        Execute the add document workflow for document ingestion.

        Args:
            raw_document: Binary document content to process
            document_id: Unique document identifier
            workspace_id: Workspace identifier for filtering
            metadata: Optional metadata to attach to chunks/entities

        Returns:
            Result containing number of chunks/entities indexed, or error

        Implementation Notes:
            - Vector RAG: parse -> chunk -> embed -> index in vector store
            - Graph RAG: parse -> extract entities -> extract relationships -> index in graph
        """
        pass
