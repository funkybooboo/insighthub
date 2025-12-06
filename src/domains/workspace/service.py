"""Workspace service for business logic."""

from typing import Optional

from returns.result import Failure, Result, Success

from src.config import config
from src.domains.default_rag_config.models import DefaultRagConfig
from src.domains.default_rag_config.service import DefaultRagConfigService
from src.domains.workspace.data_access import WorkspaceDataAccess
from src.domains.workspace.models import VectorRagConfig, Workspace, WorkspaceStatus
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.create_resources import CreateResourcesWorkflowFactory
from src.infrastructure.rag.workflows.remove_resources import RemoveResourcesWorkflowFactory
from src.infrastructure.types import DatabaseError, NotFoundError, WorkflowError

logger = create_logger(__name__)


class WorkspaceService:
    """Service for workspace-related business logic.

    Note: Input validation is handled by validation.py layer.
    This service assumes inputs are already validated and cleaned.
    """

    def __init__(
        self,
        data_access: WorkspaceDataAccess,
        default_rag_config_service: DefaultRagConfigService,
    ):
        """Initialize service with data access and default config service.

        Args:
            data_access: Workspace data access layer (handles cache + repository)
            default_rag_config_service: Service for default RAG configuration
        """
        self.data_access = data_access
        self.default_rag_config_service = default_rag_config_service

    def create_workspace(
        self,
        name: str,
        description: Optional[str],
        rag_type: str,
    ) -> Result[Workspace, WorkflowError | DatabaseError]:
        """Create a new workspace.

        Args:
            name: Workspace name (validated)
            description: Optional description (validated)
            rag_type: RAG type (validated)

        Returns:
            Result with Workspace model or error
        """
        logger.info(f"Creating workspace: name='{name}', rag_type='{rag_type}'")

        # Get default RAG config
        default_config = self.default_rag_config_service.get_config()
        if not default_config:
            return Failure(WorkflowError("Default RAG configuration not found", "create_workspace"))

        # Create workspace in database via data access layer
        workspace_result = self.data_access.create(
            name, description, rag_type, status=WorkspaceStatus.PROVISIONING.value
        )
        if isinstance(workspace_result, Failure):
            return workspace_result

        workspace = workspace_result.unwrap()
        logger.info(f"Workspace created in database: workspace_id={workspace.id}")

        # Update status: initializing config
        self.data_access.update(workspace.id, status=WorkspaceStatus.INITIALIZING_CONFIG.value)
        logger.info(f"Workspace {workspace.id}: initializing configuration")

        # Snapshot the default config for this specific workspace
        if workspace.rag_type == "vector":
            new_vector_config = VectorRagConfig(
                workspace_id=workspace.id,
                embedding_model_vector_size=default_config.vector_config.embedding_model_vector_size,
                distance_metric=default_config.vector_config.distance_metric,
                embedding_algorithm=default_config.vector_config.embedding_algorithm,
                chunking_algorithm=default_config.vector_config.chunking_algorithm,
                rerank_algorithm=default_config.vector_config.rerank_algorithm,
                chunk_size=default_config.vector_config.chunk_size,
                chunk_overlap=default_config.vector_config.chunk_overlap,
                top_k=default_config.vector_config.top_k,
            )
            config_create_result = self.data_access.repository.create_vector_rag_config(
                new_vector_config
            )
            if isinstance(config_create_result, Failure):
                return Failure(config_create_result.failure())
        # TODO: Add similar logic for 'graph' rag_type

        # Provision RAG resources
        provision_result = self._provision_rag_resources(workspace, default_config)
        if isinstance(provision_result, Failure):
            # Update status to failed
            self.data_access.update(workspace.id, status=WorkspaceStatus.FAILED.value)
            logger.error(f"Workspace provisioning failed: {provision_result.failure().message}")
            return Failure(provision_result.failure())

        # Update status to ready
        self.data_access.update(workspace.id, status=WorkspaceStatus.READY.value)
        logger.info(f"Workspace provisioned successfully: workspace_id={workspace.id}")

        # Reload workspace with updated status (data_access handles caching)
        reloaded_workspace = self.data_access.get_by_id(workspace.id)
        if not reloaded_workspace:
            return Failure(
                WorkflowError(
                    "Failed to reload workspace after provisioning", workflow="create_workspace"
                )
            )

        return Success(reloaded_workspace)

    def _provision_rag_resources(
        self, workspace: Workspace, default_config: DefaultRagConfig
    ) -> Result[None, WorkflowError]:
        """Provision RAG resources for a workspace with status tracking.

        Args:
            workspace: Workspace to provision resources for
            default_config: The default RAG configuration.

        Returns:
            Result with None on success or WorkflowError on failure
        """
        logger.info(f"Provisioning RAG resources for workspace {workspace.id}")

        # Update status based on RAG type
        if workspace.rag_type == "vector":
            self.data_access.update(
                workspace.id, status=WorkspaceStatus.CREATING_VECTOR_COLLECTION.value
            )
            logger.info(f"Workspace {workspace.id}: creating vector collection")
        elif workspace.rag_type == "graph":
            self.data_access.update(workspace.id, status=WorkspaceStatus.CREATING_GRAPH_STORE.value)
            logger.info(f"Workspace {workspace.id}: creating graph store")

        # Build configuration for workflow from defaults
        rag_config = {
            "rag_type": workspace.rag_type,
            "qdrant_url": f"http://{config.vector_store.qdrant_host}:{config.vector_store.qdrant_port}",
            "vector_size": default_config.vector_config.embedding_model_vector_size,
            "distance": default_config.vector_config.distance_metric,
        }

        # Create and execute provisioning workflow
        workflow = CreateResourcesWorkflowFactory.create(rag_config)
        result = workflow.execute(str(workspace.id))

        if isinstance(result, Failure):
            error = result.failure()
            return Failure(
                WorkflowError(
                    f"Provisioning workflow failed: {error.message}",
                    workflow="provision_rag_resources",
                )
            )

        logger.info(f"RAG resources provisioned for workspace {workspace.id}")
        return Success(None)

    def get_workspace(self, workspace_id: int) -> Optional[Workspace]:
        """Get workspace by ID with caching (handled by data access layer)."""
        return self.data_access.get_by_id(workspace_id)

    def list_workspaces(self) -> list[Workspace]:
        """List all workspace (single-user system)."""
        return self.data_access.get_all()

    def update_workspace(
        self, workspace_id: int, name: Optional[str], description: Optional[str]
    ) -> Result[Workspace, NotFoundError]:
        """Update workspace.

        Args:
            workspace_id: ID of workspace to update
            name: New name (validated, optional)
            description: New description (validated, optional)

        Returns:
            Result with Workspace model or NotFoundError
        """
        logger.info(f"Updating workspace {workspace_id}")

        updates = {}
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description

        success = self.data_access.update(workspace_id, **updates)
        if not success:
            return Failure(NotFoundError("workspace", workspace_id))

        # Reload workspace (data_access handles cache invalidation and refresh)
        updated = self.data_access.get_by_id(workspace_id)
        if not updated:
            return Failure(NotFoundError("workspace", workspace_id))

        return Success(updated)

    def delete_workspace(self, workspace_id: int) -> bool:
        """Delete workspace synchronously (single-user CLI system).

        Args:
            workspace_id: ID of the workspace to delete

        Returns:
            bool: True if deleted, False if workspace not found
        """
        logger.info(f"Deleting workspace: workspace_id={workspace_id}")

        # Get workspace
        workspace = self.data_access.get_by_id(workspace_id)
        if not workspace:
            logger.warning(
                f"Workspace deletion failed: workspace not found (workspace_id={workspace_id})"
            )
            return False

        # Deallocate RAG resources (log but don't fail on error)
        dealloc_result = self._deallocate_rag_resources(workspace)
        if isinstance(dealloc_result, Failure):
            logger.warning(
                f"Failed to deallocate workspace resources: {dealloc_result.failure().message}"
            )

        # Delete from database (data_access handles cache invalidation)
        return self.data_access.delete(workspace_id)

    def _deallocate_rag_resources(self, workspace: Workspace) -> Result[None, WorkflowError]:
        """Deallocate RAG resources for a workspace.

        Args:
            workspace: Workspace to deallocate resources for

        Returns:
            Result with None on success or WorkflowError on failure
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

        if isinstance(result, Failure):
            error = result.failure()
            return Failure(
                WorkflowError(
                    f"Deallocation workflow failed: {error.message}",
                    workflow="deallocate_rag_resources",
                )
            )

        logger.info(f"RAG resources deallocated for workspace {workspace.id}")
        return Success(None)
