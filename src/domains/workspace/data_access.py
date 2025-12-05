"""Workspace data access layer - coordinates cache and repository."""

import json
from datetime import datetime
from typing import Optional

from returns.result import Failure, Result

from src.domains.workspace.models import Workspace
from src.domains.workspace.repositories import WorkspaceRepository
from src.infrastructure.cache.cache import Cache
from src.infrastructure.logger import create_logger
from src.infrastructure.types import DatabaseError

logger = create_logger(__name__)


class WorkspaceDataAccess:
    """Data access layer for Workspace - handles caching + persistence."""

    def __init__(self, repository: WorkspaceRepository, cache: Optional[Cache] = None):
        """Initialize data access layer.

        Args:
            repository: Workspace repository for database operations
            cache: Optional cache for performance optimization
        """
        self.repository = repository  # Exposed for operations not handled by this layer
        self.cache = cache

    def get_by_id(self, workspace_id: int) -> Workspace | None:
        """Get workspace by ID with caching.

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace if found, None otherwise
        """
        # Try cache first
        cache_key = f"workspace:{workspace_id}"
        cached_json = self.cache.get(cache_key) if self.cache else None

        if cached_json:
            try:
                data = json.loads(cached_json)
                return Workspace(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    rag_type=data["rag_type"],
                    status=data["status"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    updated_at=datetime.fromisoformat(data["updated_at"]),
                )
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Cache deserialization error for workspace {workspace_id}: {e}")

        # Cache miss - fetch from database
        workspace = self.repository.get_by_id(workspace_id)

        if workspace and self.cache:
            self._cache_workspace(workspace)

        return workspace

    def get_all(self) -> list[Workspace]:
        """Get all workspaces.

        Returns:
            List of all workspaces
        """
        return self.repository.get_all()

    def create(
        self, name: str, description: Optional[str], rag_type: str, status: str = "provisioning"
    ) -> Result[Workspace, DatabaseError]:
        """Create a new workspace.

        Args:
            name: Workspace name
            description: Optional description
            rag_type: RAG type
            status: Initial status

        Returns:
            Result with created workspace or database error
        """
        result = self.repository.create(name, description, rag_type, status)
        if isinstance(result, Failure):
            return result

        workspace = result.unwrap()
        if self.cache:
            self._cache_workspace(workspace)
        return result

    def update(
        self,
        workspace_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None,
    ) -> bool:
        """Update workspace.

        Args:
            workspace_id: Workspace ID
            name: Optional new name
            description: Optional new description
            status: Optional new status

        Returns:
            True if updated successfully
        """
        # Build kwargs dict for only non-None values
        kwargs = {}
        if name is not None:
            kwargs['name'] = name
        if description is not None:
            kwargs['description'] = description
        if status is not None:
            kwargs['status'] = status

        result = self.repository.update(workspace_id, **kwargs)
        if result:
            self._invalidate_cache(workspace_id)
            return True
        return False

    def delete(self, workspace_id: int) -> bool:
        """Delete workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            True if deleted successfully
        """
        result = self.repository.delete(workspace_id)
        if result:
            self._invalidate_cache(workspace_id)
        return result

    def _cache_workspace(self, workspace: Workspace) -> None:
        """Cache workspace data.

        Args:
            workspace: Workspace to cache
        """
        if not self.cache:
            return

        cache_key = f"workspace:{workspace.id}"
        cache_value = json.dumps(
            {
                "id": workspace.id,
                "name": workspace.name,
                "description": workspace.description,
                "rag_type": workspace.rag_type,
                "status": workspace.status,
                "created_at": workspace.created_at.isoformat(),
                "updated_at": workspace.updated_at.isoformat(),
            }
        )
        self.cache.set(cache_key, cache_value, ttl=300)  # Cache for 5 minutes

    def _invalidate_cache(self, workspace_id: int) -> None:
        """Invalidate workspace cache.

        Args:
            workspace_id: Workspace ID to invalidate
        """
        if self.cache:
            cache_key = f"workspace:{workspace_id}"
            self.cache.delete(cache_key)
