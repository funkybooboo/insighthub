"""Workspace repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.infrastructure.models import GraphRagConfig, RagConfig, VectorRagConfig, Workspace


class WorkspaceRepository(ABC):
    """Interface for Workspace repository operations."""

    @abstractmethod
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
        pass

    @abstractmethod
    def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        """Get workspace by ID."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: int) -> list[Workspace]:
        """Get all workspaces for a users."""
        pass

    @abstractmethod
    def update(self, workspace_id: int, **kwargs) -> Optional[Workspace]:
        """Update workspace fields."""
        pass

    @abstractmethod
    def delete(self, workspace_id: int) -> bool:
        """Delete workspace by ID."""
        pass

    @abstractmethod
    def get_vector_rag_config(self, workspace_id: int) -> Optional[VectorRagConfig]:
        """Get vector RAG config for workspace."""
        pass

    @abstractmethod
    def get_graph_rag_config(self, workspace_id: int) -> Optional[GraphRagConfig]:
        """Get graph RAG config for workspace."""
        pass

    @abstractmethod
    def get_rag_config(self, workspace_id: int) -> Optional[RagConfig]:
        """Get generic RAG config for workspace."""
        pass
