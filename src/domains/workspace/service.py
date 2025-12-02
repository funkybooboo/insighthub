"""Workspace service for business logic."""

from src.config import config
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Workspace
from src.infrastructure.rag.workflows.create_resources import (
    CreateResourcesWorkflowFactory,
)
from src.infrastructure.rag.workflows.remove_resources import (
    RemoveResourcesWorkflowFactory,
)
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

        # Create workspace in database (status will be 'ready' after provisioning)
        workspace = self.repository.create(
            name.strip(), description, rag_type, status="provisioning"
        )

        logger.info(f"Workspace created in database: workspace_id={workspace.id}")

        # Provision RAG resources
        try:
            self._provision_rag_resources(workspace)
            # Update status to ready
            self.repository.update(workspace.id, status="ready")
            logger.info(f"Workspace provisioned successfully: workspace_id={workspace.id}")
        except Exception as e:
            # Update status to failed
            self.repository.update(workspace.id, status="failed")
            logger.error(f"Workspace provisioning failed: {e}", exc_info=True)
            raise ValueError(f"Failed to provision workspace resources: {e}")

        # Reload workspace with updated status
        workspace = self.repository.get_by_id(workspace.id)
        if not workspace:
            raise ValueError("Failed to reload workspace after provisioning")

        return workspace

    def _provision_rag_resources(self, workspace: Workspace) -> None:
        """Provision RAG resources for a workspace.

        Args:
            workspace: Workspace to provision resources for

        Raises:
            Exception: If provisioning fails
        """
        logger.info(f"Provisioning RAG resources for workspace {workspace.id}")

        # Build configuration for workflow
        rag_config = {
            "rag_type": workspace.rag_type,
            "qdrant_url": f"http://{config.vector_store.qdrant_host}:{config.vector_store.qdrant_port}",
            "vector_size": 768,  # nomic-embed-text dimension
            "distance": "cosine",
        }

        # Create and execute provisioning workflow
        workflow = CreateResourcesWorkflowFactory.create(rag_config)
        result = workflow.execute(str(workspace.id))

        if result.is_err():
            error = result.err()
            raise Exception(f"Provisioning workflow failed: {error.message}")

        logger.info(f"RAG resources provisioned for workspace {workspace.id}")

    def get_workspace(self, workspace_id: int) -> Workspace | None:
        """Get workspace by ID."""
        return self.repository.get_by_id(workspace_id)

    def list_workspaces(self) -> list[Workspace]:
        """List all workspace (single-user system)."""
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

        # Deallocate RAG resources
        try:
            self._deallocate_rag_resources(workspace)
        except Exception as e:
            logger.warning(f"Failed to deallocate workspace resources: {e}")

        # Delete from database
        self.repository.delete(workspace_id)
        logger.info(f"Workspace deleted: workspace_id={workspace_id}")

        return True

    def _deallocate_rag_resources(self, workspace: Workspace) -> None:
        """Deallocate RAG resources for a workspace.

        Args:
            workspace: Workspace to deallocate resources for

        Raises:
            Exception: If deallocation fails
        """
        logger.info(f"Deallocating RAG resources for workspace {workspace.id}")

        # Build configuration for workflow
        rag_config = {
            "rag_type": workspace.rag_type,
            "qdrant_url": f"http://{config.vector_store.qdrant_host}:{config.vector_store.qdrant_port}",
        }

        # Create and execute removal workflow
        workflow = RemoveResourcesWorkflowFactory.create(rag_config)
        result = workflow.execute(str(workspace.id))

        if result.is_err():
            error = result.err()
            raise Exception(f"Deallocation workflow failed: {error.message}")

        logger.info(f"RAG resources deallocated for workspace {workspace.id}")
