"""Workspace repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from shared.models.workspace import RagConfig, Workspace


class WorkspaceRepository(ABC):
    """Interface for Workspace repository operations."""

    @abstractmethod
    def create(
        self,
        user_id: int,
        name: str,
        description: str | None = None,
    ) -> Workspace:
        """
        Create a new workspace.

        Args:
            user_id: Owner user ID
            name: Workspace name
            description: Optional description

        Returns:
            Created workspace
        """
        pass

    @abstractmethod
    def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        """
        Get workspace by ID.

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace if found, None if not found
        """
        pass

    @abstractmethod
    def get_by_user(
        self,
        user_id: int,
        include_inactive: bool = False,
    ) -> list[Workspace]:
        """
        Get all workspaces for a user.

        Args:
            user_id: User ID
            include_inactive: Include inactive workspaces

        Returns:
            List of workspaces
        """
        pass

    @abstractmethod
    def update(
        self,
        workspace_id: int,
        **kwargs: str | int | bool | None,
    ) -> Optional[Workspace]:
        """
        Update workspace fields.

        Args:
            workspace_id: Workspace ID
            **kwargs: Fields to update

        Returns:
            Workspace if found and updated, None if not found
        """
        pass

    @abstractmethod
    def delete(self, workspace_id: int) -> bool:
        """
        Delete workspace by ID.

        Args:
            workspace_id: Workspace ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def create_rag_config(
        self,
        workspace_id: int,
        embedding_model: str = "nomic-embed-text",
        embedding_dim: int | None = None,
        retriever_type: str = "vector",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 8,
        rerank_enabled: bool = False,
        rerank_model: str | None = None,
    ) -> RagConfig:
        """
        Create RAG configuration for a workspace.

        Args:
            workspace_id: Workspace ID
            embedding_model: Embedding model name
            embedding_dim: Embedding dimension
            retriever_type: Type of retriever (vector, graph, hybrid)
            chunk_size: Chunk size for documents
            chunk_overlap: Chunk overlap
            top_k: Number of results to retrieve
            rerank_enabled: Whether reranking is enabled
            rerank_model: Reranking model name

        Returns:
            Created RagConfig
        """
        pass

    @abstractmethod
    def get_rag_config(self, workspace_id: int) -> Optional[RagConfig]:
        """
        Get RAG configuration for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            RagConfig if found, None if not found
        """
        pass

    @abstractmethod
    def update_rag_config(
        self,
        workspace_id: int,
        **kwargs: str | int | bool | None,
    ) -> Optional[RagConfig]:
        """
        Update RAG configuration fields.

        Args:
            workspace_id: Workspace ID
            **kwargs: Fields to update

        Returns:
            RagConfig if found and updated, None if not found
        """
        pass

    @abstractmethod
    def get_document_count(self, workspace_id: int) -> int:
        """
        Get count of documents in workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Document count
        """
        pass

    @abstractmethod
    def get_session_count(self, workspace_id: int) -> int:
        """
        Get count of chat sessions in workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Session count
        """
        pass
