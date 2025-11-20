"""Workspace repository for database operations."""

from typing import Optional

from shared.models import RagConfig, Workspace
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload


class WorkspaceRepository:
    """Repository for workspace-related database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create_workspace(
        self, name: str, user_id: int, description: Optional[str] = None
    ) -> Workspace:
        """
        Create a new workspace.

        Args:
            name: Workspace name
            user_id: Owner user ID
            description: Optional description

        Returns:
            Created workspace
        """
        workspace_id = str(uuid.uuid4())
        now = datetime.utcnow()

        query = """
        INSERT INTO workspaces (id, name, description, user_id, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, name, description, user_id, is_active, created_at, updated_at
        """

        row = await self.db.fetchrow(query, workspace_id, name, description, user_id, now, now)

        return Workspace(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            user_id=row["user_id"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def get_workspace(self, workspace_id: str, user_id: str) -> Optional[Workspace]:
        """
        Get workspace by ID for a specific user.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for authorization

        Returns:
            Workspace if found and accessible
        """
        query = """
        SELECT id, name, description, user_id, is_active, created_at, updated_at
        FROM workspaces
        WHERE id = $1 AND user_id = $2
        """

        row = await self.db.fetchrow(query, workspace_id, user_id)
        if not row:
            return None

        return Workspace(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            user_id=row["user_id"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def list_workspaces(
        self, user_id: str, include_inactive: bool = False
    ) -> List[Workspace]:
        """
        List all workspaces for a user.

        Args:
            user_id: User ID
            include_inactive: Whether to include inactive workspaces

        Returns:
            List of workspaces
        """
        query = """
        SELECT id, name, description, user_id, is_active, created_at, updated_at
        FROM workspaces
        WHERE user_id = $1
        """

        if not include_inactive:
            query += " AND is_active = true"

        query += " ORDER BY updated_at DESC"

        rows = await self.db.fetch(query, user_id)

        return [
            Workspace(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                user_id=row["user_id"],
                is_active=row["is_active"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    async def update_workspace(
        self, workspace_id: str, user_id: str, **kwargs
    ) -> Optional[Workspace]:
        """
        Update workspace properties.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for authorization
            **kwargs: Fields to update

        Returns:
            Updated workspace if found
        """
        # Build dynamic update query
        allowed_fields = ["name", "description", "is_active"]
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not update_fields:
            return await self.get_workspace(workspace_id, user_id)

        set_clause = ", ".join(
            [f"{field} = ${i+2}" for i, field in enumerate(update_fields.keys())]
        )
        values = list(update_fields.values())

        query = f"""
        UPDATE workspaces
        SET {set_clause}
        WHERE id = $1 AND user_id = ${len(values) + 2}
        RETURNING id, name, description, user_id, is_active, created_at, updated_at
        """

        row = await self.db.fetchrow(query, workspace_id, *values, user_id)
        if not row:
            return None

        return Workspace(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            user_id=row["user_id"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def delete_workspace(self, workspace_id: str, user_id: str) -> bool:
        """
        Delete a workspace (cascades to documents, chats, etc.).

        Args:
            workspace_id: Workspace ID
            user_id: User ID for authorization

        Returns:
            True if workspace was deleted
        """
        query = "DELETE FROM workspaces WHERE id = $1 AND user_id = $2"
        result = await self.db.execute(query, workspace_id, user_id)

        return result == "DELETE 1"

    async def get_workspace_stats(
        self, workspace_id: str, user_id: str
    ) -> Optional[WorkspaceStats]:
        """
        Get statistics for a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for authorization

        Returns:
            Workspace statistics if accessible
        """
        # First verify access
        workspace = await self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None

        query = """
        SELECT * FROM workspace_stats
        WHERE workspace_id = $1
        """

        row = await self.db.fetchrow(query, workspace_id)
        if not row:
            # Return empty stats if no data
            return WorkspaceStats(
                workspace_id=workspace_id,
                document_count=0,
                total_document_size=0,
                chunk_count=0,
                chat_session_count=0,
                total_message_count=0,
                last_activity=None,
            )

        return WorkspaceStats(
            workspace_id=row["workspace_id"],
            document_count=row["document_count"],
            total_document_size=row["total_document_size"],
            chunk_count=row["chunk_count"],
            chat_session_count=row["chat_session_count"],
            total_message_count=row["total_message_count"],
            last_activity=row["last_activity"],
        )


class RagConfigRepository:
    """Repository for RAG configuration operations."""

    def __init__(self, db_connection):
        """Initialize repository with database connection."""
        self.db = db_connection

    async def create_rag_config(self, workspace_id: str, config_data: dict) -> RagConfig:
        """
        Create RAG configuration for a workspace.

        Args:
            workspace_id: Workspace ID
            config_data: Configuration parameters

        Returns:
            Created RAG configuration
        """
        config_id = str(uuid.uuid4())
        now = datetime.utcnow()

        query = """
        INSERT INTO rag_configs (
            id, workspace_id, embedding_model, retriever_type, chunk_size,
            chunk_overlap, top_k, embedding_dim, rerank_enabled, rerank_model,
            created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
        )
        RETURNING *
        """

        row = await self.db.fetchrow(
            query,
            config_id,
            workspace_id,
            config_data.get("embedding_model", "nomic-embed-text"),
            config_data.get("retriever_type", "vector"),
            config_data.get("chunk_size", 1000),
            config_data.get("chunk_overlap", 0),
            config_data.get("top_k", 8),
            config_data.get("embedding_dim"),
            config_data.get("rerank_enabled", False),
            config_data.get("rerank_model"),
            now,
            now,
        )

        return RagConfig(
            id=row["id"],
            workspace_id=row["workspace_id"],
            embedding_model=row["embedding_model"],
            retriever_type=row["retriever_type"],
            chunk_size=row["chunk_size"],
            chunk_overlap=row["chunk_overlap"],
            top_k=row["top_k"],
            embedding_dim=row["embedding_dim"],
            rerank_enabled=row["rerank_enabled"],
            rerank_model=row["rerank_model"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def get_rag_config(self, workspace_id: str, user_id: str) -> Optional[RagConfig]:
        """
        Get RAG configuration for a workspace.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for authorization

        Returns:
            RAG configuration if found and accessible
        """
        query = """
        SELECT rc.* FROM rag_configs rc
        JOIN workspaces w ON w.id = rc.workspace_id
        WHERE rc.workspace_id = $1 AND w.user_id = $2
        """

        row = await self.db.fetchrow(query, workspace_id, user_id)
        if not row:
            return None

        return RagConfig(
            id=row["id"],
            workspace_id=row["workspace_id"],
            embedding_model=row["embedding_model"],
            retriever_type=row["retriever_type"],
            chunk_size=row["chunk_size"],
            chunk_overlap=row["chunk_overlap"],
            top_k=row["top_k"],
            embedding_dim=row["embedding_dim"],
            rerank_enabled=row["rerank_enabled"],
            rerank_model=row["rerank_model"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def update_rag_config(
        self, workspace_id: str, user_id: str, **kwargs
    ) -> Optional[RagConfig]:
        """
        Update RAG configuration.

        Args:
            workspace_id: Workspace ID
            user_id: User ID for authorization
            **kwargs: Fields to update

        Returns:
            Updated RAG configuration if found
        """
        # Build dynamic update query
        allowed_fields = [
            "embedding_model",
            "retriever_type",
            "chunk_size",
            "chunk_overlap",
            "top_k",
            "embedding_dim",
            "rerank_enabled",
            "rerank_model",
        ]
        update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}

        if not update_fields:
            return await self.get_rag_config(workspace_id, user_id)

        set_clause = ", ".join(
            [f"{field} = ${i+2}" for i, field in enumerate(update_fields.keys())]
        )
        values = list(update_fields.values())

        query = f"""
        UPDATE rag_configs
        SET {set_clause}
        WHERE workspace_id = $1
        RETURNING *
        """

        row = await self.db.fetchrow(query, workspace_id, *values)
        if not row:
            return None

        return RagConfig(
            id=row["id"],
            workspace_id=row["workspace_id"],
            embedding_model=row["embedding_model"],
            retriever_type=row["retriever_type"],
            chunk_size=row["chunk_size"],
            chunk_overlap=row["chunk_overlap"],
            top_k=row["top_k"],
            embedding_dim=row["embedding_dim"],
            rerank_enabled=row["rerank_enabled"],
            rerank_model=row["rerank_model"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
