"""Workspace service for business logic."""

from typing import Optional

from returns.result import Failure, Result, Success

from src.domains.default_rag_config.models import DefaultRagConfig
from src.domains.default_rag_config.service import DefaultRagConfigService
from src.domains.workspace.data_access import WorkspaceDataAccess
from src.domains.workspace.models import GraphRagConfig, VectorRagConfig, Workspace, WorkspaceStatus
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.rag_config_provider import RagConfigProviderFactory
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
        config_provider_factory: RagConfigProviderFactory,
    ):
        """Initialize service with data access and default config service.

        Args:
            data_access: Workspace data access layer (handles cache + repository)
            default_rag_config_service: Service for default RAG configuration
            config_provider_factory: Factory for RAG config providers
        """
        self.data_access = data_access
        self.default_rag_config_service = default_rag_config_service
        self.config_provider_factory = config_provider_factory

    def create_workspace(
        self,
        name: str,
        description: Optional[str],
        rag_type: str,
        # Vector RAG config (optional overrides)
        chunking_algorithm: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        embedding_algorithm: Optional[str] = None,
        top_k: Optional[int] = None,
        rerank_algorithm: Optional[str] = None,
        # Graph RAG config (optional overrides)
        entity_extraction_algorithm: Optional[str] = None,
        relationship_extraction_algorithm: Optional[str] = None,
        clustering_algorithm: Optional[str] = None,
    ) -> Result[Workspace, WorkflowError | DatabaseError]:
        """Create a new workspace.

        Args:
            name: Workspace name (validated)
            description: Optional description (validated)
            rag_type: RAG type (validated)
            chunking_algorithm: Optional override for chunking algorithm
            chunk_size: Optional override for chunk size
            chunk_overlap: Optional override for chunk overlap
            embedding_algorithm: Optional override for embedding algorithm
            top_k: Optional override for top K
            rerank_algorithm: Optional override for rerank algorithm
            entity_extraction_algorithm: Optional override for entity extraction
            relationship_extraction_algorithm: Optional override for relationship extraction
            clustering_algorithm: Optional override for clustering algorithm

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

        # Create config using custom values or defaults
        if workspace.rag_type == "vector":
            new_vector_config = VectorRagConfig(
                workspace_id=workspace.id,
                embedding_model_vector_size=default_config.vector_config.embedding_model_vector_size,
                distance_metric=default_config.vector_config.distance_metric,
                embedding_algorithm=embedding_algorithm
                or default_config.vector_config.embedding_algorithm,
                chunking_algorithm=chunking_algorithm
                or default_config.vector_config.chunking_algorithm,
                rerank_algorithm=rerank_algorithm or default_config.vector_config.rerank_algorithm,
                chunk_size=chunk_size or default_config.vector_config.chunk_size,
                chunk_overlap=chunk_overlap or default_config.vector_config.chunk_overlap,
                top_k=top_k or default_config.vector_config.top_k,
            )
            vector_config_result = self.data_access.repository.create_vector_rag_config(
                new_vector_config
            )
            if isinstance(vector_config_result, Failure):
                # Update status to failed and cleanup
                self.data_access.update(workspace.id, status=WorkspaceStatus.FAILED.value)
                logger.error(
                    f"Failed to create vector RAG config for workspace {workspace.id}: "
                    f"{vector_config_result.failure().message}"
                )
                return Failure(vector_config_result.failure())
        elif workspace.rag_type == "graph":
            new_graph_config = GraphRagConfig(
                workspace_id=workspace.id,
                entity_extraction_algorithm=entity_extraction_algorithm
                or default_config.graph_config.entity_extraction_algorithm,
                relationship_extraction_algorithm=relationship_extraction_algorithm
                or default_config.graph_config.relationship_extraction_algorithm,
                clustering_algorithm=clustering_algorithm
                or default_config.graph_config.clustering_algorithm,
                entity_types=default_config.graph_config.entity_types.copy(),
                relationship_types=default_config.graph_config.relationship_types.copy(),
                max_traversal_depth=default_config.graph_config.max_traversal_depth,
                top_k_entities=default_config.graph_config.top_k_entities,
                top_k_communities=default_config.graph_config.top_k_communities,
                include_entity_neighborhoods=default_config.graph_config.include_entity_neighborhoods,
                community_min_size=default_config.graph_config.community_min_size,
                clustering_resolution=default_config.graph_config.clustering_resolution,
                clustering_max_level=default_config.graph_config.clustering_max_level,
            )
            graph_config_result = self.data_access.repository.create_graph_rag_config(
                new_graph_config
            )
            if isinstance(graph_config_result, Failure):
                # Update status to failed and cleanup
                self.data_access.update(workspace.id, status=WorkspaceStatus.FAILED.value)
                logger.error(
                    f"Failed to create graph RAG config for workspace {workspace.id}: "
                    f"{graph_config_result.failure().message}"
                )
                return Failure(graph_config_result.failure())

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

        # Use provider pattern to build configuration
        provider = self.config_provider_factory.get_provider(workspace.rag_type)
        if not provider:
            return Failure(
                WorkflowError(
                    f"Unknown RAG type: {workspace.rag_type}",
                    workflow="provision_rag_resources",
                )
            )

        rag_config = provider.build_provisioning_settings(workspace.id)

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

        # Use provider pattern to build configuration
        provider = self.config_provider_factory.get_provider(workspace.rag_type)
        if not provider:
            return Failure(
                WorkflowError(
                    f"Unknown RAG type: {workspace.rag_type}",
                    workflow="deallocate_rag_resources",
                )
            )

        rag_config = provider.build_provisioning_settings(workspace.id)

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

    def update_workspace_vector_rag_config(
        self, config: VectorRagConfig
    ) -> Result[VectorRagConfig, DatabaseError]:
        """
        Update vector RAG configuration for a workspace.

        Args:
            config: Updated vector RAG configuration

        Returns:
            Result with updated config or DatabaseError
        """
        return self.data_access.update_vector_rag_config(config)

    def update_workspace_graph_rag_config(
        self, config: GraphRagConfig
    ) -> Result[GraphRagConfig, DatabaseError]:
        """
        Update graph RAG configuration for a workspace.

        Args:
            config: Updated graph RAG configuration

        Returns:
            Result with updated config or DatabaseError
        """
        return self.data_access.update_graph_rag_config(config)

    def delete_workspace_rag_config(self, workspace_id: int, rag_type: str) -> bool:
        """
        Delete RAG configuration for a workspace.

        Args:
            workspace_id: Workspace ID
            rag_type: Type of RAG config to delete ("vector" or "graph")

        Returns:
            True if deleted successfully, False otherwise
        """
        if rag_type == "vector":
            return self.data_access.delete_vector_rag_config(workspace_id)
        elif rag_type == "graph":
            return self.data_access.delete_graph_rag_config(workspace_id)
        else:
            logger.error(f"Invalid RAG type: {rag_type}")
            return False
