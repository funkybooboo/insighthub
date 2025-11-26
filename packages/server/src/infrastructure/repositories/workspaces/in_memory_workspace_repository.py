"""In-memory implementation of WorkspaceRepository."""

from datetime import datetime
from typing import Optional

from src.infrastructure.models import GraphRagConfig, RagConfig, VectorRagConfig, Workspace

from .workspace_repository import WorkspaceRepository


class InMemoryWorkspaceRepository(WorkspaceRepository):
    """In-memory implementation of WorkspaceRepository for development/testing."""

    def __init__(self):
        """Initialize the repository."""
        self._workspaces: dict[int, Workspace] = {}
        self.vector_rag_configs: dict[int, VectorRagConfig] = {}
        self.graph_rag_configs: dict[int, GraphRagConfig] = {}
        # Keep for backward compatibility
        self.rag_configs: dict[int, RagConfig] = {}
        self._next_id = 1

    def create(
        self,
        user_id: int,
        name: str,
        description: str | None = None,
        rag_type: str = "vector",
        rag_config: dict | None = None,
        status: str = "ready",
    ) -> Workspace:
        """Create a new workspace."""
        workspace = Workspace(
            id=self._next_id,
            user_id=user_id,
            name=name,
            description=description,
            rag_type=rag_type,
            status=status,
        )
        self._workspaces[self._next_id] = workspace

        # Store RAG config if provided
        if rag_config:
            if rag_type == "vector":
                vector_config = VectorRagConfig(workspace_id=self._next_id, **rag_config)
                self.vector_rag_configs[self._next_id] = vector_config
            elif rag_type == "graph":
                graph_config = GraphRagConfig(workspace_id=self._next_id, **rag_config)
                self.graph_rag_configs[self._next_id] = graph_config

            # Also store in generic rag_configs for backward compatibility
            rag_config_obj = RagConfig(
                workspace_id=self._next_id,
                rag_type=rag_type,
                config=rag_config,
            )
            self.rag_configs[self._next_id] = rag_config_obj

        self._next_id += 1
        return workspace

    def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        """Get workspace by ID."""
        return self._workspaces.get(workspace_id)

    def get_by_user(self, user_id: int) -> list[Workspace]:
        """Get all workspaces for a users."""
        return [w for w in self._workspaces.values() if w.user_id == user_id]

    def update(self, workspace_id: int, **kwargs) -> Optional[Workspace]:
        """Update workspace fields."""
        workspace = self._workspaces.get(workspace_id)
        if not workspace:
            return None

        for key, value in kwargs.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)

        workspace.updated_at = datetime.utcnow()
        return workspace

    def delete(self, workspace_id: int) -> bool:
        """Delete workspace by ID."""
        if workspace_id in self._workspaces:
            del self._workspaces[workspace_id]
            # Also clean up RAG configs
            self.vector_rag_configs.pop(workspace_id, None)
            self.graph_rag_configs.pop(workspace_id, None)
            self.rag_configs.pop(workspace_id, None)
            return True
        return False

    def get_vector_rag_config(self, workspace_id: int) -> Optional[VectorRagConfig]:
        """Get vector RAG config for workspace."""
        return self.vector_rag_configs.get(workspace_id)

    def get_graph_rag_config(self, workspace_id: int) -> Optional[GraphRagConfig]:
        """Get graph RAG config for workspace."""
        return self.graph_rag_configs.get(workspace_id)

    def get_rag_config(self, workspace_id: int) -> Optional[RagConfig]:
        """Get generic RAG config for workspace."""
        return self.rag_configs.get(workspace_id)
