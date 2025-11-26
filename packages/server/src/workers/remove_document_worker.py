"""Remove document worker for deleting document resources."""

from flask_socketio import SocketIO

from src.infrastructure.events import dispatch_event
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Document
from src.infrastructure.rag.workflows.factory import WorkflowFactory
from src.infrastructure.repositories.documents import DocumentRepository
from src.infrastructure.repositories.workspaces import WorkspaceRepository
from src.infrastructure.storage import BlobStorage
from src.workers.tasks import run_async

logger = create_logger(__name__)


class RemoveDocumentWorker:
    """
    Document cleanup worker that deletes document resources in background threads.

    The worker:
    1. Updates document status to 'deleting'
    2. Removes chunks from vector/graph store (executes RemoveDocumentWorkflow)
    3. Deletes file from blob storage
    4. Deletes document from database
    5. Broadcasts completion status via WebSocket
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        workspace_repository: WorkspaceRepository,
        blob_storage: BlobStorage,
        socketio: SocketIO,
    ):
        """Initialize the document cleanup worker.

        Args:
            document_repository: Document repository for database operations
            workspace_repository: Workspace repository for RAG config lookup
            blob_storage: Blob storage for file operations
            socketio: Socket.IO instance for real-time updates
        """
        self.document_repository = document_repository
        self.workspace_repository = workspace_repository
        self.blob_storage = blob_storage
        self.socketio = socketio

    def start_cleanup(self, document: Document, user_id: int) -> None:
        """Start document cleanup in a background thread.

        Args:
            document: The document to delete
            user_id: ID of the user who owns the document
        """
        logger.info(f"Starting background cleanup for document {document.id}")

        # Execute cleanup in background thread
        run_async(self._cleanup_document_pipeline, document, user_id)

    def _cleanup_document_pipeline(self, document: Document, user_id: int) -> None:
        """Execute the document cleanup pipeline.

        Args:
            document: The document to delete
            user_id: ID of the user who owns the document
        """
        try:
            # Update status to deleting
            self._update_status(
                document.id,
                user_id,
                document.workspace_id,
                "deleting",
                "Deleting document and associated data",
                filename=document.filename,
            )

            # TODO: Remove chunks from vector/graph store
            # This should execute a CleanupWorkflow to remove all chunks
            # associated with this document_id
            logger.info(f"Removing chunks for document {document.id} from vector/graph store")
            self._remove_chunks_from_store(document)

            # Delete file from blob storage
            if document.file_path:
                logger.info(f"Deleting blob storage file: {document.file_path}")
                try:
                    self.blob_storage.delete(document.file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete blob {document.file_path}: {e}")
                    # Continue with deletion even if blob storage delete fails

            # Delete document from database
            logger.info(f"Deleting document {document.id} from database")
            self.document_repository.delete(document.id)

            # Broadcast completion status
            logger.info(f"Document {document.id} deleted successfully")
            self._update_status(
                document.id,
                user_id,
                document.workspace_id,
                "deleted",
                "Document deleted successfully",
                filename=document.filename,
            )

        except Exception as e:
            logger.error(f"Document {document.id} cleanup failed: {e}", exc_info=True)

            # Update status to failed
            self._update_status(
                document.id,
                user_id,
                document.workspace_id,
                "failed",
                f"Deletion failed: {str(e)}",
                filename=document.filename,
                error=str(e),
            )

    def _remove_chunks_from_store(self, document: Document) -> None:
        """Remove all chunks associated with this document from vector/graph store.

        Args:
            document: The document whose chunks should be removed
        """
        try:
            # Get workspace RAG configuration
            logger.info(f"Looking up workspace {document.workspace_id} RAG config")
            workspace = self.workspace_repository.get_by_id(document.workspace_id)
            if not workspace:
                logger.warning(f"Workspace {document.workspace_id} not found, skipping chunk removal")
                return

            rag_config = self._build_rag_config(workspace)
            logger.info(f"Using RAG type: {rag_config.get('rag_type')}")

            # Create workflow dynamically based on workspace RAG config
            remove_document_workflow = WorkflowFactory.create_remove_document_workflow(rag_config)

            # Execute RemoveDocumentWorkflow to delete all chunks
            logger.info(f"Executing remove document workflow for document {document.id}")
            result = remove_document_workflow.execute(
                document_id=str(document.id),
                workspace_id=str(document.workspace_id),
            )

            if result.is_ok():
                chunks_removed = result.unwrap()
                logger.info(f"Removed {chunks_removed} chunks for document {document.id}")
            else:
                error = result.err()
                logger.warning(f"Failed to remove chunks: {error}")
                # Continue with document deletion even if chunk removal fails

        except Exception as e:
            logger.warning(f"Failed to remove chunks from store: {e}")
            # Don't raise exception, continue with document deletion

    def _build_rag_config(self, workspace: object) -> dict:
        """Build RAG configuration dictionary from workspace model.

        Args:
            workspace: Workspace model with RAG configuration

        Returns:
            RAG configuration dictionary for WorkflowFactory
        """
        # Extract RAG config from workspace model
        # Default to vector RAG if not specified
        return {
            "rag_type": getattr(workspace, "rag_type", "vector"),
            "vector_store_type": getattr(workspace, "vector_store_type", "qdrant"),
            "vector_store_config": getattr(workspace, "vector_store_config", {
                "host": "localhost",
                "port": 6333,
                "collection_name": f"workspace_{workspace.id}",
            }),
        }

    def _update_status(
        self,
        document_id: int,
        user_id: int,
        workspace_id: int | None,
        status: str,
        message: str,
        filename: str = "",
        error: str | None = None,
    ) -> None:
        """Update document cleanup status and broadcast to clients.

        Args:
            document_id: Document ID
            user_id: User ID
            workspace_id: Workspace ID
            status: Cleanup status
            message: Status message
            filename: Document filename
            error: Error message if failed
        """
        try:
            # Broadcast via WebSocket
            status_data = {
                "document_id": document_id,
                "user_id": user_id,
                "workspace_id": workspace_id,
                "status": status,
                "message": message,
                "filename": filename,
                "error": error,
            }

            dispatch_event("document.status.updated", status_data)

        except Exception as e:
            logger.error(f"Failed to update document status: {e}")


# Global worker instance (will be initialized in context)
_remove_document_worker: RemoveDocumentWorker | None = None


def get_remove_document_worker() -> RemoveDocumentWorker:
    """Get the global remove document worker instance."""
    if _remove_document_worker is None:
        raise RuntimeError(
            "Remove document worker not initialized. Call initialize_remove_document_worker() first."
        )
    return _remove_document_worker


def initialize_remove_document_worker(
    document_repository: DocumentRepository,
    workspace_repository: WorkspaceRepository,
    blob_storage: BlobStorage,
    socketio: SocketIO,
) -> RemoveDocumentWorker:
    """Initialize the global remove document worker instance.

    Args:
        document_repository: Document repository
        workspace_repository: Workspace repository for RAG config lookup
        blob_storage: Blob storage
        socketio: Socket.IO instance

    Returns:
        The initialized remove document worker
    """
    global _remove_document_worker
    _remove_document_worker = RemoveDocumentWorker(
        document_repository, workspace_repository, blob_storage, socketio
    )
    return _remove_document_worker
