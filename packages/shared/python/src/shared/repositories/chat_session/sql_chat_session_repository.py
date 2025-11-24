"""SQL implementation of chat session repository using PostgresSqlDatabase."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.models.chat import ChatSession
from .chat_session_repository import ChatSessionRepository


class SqlChatSessionRepository(ChatSessionRepository):
    """Repository for ChatSession operations using direct SQL queries."""

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
        title: str | None = None,
        workspace_id: int | None = None,
        rag_type: str = "vector",
    ) -> ChatSession:
        """Create a new chat session."""
        query = """
        INSERT INTO chat_sessions (user_id, workspace_id, title, rag_type)
        VALUES (%(user_id)s, %(workspace_id)s, %(title)s, %(rag_type)s)
        RETURNING *;
        """
        params = {
            "user_id": user_id,
            "workspace_id": workspace_id,
            "title": title,
            "rag_type": rag_type,
        }
        row = self._db.fetchone(query, params)
        if row is None:
            raise ValueError("Failed to create chat session")
        return ChatSession(**row)

    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get chat session by ID."""
        query = "SELECT * FROM chat_sessions WHERE id = %(id)s;"
        row = self._db.fetchone(query, {"id": session_id})
        if row is None:
            return None
        return ChatSession(**row)

    def get_by_user(self, user_id: int, skip: int, limit: int) -> list[ChatSession]:
        """Get all chat sessions for a user with pagination."""
        query = """
        SELECT * FROM chat_sessions
        WHERE user_id = %(user_id)s
        ORDER BY updated_at DESC
        OFFSET %(skip)s
        LIMIT %(limit)s;
        """
        rows = self._db.fetchall(query, {"user_id": user_id, "skip": skip, "limit": limit})
        return [ChatSession(**row) for row in rows]

    def update(self, session_id: int, **kwargs: str | int | None) -> Optional[ChatSession]:
        """Update chat session fields."""
        if not kwargs:
            return self.get_by_id(session_id)

        set_clause = ", ".join(f"{key} = %({key})s" for key in kwargs.keys())
        kwargs["id"] = session_id
        query = f"""
        UPDATE chat_sessions
        SET {set_clause}, updated_at = NOW()
        WHERE id = %(id)s
        RETURNING *;
        """
        row = self._db.fetchone(query, kwargs)
        if row is None:
            return None
        return ChatSession(**row)

    def delete(self, session_id: int) -> bool:
        """Delete chat session by ID."""
        query = "DELETE FROM chat_sessions WHERE id = %(id)s;"
        self._db.execute(query, {"id": session_id})
        return True
