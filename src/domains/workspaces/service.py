"""Workspace service for business logic."""

from src.infrastructure.logger import create_logger
from src.infrastructure.models import Workspace
from src.infrastructure.repositories import WorkspaceRepository

logger = create_logger(__name__)


class WorkspaceService:
    """Service for workspace-related business logic."""

    def __init__(self, repository: WorkspaceRepository):
        """Initialize service with repository."""
        self.repository = repository

    def create_workspace(
        self,
        name: str,
        description: str | None = None,
        rag_type: str = "vector",
    ) -> Workspace:
        """Create a new workspace synchronously (single-user CLI system)."""
        logger.info(f"Creating workspace: name='{name}', rag_type='{rag_type}'")

        # Validate inputs
        if not name or not name.strip():
            logger.error("Workspace creation failed: empty name")
            raise ValueError("Workspace name cannot be empty")

        if len(name.strip()) > 255:
            logger.error(f"Workspace creation failed: name too long '{name[:50]}...'")
            raise ValueError("Workspace name too long (max 255 characters)")

        if description and len(description) > 1000:
            logger.error("Workspace creation failed: description too long")
            raise ValueError("Workspace description too long (max 1000 characters)")

        if rag_type not in ["vector", "graph"]:
            logger.error(f"Workspace creation failed: invalid rag_type '{rag_type}'")
            raise ValueError("Invalid rag_type. Must be 'vector' or 'graph'")

        # Create workspace in database with status='ready' (no async provisioning in CLI)
        workspace = self.repository.create(
            name.strip(), description, rag_type, status="ready"
        )

        logger.info(f"Workspace created: workspace_id={workspace.id}, status='ready'")

        return workspace

    def get_workspace(self, workspace_id: int) -> Workspace | None:
        """Get workspace by ID."""
        return self.repository.get_by_id(workspace_id)

    def list_workspaces(self) -> list[Workspace]:
        """List all workspaces (single-user system)."""
        return self.repository.get_all()

    def update_workspace(
        self, workspace_id: int, name: str | None = None, description: str | None = None
    ) -> Workspace | None:
        """Update workspace name and/or description."""
        logger.info(f"Updating workspace {workspace_id}")

        # Validate inputs
        if name is not None:
            if not name.strip():
                raise ValueError("Workspace name cannot be empty")
            if len(name.strip()) > 255:
                raise ValueError("Workspace name too long (max 255 characters)")

        if description is not None and len(description) > 1000:
            raise ValueError("Workspace description too long (max 1000 characters)")

        updates = {}
        if name is not None:
            updates["name"] = name.strip()
        if description is not None:
            updates["description"] = description

        return self.repository.update(workspace_id, **updates)

    def delete_workspace(self, workspace_id: int) -> bool:
        """Delete workspace synchronously (single-user CLI system).

        Args:
            workspace_id: ID of the workspace to delete

        Returns:
            bool: True if deleted, False if workspace not found
        """
        logger.info(f"Deleting workspace: workspace_id={workspace_id}")

        # Get workspace
        workspace = self.repository.get_by_id(workspace_id)
        if not workspace:
            logger.warning(f"Workspace deletion failed: workspace not found (workspace_id={workspace_id})")
            return False

        # Delete workspace directly (no background worker in CLI)
        try:
            from src.workers import get_remove_workspace_worker

            cleanup_worker = get_remove_workspace_worker()
            cleanup_worker.cleanup_workspace(workspace)
        except Exception as e:
            logger.warning(f"Failed to cleanup workspace resources: {e}")

        # Delete from database
        self.repository.delete(workspace_id)
        logger.info(f"Workspace deleted: workspace_id={workspace_id}")

        return True
