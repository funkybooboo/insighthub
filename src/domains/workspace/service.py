"""Workspace service for business logic."""

import json
from typing import Optional

from returns.result import Failure, Result, Success

from src.config import config
from src.infrastructure.cache.cache import Cache
from src.infrastructure.logger import create_logger
from src.infrastructure.models import Workspace
from src.infrastructure.rag.options import get_valid_rag_types, is_valid_rag_type
from src.infrastructure.rag.workflows.create_resources import CreateResourcesWorkflowFactory
from src.infrastructure.rag.workflows.remove_resources import RemoveResourcesWorkflowFactory
from src.infrastructure.repositories import WorkspaceRepository
from src.infrastructure.types import DatabaseError, NotFoundError, ValidationError, WorkflowError

logger = create_logger(__name__)


class WorkspaceService:
    """Service for workspace-related business logic."""

    def __init__(self, repository: WorkspaceRepository, cache: Optional[Cache] = None):
        """Initialize service with repository and cache."""
        self.repository = repository
        self.cache = cache

    def create_workspace(
        self,
        name: str,
        description: str | None = None,
        rag_type: str = "vector",
    ) -> Result[Workspace, ValidationError | WorkflowError | DatabaseError]:
        """Create a new workspace synchronously (single-user CLI system)."""
        logger.info(f"Creating workspace: name='{name}', rag_type='{rag_type}'")

        # Validate inputs
        if not name or not name.strip():
            logger.error("Workspace creation failed: empty name")
            return Failure(ValidationError("Workspace name cannot be empty", field="name"))

        if len(name.strip()) > 255:
            logger.error(f"Workspace creation failed: name too long '{name[:50]}...'")
            return Failure(
                ValidationError("Workspace name too long (max 255 characters)", field="name")
            )

        if description and len(description) > 1000:
            logger.error("Workspace creation failed: description too long")
            return Failure(
                ValidationError(
                    "Workspace description too long (max 1000 characters)", field="description"
                )
            )

        if not is_valid_rag_type(rag_type):
            valid_types = get_valid_rag_types()
            logger.error(f"Workspace creation failed: invalid rag_type '{rag_type}'")
            return Failure(
                ValidationError(
                    f"Invalid rag_type. Must be one of: {', '.join(valid_types)}", field="rag_type"
                )
            )

        # Create workspace in database (status will be 'ready' after provisioning)
        create_result = self.repository.create(
            name.strip(), description, rag_type, status="provisioning"
        )
        if isinstance(create_result, Failure):
            return Failure(create_result.failure())

        workspace = create_result.unwrap()
        logger.info(f"Workspace created in database: workspace_id={workspace.id}")

        # Provision RAG resources
        provision_result = self._provision_rag_resources(workspace)
        if isinstance(provision_result, Failure):
            # Update status to failed
            self.repository.update(workspace.id, status="failed")
            logger.error(f"Workspace provisioning failed: {provision_result.failure().message}")
            return Failure(provision_result.failure())

        # Update status to ready
        self.repository.update(workspace.id, status="ready")
        logger.info(f"Workspace provisioned successfully: workspace_id={workspace.id}")

        # Reload workspace with updated status
        reloaded_workspace = self.repository.get_by_id(workspace.id)
        if not reloaded_workspace:
            return Failure(
                WorkflowError(
                    "Failed to reload workspace after provisioning", workflow="create_workspace"
                )
            )

        # Cache the workspace
        if self.cache:
            self._cache_workspace(reloaded_workspace)

        return Success(reloaded_workspace)

    def _provision_rag_resources(self, workspace: Workspace) -> Result[None, WorkflowError]:
        """Provision RAG resources for a workspace.

        Args:
            workspace: Workspace to provision resources for

        Returns:
            Result with None on success or WorkflowError on failure
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

    def get_workspace(self, workspace_id: int) -> Workspace | None:
        """Get workspace by ID with caching."""
        # Try cache first
        if self.cache:
            cached = self._get_cached_workspace(workspace_id)
            if cached:
                logger.debug(f"Cache hit for workspace {workspace_id}")
                return cached

        # Cache miss, fetch from database
        workspace = self.repository.get_by_id(workspace_id)
        if workspace and self.cache:
            self._cache_workspace(workspace)

        return workspace

    def list_workspaces(self) -> list[Workspace]:
        """List all workspace (single-user system)."""
        return self.repository.get_all()

    def update_workspace(
        self, workspace_id: int, name: str | None = None, description: str | None = None
    ) -> Result[Workspace, ValidationError | NotFoundError]:
        """Update workspace name and/or description."""
        logger.info(f"Updating workspace {workspace_id}")

        # Validate inputs
        if name is not None:
            if not name.strip():
                return Failure(ValidationError("Workspace name cannot be empty", field="name"))
            if len(name.strip()) > 255:
                return Failure(
                    ValidationError("Workspace name too long (max 255 characters)", field="name")
                )

        if description is not None and len(description) > 1000:
            return Failure(
                ValidationError(
                    "Workspace description too long (max 1000 characters)", field="description"
                )
            )

        updates = {}
        if name is not None:
            updates["name"] = name.strip()
        if description is not None:
            updates["description"] = description

        updated = self.repository.update(workspace_id, **updates)
        if not updated:
            return Failure(NotFoundError("workspace", workspace_id))

        # Invalidate cache
        if self.cache:
            self._invalidate_workspace_cache(workspace_id)
            self._cache_workspace(updated)

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
        workspace = self.repository.get_by_id(workspace_id)
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

        # Delete from database
        self.repository.delete(workspace_id)
        logger.info(f"Workspace deleted: workspace_id={workspace_id}")

        # Invalidate cache
        if self.cache:
            self._invalidate_workspace_cache(workspace_id)

        return True

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

    def _cache_workspace(self, workspace: Workspace) -> None:
        """Cache a workspace object."""
        if not self.cache:
            return
        key = f"workspace:{workspace.id}"
        value = json.dumps({
            "id": workspace.id,
            "name": workspace.name,
            "description": workspace.description,
            "rag_type": workspace.rag_type,
            "status": workspace.status,
            "created_at": workspace.created_at.isoformat(),
            "updated_at": workspace.updated_at.isoformat(),
        })
        self.cache.set(key, value, ttl=300)  # Cache for 5 minutes

    def _get_cached_workspace(self, workspace_id: int) -> Workspace | None:
        """Get workspace from cache."""
        if not self.cache:
            return None
        key = f"workspace:{workspace_id}"
        cached = self.cache.get(key)
        if not cached:
            return None
        try:
            from datetime import datetime
            data = json.loads(cached)
            return Workspace(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                rag_type=data["rag_type"],
                status=data["status"],
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def _invalidate_workspace_cache(self, workspace_id: int) -> None:
        """Invalidate workspace cache."""
        if not self.cache:
            return
        key = f"workspace:{workspace_id}"
        self.cache.delete(key)
