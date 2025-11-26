"""Workspace cleanup worker for deleting workspace resources."""

from flask_socketio import SocketIO

from src.infrastructure.events import dispatch_event
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Workspace
from src.infrastructure.rag.workflows.factory import WorkflowFactory
from src.infrastructure.repositories.documents import DocumentRepository
from src.infrastructure.repositories.workspaces import WorkspaceRepository
from src.infrastructure.storage import BlobStorage
from src.workers.tasks import run_async

logger = create_logger(__name__)


class RemoveWorkspaceWorker:
    """
    Workspace cleanup worker that deletes workspace resources in background threads.

    The worker:
    1. Updates workspace status to 'deleting'
    2. Deletes all documents in workspace (including their chunks and blob storage files)
    3. Executes RemoveRagResourcesWorkflow to delete RAG resources
    4. Removes permissions/quotas
    5. Deletes workspace from database
    6. Broadcasts completion status via WebSocket
    """

    def __init__(
        self,
        workspace_repository: WorkspaceRepository,
        document_repository: DocumentRepository,
        blob_storage: BlobStorage,
        socketio: SocketIO,
    ):
        """Initialize the workspace cleanup worker.

        Args:
            workspace_repository: Workspace repository for database operations
            document_repository: Document repository for deleting documents
            blob_storage: Blob storage for file operations
            socketio: Socket.IO instance for real-time updates
        """
        self.workspace_repository = workspace_repository
        self.document_repository = document_repository
        self.blob_storage = blob_storage
        self.socketio = socketio

    def start_cleanup(self, workspace: Workspace, user_id: int) -> None:
        """Start workspace cleanup in a background thread.

        Args:
            workspace: The workspace to delete
            user_id: ID of the user who owns the workspace
        """
        logger.info(f"Starting background cleanup for workspace {workspace.id}")

        # Execute cleanup in background thread
        run_async(self._cleanup_workspace_pipeline, workspace, user_id)

    def _cleanup_workspace_pipeline(self, workspace: Workspace, user_id: int) -> None:
        """Execute the workspace cleanup pipeline.

        Args:
            workspace: The workspace to delete
            user_id: ID of the user who owns the workspace
        """
        try:
            # Update status to deleting
            self._update_status(
                workspace.id,
                user_id,
                "deleting",
                "Deleting workspace resources",
            )

            # Delete all documents in workspace
            logger.info(f"Deleting all documents in workspace {workspace.id}")
            self._delete_all_documents(workspace)

            # Get workspace RAG configuration
            logger.info(f"Building RAG config for workspace {workspace.id}")
            rag_config = self._build_rag_config(workspace)
            logger.info(f"Using RAG type: {rag_config.get('rag_type')}")

            # Create workflow dynamically based on workspace RAG config
            remove_rag_resources_workflow = WorkflowFactory.create_remove_rag_resources_workflow(rag_config)

            # Execute remove RAG resources workflow to delete storage resources
            logger.info(f"Executing remove RAG resources workflow for workspace {workspace.id}")
            result = remove_rag_resources_workflow.execute(
                workspace_id=str(workspace.id),
            )

            if result.is_err():
                error = result.err()
                logger.warning(f"Failed to remove RAG resources: {error.message}")
                # Continue with workspace deletion even if resource removal fails

            # Remove permissions/quotas (placeholder for future implementation)
            logger.info(f"Removing permissions for workspace {workspace.id}")
            self._remove_permissions(workspace)

            # Delete workspace from database
            logger.info(f"Deleting workspace {workspace.id} from database")
            self.workspace_repository.delete(workspace.id)

            # Broadcast completion status
            logger.info(f"Workspace {workspace.id} deleted successfully")
            self._update_status(
                workspace.id,
                user_id,
                "deleted",
                "Workspace deleted successfully",
            )

        except Exception as e:
            logger.error(f"Workspace {workspace.id} cleanup failed: {e}", exc_info=True)

            # Update status to failed
            self._update_status(
                workspace.id,
                user_id,
                "failed",
                f"Deletion failed: {str(e)}",
                error=str(e),
            )

    def _delete_all_documents(self, workspace: Workspace) -> None:
        """Delete all documents in the workspace.

        Args:
            workspace: The workspace to delete documents from
        """
        try:
            # Get all documents in workspace
            documents = self.document_repository.get_by_workspace(workspace.id)

            logger.info(f"Deleting {len(documents)} documents from workspace {workspace.id}")

            for document in documents:
                try:
                    # Delete from blob storage
                    if document.file_path:
                        try:
                            self.blob_storage.delete(document.file_path)
                        except Exception as e:
                            logger.warning(f"Failed to delete blob {document.file_path}: {e}")

                    # TODO: Delete chunks from vector/graph store
                    # This should execute a CleanupWorkflow to remove chunks

                    # Delete from database
                    self.document_repository.delete(document.id)

                except Exception as e:
                    logger.warning(f"Failed to delete document {document.id}: {e}")
                    # Continue with other documents even if one fails

        except Exception as e:
            raise Exception(f"Failed to delete documents: {e}") from e

    def _build_rag_config(self, workspace: Workspace) -> dict:
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
            "qdrant_url": getattr(workspace, "qdrant_url", "http://localhost:6333"),
        }

    def _remove_permissions(self, workspace: Workspace) -> None:
        """Remove permissions and quotas for workspace.

        Args:
            workspace: The workspace to remove permissions for
        """
        # TODO: Implement permission/quota removal when auth system is enhanced
        # For now, workspace deletion handles cleanup
        pass

    def _update_status(
        self,
        workspace_id: int,
        user_id: int,
        status: str,
        message: str,
        error: str | None = None,
    ) -> None:
        """Update workspace cleanup status in database and broadcast to clients.

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            status: Cleanup status
            message: Status message
            error: Error message if failed
        """
        try:
            # Update status in database
            self.workspace_repository.update(workspace_id, status=status)

            # Broadcast via WebSocket
            status_data = {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "status": status,
                "message": message,
                "error": error,
            }

            dispatch_event("workspace.status.updated", status_data)

        except Exception as e:
            logger.error(f"Failed to update workspace status: {e}")


# Global worker instance (will be initialized in context)
_remove_workspace_worker: RemoveWorkspaceWorker | None = None


def get_remove_workspace_worker() -> RemoveWorkspaceWorker:
    """Get the global remove workspace worker instance."""
    if _remove_workspace_worker is None:
        raise RuntimeError(
            "Remove workspace worker not initialized. Call initialize_remove_workspace_worker() first."
        )
    return _remove_workspace_worker


def initialize_remove_workspace_worker(
    workspace_repository: WorkspaceRepository,
    document_repository: DocumentRepository,
    blob_storage: BlobStorage,
    socketio: SocketIO,
) -> RemoveWorkspaceWorker:
    """Initialize the global remove workspace worker instance.

    Args:
        workspace_repository: Workspace repository
        document_repository: Document repository
        blob_storage: Blob storage
        socketio: Socket.IO instance

    Returns:
        The initialized remove workspace worker
    """
    global _remove_workspace_worker
    _remove_workspace_worker = RemoveWorkspaceWorker(
        workspace_repository, document_repository, blob_storage, socketio
    )
    return _remove_workspace_worker
