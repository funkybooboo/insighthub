"""Workspace service for business logic."""

from src.infrastructure.models import GraphRagConfig, RagConfig, VectorRagConfig, Workspace
from src.infrastructure.repositories.workspaces import WorkspaceRepository


class WorkspaceService:
    """Service for workspace-related business logic."""

    def __init__(self, repository: WorkspaceRepository):
        """Initialize service with repository."""
        self.repository = repository

    def create_workspace(
        self,
        user_id: int,
        name: str,
        description: str | None = None,
        rag_type: str = "vector",
        rag_config: dict[str, str | int | float | bool] | None = None,
    ) -> Workspace:
        """Create a new workspace with optional RAG configuration."""
        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Workspace name cannot be empty")

        if len(name.strip()) > 255:
            raise ValueError("Workspace name too long (max 255 characters)")

        if description and len(description) > 1000:
            raise ValueError("Workspace description too long (max 1000 characters)")

        if rag_type not in ["vector", "graph"]:
            raise ValueError("Invalid rag_type. Must be 'vector' or 'graph'")

        # Validate RAG config if provided
        if rag_config:
            self._validate_rag_config(rag_type, rag_config)

        # TODO: Launch WorkspaceProvisionWorker
        # Worker should:
        # 1. Create workspace in database with status='provisioning'
        # 2. Create Qdrant collection (if vector RAG) or Neo4j database (if graph RAG)
        # 3. Initialize default RAG configs
        # 4. Set up permissions/quotas
        # 5. Update status to 'ready'
        # 6. Broadcast status updates via WebSocket
        #
        # Example implementation:
        #    workspace = self.repository.create(user_id, name.strip(), description, rag_type, rag_config, status='provisioning')
        #    from src.workers import get_workspace_provision_worker
        #    provision_worker = get_workspace_provision_worker()
        #    provision_worker.start_provisioning(workspace, user_id)
        #    return workspace  # Returns immediately with status='provisioning'
        #
        # For now, creating workspace synchronously:
        return self.repository.create(user_id, name.strip(), description, rag_type, rag_config)

    def get_workspace(self, workspace_id: int) -> Workspace | None:
        """Get workspace by ID."""
        workspace = self.repository.get_by_id(workspace_id)
        return workspace

    def list_user_workspaces(self, user_id: int) -> list[Workspace]:
        """List all workspaces for a users."""
        return self.repository.get_by_user(user_id)

    def update_workspace(
        self, workspace_id: int, name: str | None = None, description: str | None = None
    ) -> Workspace | None:
        """Update workspace."""
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
        """Delete workspace."""

        # TODO: Launch WorkspaceCleanupWorker
        # Worker should:
        # 1. Update workspace status to 'deleting'
        # 2. Delete all documents in workspace (calls DocumentCleanupWorker for each)
        # 3. Delete Qdrant collection (if vector RAG) or Neo4j database (if graph RAG)
        # 4. Remove permissions/quotas
        # 5. Delete workspace from database
        # 6. Broadcast completion status via WebSocket
        #
        # Example implementation:
        #    workspace = self.repository.get_by_id(workspace_id)
        #    if not workspace:
        #        return False
        #    self.repository.update(workspace_id, status='deleting')
        #    from src.workers import get_workspace_cleanup_worker
        #    cleanup_worker = get_workspace_cleanup_worker()
        #    cleanup_worker.start_cleanup(workspace, user_id)
        #    return True  # Returns immediately, deletion happens in background
        #
        # For now, deleting workspace synchronously:
        return self.repository.delete(workspace_id)

    def get_rag_config(self, workspace_id: int) -> RagConfig | None:
        """Get RAG configuration for a workspace."""
        workspace = self.repository.get_by_id(workspace_id)
        if not workspace:
            return None

        # Check if we have a stored config
        stored_config = self.repository.get_rag_config(workspace_id)
        if stored_config:
            return stored_config

        # Return default config based on workspace rag_type
        if workspace.rag_type == "vector":
            config: dict[str, str | int | float | bool] = {
                "embedding_algorithm": "ollama",
                "chunking_algorithm": "sentence",
                "rerank_algorithm": "none",
                "chunk_size": 1000,
                "chunk_overlap": 200,
                "top_k": 5,
            }
        elif workspace.rag_type == "graph":
            config: dict[str, str | int | float | bool] = {
                "entity_extraction_algorithm": "spacy",
                "relationship_extraction_algorithm": "dependency-parsing",
                "clustering_algorithm": "leiden",
            }
        else:
            config = {}

        return RagConfig(
            workspace_id=workspace_id,
            rag_type=workspace.rag_type,
            config=config,
        )

    def get_vector_rag_config(self, workspace_id: int) -> VectorRagConfig | None:
        """Get vector RAG configuration for a workspace."""
        workspace = self.repository.get_by_id(workspace_id)
        if not workspace or workspace.rag_type != "vector":
            return None

        # Check if we have a stored config
        stored_config = self.repository.get_vector_rag_config(workspace_id)
        if stored_config:
            return stored_config

        # Return default config
        return VectorRagConfig(workspace_id=workspace_id)

    def get_graph_rag_config(self, workspace_id: int) -> GraphRagConfig | None:
        """Get graph RAG configuration for a workspace."""
        workspace = self.repository.get_by_id(workspace_id)
        if not workspace or workspace.rag_type != "graph":
            return None

        # Check if we have a stored config
        stored_config = self.repository.get_graph_rag_config(workspace_id)
        if stored_config:
            return stored_config

        # Return default config
        return GraphRagConfig(workspace_id=workspace_id)

    def _validate_rag_config(
        self, rag_type: str, config: dict[str, str | int | float | bool]
    ) -> None:
        """Validate RAG configuration."""
        if rag_type == "vector":
            required_fields = [
                "embedding_algorithm",
                "chunking_algorithm",
                "rerank_algorithm",
                "chunk_size",
                "chunk_overlap",
                "top_k",
            ]
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field '{field}' for vector RAG config")

            # Validate types
            if not isinstance(config["chunk_size"], int) or config["chunk_size"] <= 0:
                raise ValueError("chunk_size must be a positive integer")

            if not isinstance(config["chunk_overlap"], int) or config["chunk_overlap"] < 0:
                raise ValueError("chunk_overlap must be a non-negative integer")

            if not isinstance(config["top_k"], int) or config["top_k"] <= 0:
                raise ValueError("top_k must be a positive integer")

        elif rag_type == "graph":
            required_fields = [
                "entity_extraction_algorithm",
                "relationship_extraction_algorithm",
                "clustering_algorithm",
            ]
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Missing required field '{field}' for graph RAG config")

        # Validate string fields are not empty
        for key, value in config.items():
            if isinstance(value, str) and not value.strip():
                raise ValueError(f"Field '{key}' cannot be empty")

    def validate_workspace_access(self, workspace_id: int, user_id: int) -> bool:
        """Validate that users has access to workspace."""
        workspace = self.repository.get_by_id(workspace_id)
        return workspace is not None and workspace.user_id == user_id

    def get_user_workspace(self, workspace_id: int, user_id: int) -> Workspace | None:
        """Get workspace by ID for specific users."""
        workspace = self.repository.get_by_id(workspace_id)
        if workspace and workspace.user_id == user_id:
            return workspace
        return None
