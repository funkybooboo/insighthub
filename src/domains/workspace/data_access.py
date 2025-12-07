"""Workspace data access layer - coordinates cache and repository."""

import json
from datetime import UTC, datetime
from typing import Optional

from returns.result import Failure, Result

from src.cache_keys import CacheKeys
from src.domains.workspace.models import GraphRagConfig, VectorRagConfig, Workspace
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

    def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        """Get workspace by ID with caching.

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace if found, None otherwise
        """
        # Try cache first
        cache_key = CacheKeys.workspace(workspace_id)
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
        """Get all workspaces with caching.

        Returns:
            List of all workspaces
        """
        # Try cache first
        cache_key = CacheKeys.workspaces_all()
        cached_json = self.cache.get(cache_key) if self.cache else None

        if cached_json:
            cached_workspaces = self._try_get_cached_workspaces(cache_key, cached_json)
            if cached_workspaces is not None:
                return cached_workspaces

        # Cache miss - fetch from database
        workspaces = self.repository.get_all()

        # Cache the result
        if self.cache and workspaces:
            cache_value = json.dumps([ws.id for ws in workspaces])
            self.cache.set(cache_key, cache_value, ttl=180)  # Cache for 3 minutes
            # Also cache individual workspaces
            for ws in workspaces:
                self._cache_workspace(ws)

        return workspaces

    def _try_get_cached_workspaces(
        self, cache_key: str, cached_json: str
    ) -> Optional[list[Workspace]]:
        """Try to retrieve workspaces from cache.

        Returns:
            List of workspaces if all found, None if any missing or invalid
        """
        try:
            workspace_ids = json.loads(cached_json)
            workspaces = []
            for ws_id in workspace_ids:
                ws = self.get_by_id(ws_id)
                if not ws:
                    if self.cache:
                        self.cache.delete(cache_key)
                    return None
                workspaces.append(ws)
            return workspaces
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

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
            kwargs["name"] = name
        if description is not None:
            kwargs["description"] = description
        if status is not None:
            kwargs["status"] = status

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

        cache_key = CacheKeys.workspace(workspace.id)
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
            cache_key = CacheKeys.workspace(workspace_id)
            self.cache.delete(cache_key)
            # Also invalidate the all workspaces list cache
            self.cache.delete(CacheKeys.workspaces_all())
            # Invalidate RAG configs as well
            self.cache.delete(CacheKeys.workspace_vector_config(workspace_id))
            self.cache.delete(CacheKeys.workspace_graph_config(workspace_id))

    def get_vector_rag_config(self, workspace_id: int) -> Optional[VectorRagConfig]:
        """Get vector RAG config for workspace with caching.

        Args:
            workspace_id: Workspace ID

        Returns:
            VectorRagConfig if found, None otherwise
        """
        # Try cache first
        cache_key = CacheKeys.workspace_vector_config(workspace_id)
        cached_json = self.cache.get(cache_key) if self.cache else None

        if cached_json:
            try:
                data = json.loads(cached_json)
                return VectorRagConfig(
                    workspace_id=data["workspace_id"],
                    embedding_model_vector_size=data.get("embedding_model_vector_size", 384),
                    distance_metric=data.get("distance_metric", "cosine"),
                    embedding_algorithm=data["embedding_algorithm"],
                    chunking_algorithm=data["chunking_algorithm"],
                    rerank_algorithm=data["rerank_algorithm"],
                    chunk_size=data["chunk_size"],
                    chunk_overlap=data["chunk_overlap"],
                    top_k=data["top_k"],
                    created_at=(
                        datetime.fromisoformat(data["created_at"])
                        if data.get("created_at")
                        else datetime.now(UTC)
                    ),
                    updated_at=(
                        datetime.fromisoformat(data["updated_at"])
                        if data.get("updated_at")
                        else datetime.now(UTC)
                    ),
                )
            except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                logger.warning(
                    f"Cache deserialization error for vector RAG config {workspace_id}: {e}"
                )

        # Cache miss - fetch from database
        config = self.repository.get_vector_rag_config(workspace_id)

        if config and self.cache:
            self._cache_vector_rag_config(workspace_id, config)

        return config

    def get_graph_rag_config(self, workspace_id: int) -> Optional[GraphRagConfig]:
        """Get graph RAG config for workspace with caching.

        Args:
            workspace_id: Workspace ID

        Returns:
            GraphRagConfig if found, None otherwise
        """
        # Try cache first
        cache_key = CacheKeys.workspace_graph_config(workspace_id)
        cached_json = self.cache.get(cache_key) if self.cache else None

        if cached_json:
            try:
                data = json.loads(cached_json)
                return GraphRagConfig(
                    workspace_id=data["workspace_id"],
                    entity_extraction_algorithm=data["entity_extraction_algorithm"],
                    relationship_extraction_algorithm=data["relationship_extraction_algorithm"],
                    clustering_algorithm=data["clustering_algorithm"],
                    created_at=(
                        datetime.fromisoformat(data["created_at"])
                        if data.get("created_at")
                        else datetime.now(UTC)
                    ),
                    updated_at=(
                        datetime.fromisoformat(data["updated_at"])
                        if data.get("updated_at")
                        else datetime.now(UTC)
                    ),
                )
            except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                logger.warning(
                    f"Cache deserialization error for graph RAG config {workspace_id}: {e}"
                )

        # Cache miss - fetch from database
        config = self.repository.get_graph_rag_config(workspace_id)

        if config and self.cache:
            self._cache_graph_rag_config(workspace_id, config)

        return config

    def _cache_vector_rag_config(self, workspace_id: int, config: VectorRagConfig) -> None:
        """Cache vector RAG config.

        Args:
            workspace_id: Workspace ID
            config: VectorRagConfig to cache
        """
        if not self.cache:
            return

        cache_key = CacheKeys.workspace_vector_config(workspace_id)
        cache_value = json.dumps(
            {
                "workspace_id": config.workspace_id,
                "embedding_model_vector_size": config.embedding_model_vector_size,
                "distance_metric": config.distance_metric,
                "embedding_algorithm": config.embedding_algorithm,
                "chunking_algorithm": config.chunking_algorithm,
                "rerank_algorithm": config.rerank_algorithm,
                "chunk_size": config.chunk_size,
                "chunk_overlap": config.chunk_overlap,
                "top_k": config.top_k,
                "created_at": config.created_at.isoformat() if config.created_at else None,
                "updated_at": config.updated_at.isoformat() if config.updated_at else None,
            }
        )
        self.cache.set(
            cache_key, cache_value, ttl=600
        )  # Cache for 10 minutes (configs change less frequently)

    def _cache_graph_rag_config(self, workspace_id: int, config: GraphRagConfig) -> None:
        """Cache graph RAG config.

        Args:
            workspace_id: Workspace ID
            config: GraphRagConfig to cache
        """
        # TODO: Add missing fields to cache serialization (added in migration 008):
        #       entity_types, relationship_types, max_traversal_depth, top_k_entities,
        #       top_k_communities, include_entity_neighborhoods, community_min_size,
        #       clustering_resolution, clustering_max_level
        # TODO: Update corresponding deserialization in get_graph_rag_config method
        if not self.cache:
            return

        cache_key = CacheKeys.workspace_graph_config(workspace_id)
        cache_value = json.dumps(
            {
                "workspace_id": config.workspace_id,
                "entity_extraction_algorithm": config.entity_extraction_algorithm,
                "relationship_extraction_algorithm": config.relationship_extraction_algorithm,
                "clustering_algorithm": config.clustering_algorithm,
                "created_at": config.created_at.isoformat() if config.created_at else None,
                "updated_at": config.updated_at.isoformat() if config.updated_at else None,
            }
        )
        self.cache.set(
            cache_key, cache_value, ttl=600
        )  # Cache for 10 minutes (configs change less frequently)
