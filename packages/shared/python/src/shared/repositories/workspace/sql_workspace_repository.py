"""SQL implementation of workspace repository using PostgresSqlDatabase."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.models.workspace import RagConfig, Workspace

from .workspace_repository import WorkspaceRepository


class SqlWorkspaceRepository(WorkspaceRepository):
    """Repository for Workspace operations using direct SQL queries."""

    def __init__(self, db: PostgresSqlDatabase) -> None:
        """
        Initialize repository with PostgresSqlDatabase.

        Args:
            db: PostgresSqlDatabase instance
        """
        self._db = db

    def create(
        self,
        user_id: int,
        name: str,
        description: str | None = None,
    ) -> Workspace:
        """Create a new workspace."""
        query = """
        INSERT INTO workspaces
            (user_id, name, description, is_active, status)
        VALUES
            (%(user_id)s, %(name)s, %(description)s, TRUE, 'provisioning')
        RETURNING *;
        """
        params = {
            "user_id": user_id,
            "name": name,
            "description": description,
        }
        row = self._db.fetchone(query, params)
        if row is None:
            raise ValueError("Failed to create workspace")
        return Workspace(**row)

    def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        """Get workspace by ID."""
        query = "SELECT * FROM workspaces WHERE id = %(id)s;"
        row = self._db.fetchone(query, {"id": workspace_id})
        if row is None:
            return None
        return Workspace(**row)

    def get_by_user(
        self,
        user_id: int,
        include_inactive: bool = False,
    ) -> list[Workspace]:
        """Get all workspaces for a user."""
        if include_inactive:
            query = """
            SELECT * FROM workspaces
            WHERE user_id = %(user_id)s
            ORDER BY updated_at DESC;
            """
        else:
            query = """
            SELECT * FROM workspaces
            WHERE user_id = %(user_id)s AND is_active = TRUE
            ORDER BY updated_at DESC;
            """
        rows = self._db.fetchall(query, {"user_id": user_id})
        return [Workspace(**row) for row in rows]

    def update(
        self,
        workspace_id: int,
        **kwargs: str | int | bool | None,
    ) -> Optional[Workspace]:
        """Update workspace fields."""
        if not kwargs:
            return self.get_by_id(workspace_id)

        set_clause = ", ".join(f"{key} = %({key})s" for key in kwargs.keys())
        kwargs["id"] = workspace_id
        query = f"""
        UPDATE workspaces
        SET {set_clause}, updated_at = NOW()
        WHERE id = %(id)s
        RETURNING *;
        """
        row = self._db.fetchone(query, kwargs)
        if row is None:
            return None
        return Workspace(**row)

    def delete(self, workspace_id: int) -> bool:
        """Delete workspace by ID (cascades to rag_configs)."""
        # First delete rag_config
        self._db.execute(
            "DELETE FROM rag_configs WHERE workspace_id = %(id)s;",
            {"id": workspace_id},
        )
        # Then delete workspace
        query = "DELETE FROM workspaces WHERE id = %(id)s;"
        self._db.execute(query, {"id": workspace_id})
        return True

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
        """Create RAG configuration for a workspace."""
        query = """
        INSERT INTO rag_configs
            (workspace_id, embedding_model, embedding_dim, retriever_type,
             chunk_size, chunk_overlap, top_k, rerank_enabled, rerank_model)
        VALUES
            (%(workspace_id)s, %(embedding_model)s, %(embedding_dim)s, %(retriever_type)s,
             %(chunk_size)s, %(chunk_overlap)s, %(top_k)s, %(rerank_enabled)s, %(rerank_model)s)
        RETURNING *;
        """
        params = {
            "workspace_id": workspace_id,
            "embedding_model": embedding_model,
            "embedding_dim": embedding_dim,
            "retriever_type": retriever_type,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "top_k": top_k,
            "rerank_enabled": rerank_enabled,
            "rerank_model": rerank_model,
        }
        row = self._db.fetchone(query, params)
        if row is None:
            raise ValueError("Failed to create RAG config")
        return RagConfig(**row)

    def get_rag_config(self, workspace_id: int) -> Optional[RagConfig]:
        """Get RAG configuration for a workspace."""
        query = "SELECT * FROM rag_configs WHERE workspace_id = %(workspace_id)s;"
        row = self._db.fetchone(query, {"workspace_id": workspace_id})
        if row is None:
            return None
        return RagConfig(**row)

    def update_rag_config(
        self,
        workspace_id: int,
        **kwargs: str | int | bool | None,
    ) -> Optional[RagConfig]:
        """Update RAG configuration fields."""
        if not kwargs:
            return self.get_rag_config(workspace_id)

        set_clause = ", ".join(f"{key} = %({key})s" for key in kwargs.keys())
        kwargs["workspace_id"] = workspace_id
        query = f"""
        UPDATE rag_configs
        SET {set_clause}, updated_at = NOW()
        WHERE workspace_id = %(workspace_id)s
        RETURNING *;
        """
        row = self._db.fetchone(query, kwargs)
        if row is None:
            return None
        return RagConfig(**row)

    def get_document_count(self, workspace_id: int) -> int:
        """Get count of documents in workspace."""
        query = """
        SELECT COUNT(*) as count FROM documents
        WHERE workspace_id = %(workspace_id)s;
        """
        row = self._db.fetchone(query, {"workspace_id": workspace_id})
        return row["count"] if row else 0

    def get_session_count(self, workspace_id: int) -> int:
        """Get count of chat sessions in workspace."""
        query = """
        SELECT COUNT(*) as count FROM chat_sessions
        WHERE workspace_id = %(workspace_id)s;
        """
        row = self._db.fetchone(query, {"workspace_id": workspace_id})
        return row["count"] if row else 0
