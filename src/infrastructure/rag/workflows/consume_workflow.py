"""Base interface for consume workflows.

All RAG implementations (Vector RAG, Graph RAG) must implement this interface
for document ingestion workflows.

DEPRECATED: Use AddDocumentWorkflow instead. This interface is kept for backward compatibility.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO

from src.infrastructure.rag.workflows.add_document_workflow import AddDocumentWorkflowError
from src.infrastructure.types.common import MetadataDict
from src.infrastructure.types.result import Result


class ConsumeWorkflowError(AddDocumentWorkflowError):
    """Error during consume workflow execution.

    DEPRECATED: Use AddDocumentWorkflowError instead.
    This class is kept for backward compatibility.
    """

    pass


class ConsumeWorkflow(ABC):
    """
    Base interface for document consumption workflows.

    All RAG implementations must provide a consume workflow that:
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
    ) -> Result[int, ConsumeWorkflowError]:
        """
        Execute the consume workflow for document ingestion.

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
