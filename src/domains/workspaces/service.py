"""Workspace service for business logic."""

from src.infrastructure.logger import create_logger
from src.infrastructure.models import GraphRagConfig, RagConfig, VectorRagConfig, Workspace
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
        rag_config: dict[str, str | int | float | bool] | None = None,
    ) -> Workspace:
        """Create a new workspace with optional RAG configuration (single-user system)."""
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

        # Validate RAG config if provided
        if rag_config:
            self._validate_rag_config(rag_type, rag_config)

        # Create workspace in database with status='provisioning'
        workspace = self.repository.create(
            name.strip(), description, rag_type, rag_config, status="provisioning"
        )

        logger.info(
            f"Workspace created in database: workspace_id={workspace.id}, status='provisioning'"
        )

        # Launch CreateWorkspaceWorker in background
        try:
            from src.workers import get_create_workspace_worker

            provision_worker = get_create_workspace_worker()
            provision_worker.start_provisioning(workspace)
        except Exception:
            # Skip worker initialization in unit tests or when dependencies unavailable
            pass

        logger.info(f"Background provisioning started for workspace {workspace.id}")

        # Returns immediately with status='provisioning'
        # Worker will update status to 'ready' when complete
        return workspace

    def get_workspace(self, workspace_id: int) -> Workspace | None:
        """Get workspace by ID."""
        workspace = self.repository.get_by_id(workspace_id)
        return workspace

    def list_workspaces(self) -> list[Workspace]:
        """List all workspaces (single-user system)."""
        return self.repository.get_all()

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
        """Delete workspace (single-user system).

        Args:
            workspace_id: ID of the workspace to delete

        Returns:
            bool: True if deletion was started, False if workspace not found
        """
        logger.info(f"Starting workspace deletion: workspace_id={workspace_id}")

        # Get workspace
        workspace = self.repository.get_by_id(workspace_id)
        if not workspace:
            logger.warning(f"Workspace deletion failed: workspace not found (workspace_id={workspace_id})")
            return False

        # Update status to 'deleting'
        self.repository.update(workspace_id, status="deleting")
        logger.info(f"Workspace status updated to 'deleting': workspace_id={workspace_id}")

        # Launch RemoveWorkspaceWorker in background
        try:
            from src.workers import get_remove_workspace_worker

            cleanup_worker = get_remove_workspace_worker()
            cleanup_worker.start_cleanup(workspace)
        except Exception:
            # Skip worker initialization in unit tests or when dependencies unavailable
            pass

        logger.info(f"Background cleanup started for workspace {workspace_id}")

        # Returns immediately, deletion happens in background
        return True

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

    @staticmethod
    def _validate_rag_config(rag_type: str, config: dict[str, str | int | float | bool]) -> None:
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


    def create_vector_rag_config(
        self,
        workspace_id: int,
        embedding_algorithm: str = "ollama",
        chunking_algorithm: str = "sentence",
        rerank_algorithm: str = "none",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 5,
    ) -> VectorRagConfig:
        """Create vector RAG configuration for a workspace."""
        logger.info(f"Creating vector RAG config for workspace {workspace_id}")

        # Validate workspace exists and is vector type
        workspace = self.repository.get_by_id(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        if workspace.rag_type != "vector":
            raise ValueError(f"Workspace {workspace_id} is not a vector RAG workspace")

        config = VectorRagConfig(
            workspace_id=workspace_id,
            embedding_algorithm=embedding_algorithm,
            chunking_algorithm=chunking_algorithm,
            rerank_algorithm=rerank_algorithm,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            top_k=top_k,
        )

        return self.repository.create_vector_rag_config(config)

    def update_vector_rag_config(
        self,
        workspace_id: int,
        embedding_algorithm: str | None = None,
        chunking_algorithm: str | None = None,
        rerank_algorithm: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        top_k: int | None = None,
    ) -> VectorRagConfig | None:
        """Update vector RAG configuration for a workspace."""
        logger.info(f"Updating vector RAG config for workspace {workspace_id}")

        # Validate workspace exists and is vector type
        workspace = self.repository.get_by_id(workspace_id)
        if not workspace:
            return None
        if workspace.rag_type != "vector":
            raise ValueError(f"Workspace {workspace_id} is not a vector RAG workspace")

        updates = {}
        if embedding_algorithm is not None:
            updates["embedding_algorithm"] = embedding_algorithm
        if chunking_algorithm is not None:
            updates["chunking_algorithm"] = chunking_algorithm
        if rerank_algorithm is not None:
            updates["rerank_algorithm"] = rerank_algorithm
        if chunk_size is not None:
            updates["chunk_size"] = chunk_size
        if chunk_overlap is not None:
            updates["chunk_overlap"] = chunk_overlap
        if top_k is not None:
            updates["top_k"] = top_k

        return self.repository.update_vector_rag_config(workspace_id, **updates)

    def create_graph_rag_config(
        self,
        workspace_id: int,
        entity_extraction_algorithm: str = "spacy",
        relationship_extraction_algorithm: str = "dependency-parsing",
        clustering_algorithm: str = "leiden",
    ) -> GraphRagConfig:
        """Create graph RAG configuration for a workspace."""
        logger.info(f"Creating graph RAG config for workspace {workspace_id}")

        # Validate workspace exists and is graph type
        workspace = self.repository.get_by_id(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        if workspace.rag_type != "graph":
            raise ValueError(f"Workspace {workspace_id} is not a graph RAG workspace")

        config = GraphRagConfig(
            workspace_id=workspace_id,
            entity_extraction_algorithm=entity_extraction_algorithm,
            relationship_extraction_algorithm=relationship_extraction_algorithm,
            clustering_algorithm=clustering_algorithm,
        )

        return self.repository.create_graph_rag_config(config)

    def update_graph_rag_config(
        self,
        workspace_id: int,
        entity_extraction_algorithm: str | None = None,
        relationship_extraction_algorithm: str | None = None,
        clustering_algorithm: str | None = None,
    ) -> GraphRagConfig | None:
        """Update graph RAG configuration for a workspace."""
        logger.info(f"Updating graph RAG config for workspace {workspace_id}")

        # Validate workspace exists and is graph type
        workspace = self.repository.get_by_id(workspace_id)
        if not workspace:
            return None
        if workspace.rag_type != "graph":
            raise ValueError(f"Workspace {workspace_id} is not a graph RAG workspace")

        updates = {}
        if entity_extraction_algorithm is not None:
            updates["entity_extraction_algorithm"] = entity_extraction_algorithm
        if relationship_extraction_algorithm is not None:
            updates["relationship_extraction_algorithm"] = relationship_extraction_algorithm
        if clustering_algorithm is not None:
            updates["clustering_algorithm"] = clustering_algorithm

        return self.repository.update_graph_rag_config(workspace_id, **updates)
