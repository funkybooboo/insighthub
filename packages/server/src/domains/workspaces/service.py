"""Workspace domain service for managing workspaces and RAG configurations."""

from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

from shared.cache import Cache
from shared.models import Document
from shared.models.chat import ChatMessage, ChatSession
from shared.models.workspace import RagConfig, Workspace
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class RagConfigInput(TypedDict, total=False):
    """TypedDict for RAG configuration input."""

    embedding_model: str
    embedding_dim: int | None
    retriever_type: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    rerank_enabled: bool
    rerank_model: str | None


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

    def __init__(self, db: AsyncSession, cache: Cache | None = None):
        self.db = db
        self.cache = cache

    async def create_workspace(
        self,
        name: str,
        user_id: int,
        description: str | None = None,
        rag_config_data: RagConfigInput | None = None,
    ) -> Workspace:
        """
        Create a new workspace with optional RAG configuration.

        Args:
            name: Workspace name
            user_id: Owner user ID
            description: Optional description
            rag_config_data: Optional RAG configuration dict

        Returns:
            Created workspace
        """
        workspace = Workspace(
            name=name,
            user_id=user_id,
            description=description,
            is_active=True,
            status="provisioning",
        )
        self.db.add(workspace)
        await self.db.flush()  # Get the workspace ID

        # Create RAG config if provided
        if rag_config_data:
            rag_config = RagConfig(
                workspace_id=workspace.id,
                embedding_model=rag_config_data.get("embedding_model", "nomic-embed-text"),
                embedding_dim=rag_config_data.get("embedding_dim"),
                retriever_type=rag_config_data.get("retriever_type", "vector"),
                chunk_size=rag_config_data.get("chunk_size", 1000),
                chunk_overlap=rag_config_data.get("chunk_overlap", 200),
                top_k=rag_config_data.get("top_k", 8),
                rerank_enabled=rag_config_data.get("rerank_enabled", False),
                rerank_model=rag_config_data.get("rerank_model"),
            )
            self.db.add(rag_config)
        else:
            # Create default RAG config
            rag_config = RagConfig(
                workspace_id=workspace.id,
                embedding_model="nomic-embed-text",
                retriever_type="vector",
                chunk_size=1000,
                chunk_overlap=200,
                top_k=8,
                rerank_enabled=False,
            )
            self.db.add(rag_config)

        # Mark workspace as ready (in production, this would be async after provisioning)
        workspace.status = "ready"

        await self.db.commit()
        await self.db.refresh(workspace)

        return workspace

    async def list_workspaces(
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
        query = (
            select(Workspace)
            .options(selectinload(Workspace.rag_config))
            .where(Workspace.user_id == user_id)
            .order_by(Workspace.updated_at.desc())
        )

        if not include_inactive:
            query = query.where(Workspace.is_active == True)  # noqa: E712

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_workspace(
        self,
        workspace_id: int | str,
        user_id: int,
    ) -> Workspace | None:
        """
        Get a workspace by ID if user has access.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check

        Returns:
            Workspace if found and accessible, None otherwise
        """
        ws_id = int(workspace_id) if isinstance(workspace_id, str) else workspace_id
        query = (
            select(Workspace)
            .options(selectinload(Workspace.rag_config))
            .where(Workspace.id == ws_id, Workspace.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_workspace(
        self,
        workspace_id: int | str,
        user_id: int,
        **update_data: UpdateValue,
    ) -> Workspace | None:
        """
        Update a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check
            **update_data: Fields to update

        Returns:
            Updated workspace or None if not found
        """
        workspace = await self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None

        for key, value in update_data.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)

        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def delete_workspace(
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
        workspace = await self.get_workspace(workspace_id, user_id)
        if not workspace:
            return False

        await self.db.delete(workspace)
        await self.db.commit()
        return True

    async def get_workspace_stats(
        self,
        workspace_id: int | str,
        user_id: int,
    ) -> WorkspaceStats | None:
        """
        Get statistics for a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check

        Returns:
            WorkspaceStats or None if workspace not found
        """
        workspace = await self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None

        ws_id = int(workspace_id) if isinstance(workspace_id, str) else workspace_id

        # Document stats
        doc_query = select(
            func.count(Document.id).label("count"),
            func.coalesce(func.sum(Document.file_size), 0).label("total_size"),
            func.coalesce(func.sum(Document.chunk_count), 0).label("chunks"),
        ).where(Document.workspace_id == ws_id)
        doc_result = await self.db.execute(doc_query)
        doc_stats = doc_result.one()

        # Chat session stats
        session_query = select(func.count(ChatSession.id)).where(ChatSession.workspace_id == ws_id)
        session_result = await self.db.execute(session_query)
        session_count = session_result.scalar() or 0

        # Message count
        message_query = (
            select(func.count(ChatMessage.id))
            .select_from(ChatMessage)
            .join(ChatSession, ChatMessage.session_id == ChatSession.id)
            .where(ChatSession.workspace_id == ws_id)
        )
        message_result = await self.db.execute(message_query)
        message_count = message_result.scalar() or 0

        # Last activity (most recent message or document)
        last_doc = select(func.max(Document.created_at)).where(Document.workspace_id == ws_id)
        last_doc_result = await self.db.execute(last_doc)
        last_doc_time = last_doc_result.scalar()

        last_msg = (
            select(func.max(ChatMessage.created_at))
            .select_from(ChatMessage)
            .join(ChatSession, ChatMessage.session_id == ChatSession.id)
            .where(ChatSession.workspace_id == ws_id)
        )
        last_msg_result = await self.db.execute(last_msg)
        last_msg_time = last_msg_result.scalar()

        last_activity = None
        if last_doc_time and last_msg_time:
            last_activity = max(last_doc_time, last_msg_time)
        else:
            last_activity = last_doc_time or last_msg_time

        return WorkspaceStats(
            workspace_id=ws_id,
            document_count=doc_stats.count,
            total_document_size=doc_stats.total_size,
            chunk_count=doc_stats.chunks,
            chat_session_count=session_count,
            total_message_count=message_count,
            last_activity=last_activity,
        )

    async def get_rag_config(
        self,
        workspace_id: int | str,
        user_id: int,
    ) -> RagConfig | None:
        """
        Get RAG configuration for a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check

        Returns:
            RagConfig or None if not found
        """
        workspace = await self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None

        ws_id = int(workspace_id) if isinstance(workspace_id, str) else workspace_id
        query = select(RagConfig).where(RagConfig.workspace_id == ws_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_rag_config(
        self,
        workspace_id: int | str,
        user_id: int,
        **update_data: UpdateValue,
    ) -> RagConfig | None:
        """
        Update RAG configuration for a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check
            **update_data: Fields to update

        Returns:
            Updated RagConfig or None if not found
        """
        rag_config = await self.get_rag_config(workspace_id, user_id)
        if not rag_config:
            return None

        for key, value in update_data.items():
            if hasattr(rag_config, key):
                setattr(rag_config, key, value)

        await self.db.commit()
        await self.db.refresh(rag_config)
        return rag_config

    async def validate_workspace_access(
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
        workspace = await self.get_workspace(workspace_id, user_id)
        return workspace is not None

    async def get_workspace_documents(
        self,
        workspace_id: int | str,
        user_id: int,
    ) -> list[Document]:
        """
        Get all documents in a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check

        Returns:
            List of documents
        """
        workspace = await self.get_workspace(workspace_id, user_id)
        if not workspace:
            return []

        ws_id = int(workspace_id) if isinstance(workspace_id, str) else workspace_id
        query = (
            select(Document)
            .where(Document.workspace_id == ws_id)
            .order_by(Document.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def add_document_to_workspace(
        self,
        workspace_id: int | str,
        user_id: int,
        document: Document,
    ) -> Document | None:
        """
        Associate a document with a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for access check
            document: Document to associate

        Returns:
            Updated document or None if workspace not found
        """
        workspace = await self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None

        ws_id = int(workspace_id) if isinstance(workspace_id, str) else workspace_id
        document.workspace_id = ws_id
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def remove_document_from_workspace(
        self,
        workspace_id: int | str,
        document_id: int,
        user_id: int,
    ) -> bool:
        """
        Remove a document from a workspace (and delete it).

        Args:
            workspace_id: Workspace ID
            document_id: Document ID
            user_id: User ID for access check

        Returns:
            True if deleted, False if not found
        """
        workspace = await self.get_workspace(workspace_id, user_id)
        if not workspace:
            return False

        ws_id = int(workspace_id) if isinstance(workspace_id, str) else workspace_id
        query = select(Document).where(
            Document.id == document_id,
            Document.workspace_id == ws_id,
        )
        result = await self.db.execute(query)
        document = result.scalar_one_or_none()

        if not document:
            return False

        await self.db.delete(document)
        await self.db.commit()
        return True
