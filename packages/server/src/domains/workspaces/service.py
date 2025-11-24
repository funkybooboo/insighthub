"""Workspace domain service for managing workspaces and RAG configurations."""

from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict, Optional

from shared.messaging import RabbitMQPublisher
from shared.models.workspace import RagConfig, Workspace
from shared.repositories.workspace import WorkspaceRepository





# Type for update data fields
UpdateValue = str | int | bool | None


@dataclass
class WorkspaceStats:
    """Statistics for a workspace."""

    workspace_id: int
    document_count: int
    total_document_size: int
    chunk_count: int
    chat_session_count: int
    total_message_count: int
    last_activity: datetime | None


class WorkspaceService:
    """Service for workspace operations."""

    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        message_publisher: RabbitMQPublisher | None = None,
    ):
        self._repo = workspace_repo
        self._message_publisher = message_publisher

    def create_workspace(
        self,
        name: str,
        user_id: int,
        description: str | None = None,
        rag_config: dict | None = None,
    ) -> Workspace:
        """
        Create a new workspace with RAG configuration.

        Args:
            name: Workspace name
            user_id: Owner user ID
            description: Optional description
            rag_config: Optional RAG configuration (uses defaults if not provided)

        Returns:
            Created workspace
        """
        # Create workspace with provisioning status
        workspace = self._repo.create(
            user_id=user_id,
            name=name,
            description=description,
        )

        # Create RAG config for the workspace
        if rag_config:
            self._repo.create_rag_config(
                workspace_id=workspace.id,
                embedding_model=rag_config.get("embedding_model", "nomic-embed-text"),
                embedding_dim=rag_config.get("embedding_dim"),
                retriever_type=rag_config.get("retriever_type", "vector"),
                chunk_size=rag_config.get("chunk_size", 1000),
                chunk_overlap=rag_config.get("chunk_overlap", 200),
                top_k=rag_config.get("top_k", 8),
                rerank_enabled=rag_config.get("rerank_enabled", False),
                rerank_model=rag_config.get("rerank_model"),
            )
        else:
            # Use default RAG config
            self._repo.create_rag_config(workspace_id=workspace.id)

        # Publish workspace provision requested event
        if self._message_publisher:
            try:
                event_data = {
                    "workspace_id": workspace.id,
                    "user_id": user_id,
                    "name": workspace.name,
                    "rag_config": rag_config or {},
                }
                self._message_publisher.publish(
                    routing_key="workspace.provision_requested",
                    message=event_data,
                )
            except Exception as e:
                # Log error but don't fail workspace creation
                print(f"Failed to publish workspace provision event: {e}")

        return workspace

    def list_workspaces(
        self,
        user_id: int,
        include_inactive: bool = False,
    ) -> list[Workspace]:
        """
        List workspaces for a user.

        Args:
            user_id: User ID
            include_inactive: Include inactive workspaces

        Returns:
            List of workspaces
        """
        return self._repo.get_by_user(user_id, include_inactive)

    def get_workspace(
        self,
        workspace_id: int | str,
        user_id: int,
    ) -> Optional[Workspace]:
        """
        Get a workspace by ID if user has access.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check

        Returns:
            Workspace if found and accessible, None otherwise
        """
        ws_id = int(workspace_id) if isinstance(workspace_id, str) else workspace_id
        workspace = self._repo.get_by_id(ws_id)
        if workspace is None:
            return None
        # Check user access
        if workspace.user_id != user_id:
            return None
        return workspace

    def update_workspace(
        self,
        workspace_id: int | str,
        user_id: int,
        **update_data: UpdateValue,
    ) -> Optional[Workspace]:
        """
        Update a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check
            **update_data: Fields to update

        Returns:
            Updated workspace or None if not found
        """
        workspace = self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None

        return self._repo.update(workspace.id, **update_data)

    def delete_workspace(
        self,
        workspace_id: int | str,
        user_id: int,
    ) -> bool:
        """
        Delete a workspace and all associated data.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check

        Returns:
            True if deleted, False if not found
        """
        workspace = self.get_workspace(workspace_id, user_id)
        if not workspace:
            return False

        # Publish workspace deletion requested event before deleting
        if self._message_publisher:
            try:
                event_data = {
                    "workspace_id": workspace.id,
                    "user_id": user_id,
                    "name": workspace.name,
                }
                self._message_publisher.publish(
                    routing_key="workspace.deletion_requested",
                    message=event_data,
                )
            except Exception as e:
                # Log error but continue with deletion
                print(f"Failed to publish workspace deletion event: {e}")

        return self._repo.delete(workspace.id)

    def get_workspace_stats(
        self,
        workspace_id: int | str,
        user_id: int,
    ) -> Optional[WorkspaceStats]:
        """
        Get statistics for a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check

        Returns:
            WorkspaceStats or None if workspace not found
        """
        workspace = self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None

        ws_id = int(workspace_id) if isinstance(workspace_id, str) else workspace_id
        document_count = self._repo.get_document_count(ws_id)
        session_count = self._repo.get_session_count(ws_id)

        return WorkspaceStats(
            workspace_id=ws_id,
            document_count=document_count,
            total_document_size=0,  # Could add if needed
            chunk_count=0,  # Could add if needed
            chat_session_count=session_count,
            total_message_count=0,  # Could add if needed
            last_activity=None,  # Could add if needed
        )



    def validate_workspace_access(
        self,
        workspace_id: int | str,
        user_id: int,
    ) -> bool:
        """
        Validate that a user has access to a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID

        Returns:
            True if user has access, False otherwise
        """
        workspace = self.get_workspace(workspace_id, user_id)
        return workspace is not None
