"""SQL implementation of chat session repository using SqlDatabase."""

from typing import List
from shared.models.chat import ChatSession
from shared.types.option import Option, Some, Nothing

from .chat_session_repository import ChatSessionRepository
from shared.database.sql.sql_database import SqlDatabase


class SqlChatSessionRepository(ChatSessionRepository):
    """Repository for ChatSession operations using direct SQL queries."""

    def __init__(self, db: SqlDatabase) -> None:
        """
        Initialize repository with SqlDatabase.

        Args:
            db: SqlDatabase instance
        """
        self._db = db

    def create(
        self, user_id: int, title: str | None = None, rag_type: str | None = "vector"
    ) -> ChatSession:
        """Create a new chat session."""
        query = """
        INSERT INTO chat_session (user_id, title, rag_type, created_at, updated_at)
        VALUES (%(user_id)s, %(title)s, %(rag_type)s, NOW(), NOW())
        RETURNING id, user_id, title, rag_type, created_at, updated_at;
        """
        params = {"user_id": user_id, "title": title, "rag_type": rag_type}
        row = self._db.fetchone(query, params)
        return ChatSession(**row)

    def get_by_id(self, session_id: int) -> Option[ChatSession]:
        """Get chat session by ID."""
        query = "SELECT * FROM chat_session WHERE id = %(id)s;"
        row = self._db.fetchone(query, {"id": session_id})
        if row is None:
            return Nothing()
        return Some(ChatSession(**row))

    def get_by_user(self, user_id: int, skip: int, limit: int) -> List[ChatSession]:
        """Get all chat sessions for a user with pagination."""
        query = """
        SELECT * FROM chat_session
        WHERE user_id = %(user_id)s
        OFFSET %(skip)s
        LIMIT %(limit)s;
        """
        rows = self._db.fetchall(query, {"user_id": user_id, "skip": skip, "limit": limit})
        return [ChatSession(**row) for row in rows]

    def update(self, session_id: int, **kwargs: str) -> Option[ChatSession]:
        """Update chat session fields."""
        # Build dynamic set clause
        if not kwargs:
            return self.get_by_id(session_id)

        set_clause = ", ".join(f"{key} = %({key})s" for key in kwargs.keys())
        kwargs["id"] = session_id
        query = f"""
        UPDATE chat_session
        SET {set_clause}, updated_at = NOW()
        WHERE id = %(id)s
        RETURNING id, user_id, title, rag_type, created_at, updated_at;
        """
        row = self._db.fetchone(query, kwargs)
        if row is None:
            return Nothing()
        return Some(ChatSession(**row))

    def delete(self, session_id: int) -> bool:
        """Delete chat session by ID."""
        query = "DELETE FROM chat_session WHERE id = %(id)s;"
        result = self._db.execute(query, {"id": session_id})
        # Optional: check row count if your SqlDatabase supports it
        return True
