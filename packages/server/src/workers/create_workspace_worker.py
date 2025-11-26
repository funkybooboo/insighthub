"""Workspace provisioning worker for creating workspace resources."""

from flask_socketio import SocketIO

from src.infrastructure.events import dispatch_event
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Workspace
from src.infrastructure.rag.workflows.factory import WorkflowFactory
from src.infrastructure.repositories.workspaces import WorkspaceRepository
from src.workers.tasks import run_async

logger = create_logger(__name__)


class CreateWorkspaceWorker:
    """
    Workspace provisioning worker that sets up workspace resources in background threads.

    The worker:
    1. Updates workspace status to 'provisioning'
    2. Executes CreateRagResourcesWorkflow to create storage resources
    3. Initializes default RAG configurations
    4. Updates workspace status to 'ready'
    5. Broadcasts status updates via WebSocket
    """

    def __init__(
        self,
        repository: WorkspaceRepository,
        socketio: SocketIO,
    ):
        """Initialize the workspace provision worker.

        Args:
            repository: Workspace repository for database operations
            socketio: Socket.IO instance for real-time updates
        """
        self.repository = repository
        self.socketio = socketio

    def start_provisioning(self, workspace: Workspace, user_id: int) -> None:
        """Start workspace provisioning in a background thread.

        Args:
            workspace: The workspace to provision
            user_id: ID of the user who owns the workspace
        """
        logger.info(f"Starting background provisioning for workspace {workspace.id}")

        # Execute provisioning in background thread
        run_async(self._provision_workspace_pipeline, workspace, user_id)

    def _provision_workspace_pipeline(self, workspace: Workspace, user_id: int) -> None:
        """Execute the workspace provisioning pipeline.

        Args:
            workspace: The workspace to provision
            user_id: ID of the user who owns the workspace
        """
        try:
            # Update status to provisioning
            self._update_status(
                workspace.id,
                user_id,
                "provisioning",
                "Initializing workspace resources",
            )

            # Get workspace RAG configuration
            logger.info(f"Building RAG config for workspace {workspace.id}")
            rag_config = self._build_rag_config(workspace)
            logger.info(f"Using RAG type: {rag_config.get('rag_type')}")

            # Create workflow dynamically based on workspace RAG config
            create_rag_resources_workflow = WorkflowFactory.create_create_rag_resources_workflow(rag_config)

            # Execute create RAG resources workflow to create storage resources
            logger.info(f"Executing create RAG resources workflow for workspace {workspace.id}")
            result = create_rag_resources_workflow.execute(
                workspace_id=str(workspace.id),
                config=None,  # Uses default config from workflow
            )

            if result.is_err():
                error = result.err()
                raise Exception(f"Provision workflow failed: {error.message}")

            # Initialize default RAG configs
            logger.info(f"Initializing default RAG configs for workspace {workspace.id}")
            self._initialize_default_configs(workspace)

            # Set up permissions/quotas (placeholder for future implementation)
            logger.info(f"Setting up permissions for workspace {workspace.id}")
            self._setup_permissions(workspace)

            # Update status to ready
            logger.info(f"Workspace {workspace.id} provisioned successfully")
            self._update_status(
                workspace.id,
                user_id,
                "ready",
                "Workspace ready for use",
            )

        except Exception as e:
            logger.error(f"Workspace {workspace.id} provisioning failed: {e}")

            # Update status to failed
            self._update_status(
                workspace.id,
                user_id,
                "failed",
                f"Provisioning failed: {str(e)}",
                error=str(e),
            )

            # Clean up any partial resources
            self._cleanup_failed_provisioning(workspace)

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
            "vector_size": getattr(workspace, "vector_size", 768),
            "distance": getattr(workspace, "distance", "cosine"),
        }

    def _initialize_default_configs(self, workspace: Workspace) -> None:
        """Initialize default RAG configurations for workspace.

        Args:
            workspace: The workspace to initialize configs for
        """
        # Default configs are created on-demand by the service layer
        # No action needed here for now
        pass

    def _setup_permissions(self, workspace: Workspace) -> None:
        """Set up permissions and quotas for workspace.

        Args:
            workspace: The workspace to set up permissions for
        """
        # TODO: Implement permission/quota setup when auth system is enhanced
        # For now, basic user_id ownership is sufficient
        pass

    def _update_status(
        self,
        workspace_id: int,
        user_id: int,
        status: str,
        message: str,
        error: str | None = None,
    ) -> None:
        """Update workspace provisioning status and broadcast to clients.

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            status: Provisioning status
            message: Status message
            error: Error message if failed
        """
        try:
            # Update in database
            self.repository.update(workspace_id, status=status)

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

    def _cleanup_failed_provisioning(self, workspace: Workspace) -> None:
        """Clean up any partial provisioning resources for failed workspaces.

        Uses the RemoveWorkspaceWorker to ensure consistent cleanup behavior.

        Args:
            workspace: The workspace that failed provisioning
        """
        try:
            logger.info(f"Cleaning up failed provisioning for workspace {workspace.id}")

            # Use the RemoveWorkspaceWorker for consistent cleanup
            from src.workers import get_remove_workspace_worker

            cleanup_worker = get_remove_workspace_worker()
            # Use the workspace owner's user_id for proper WebSocket notifications
            cleanup_worker.start_cleanup(workspace, user_id=workspace.user_id)

        except Exception as e:
            logger.warning(f"Failed to cleanup workspace {workspace.id}: {e}")


# Global worker instance (will be initialized in context)
_create_workspace_worker: CreateWorkspaceWorker | None = None


def get_create_workspace_worker() -> CreateWorkspaceWorker:
    """Get the global create workspace worker instance."""
    if _create_workspace_worker is None:
        raise RuntimeError(
            "Create workspace worker not initialized. Call initialize_create_workspace_worker() first."
        )
    return _create_workspace_worker


def initialize_create_workspace_worker(
    repository: WorkspaceRepository,
    socketio: SocketIO,
) -> CreateWorkspaceWorker:
    """Initialize the global create workspace worker instance.

    Args:
        repository: Workspace repository
        socketio: Socket.IO instance

    Returns:
        The initialized create workspace worker
    """
    global _create_workspace_worker
    _create_workspace_worker = CreateWorkspaceWorker(repository, socketio)
    return _create_workspace_worker
