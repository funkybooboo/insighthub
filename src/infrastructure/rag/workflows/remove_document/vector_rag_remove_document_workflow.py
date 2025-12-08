"""Vector RAG implementation of remove document workflow."""

from returns.result import Failure, Result, Success

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.remove_document.remove_document_workflow import (
    RemoveDocumentWorkflow,
    RemoveDocumentWorkflowError,
)
from src.infrastructure.types.common import FilterDict
from src.infrastructure.vector_stores import VectorStore

logger = create_logger(__name__)


class VectorRagRemoveDocumentWorkflow(RemoveDocumentWorkflow):
    """
    Vector RAG implementation of document removal workflow.

    Pipeline:
    1. Build a metadata filter for the document and workspace.
    2. Call the vector store's delete method with the filter.
    3. Return the number of deleted chunks.
    """

    def __init__(self, vector_store: VectorStore):
        """Initialize workflow with a vector store.

        Args:
            vector_store: Vector store for chunk storage
        """
        self.vector_store = vector_store

    def execute(
        self,
        document_id: str,
        workspace_id: str,
    ) -> Result[int, RemoveDocumentWorkflowError]:
        """Execute removal workflow for a document.

        Args:
            document_id: Unique document identifier
            workspace_id: Workspace identifier for filtering

        Returns:
            Result containing number of chunks removed, or error
        """
        try:
            logger.info(f"Starting document removal for document_id={document_id}")

            filters: FilterDict = {"document_id": document_id, "workspace_id": workspace_id}
            chunks_deleted = self.vector_store.delete(filters)

            logger.info(f"Removed {chunks_deleted} chunks for document {document_id}")

            return Success(chunks_deleted)

        except Exception as e:
            logger.error(f"Document removal failed: {e}", exc_info=True)
            return Failure(
                RemoveDocumentWorkflowError(
                    message=f"Failed to remove document: {str(e)}",
                    step="document_removal",
                )
            )
