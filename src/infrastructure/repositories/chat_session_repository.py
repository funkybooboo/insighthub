"""SQL implementation of ChatSessionRepository."""

from datetime import datetime
from typing import Optional

from src.infrastructure.sql_database import SqlDatabase
from src.infrastructure.models import ChatSession




class ChatSessionRepository:
    """SQL implementation of chat session repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

    def create(
        self,
        title: str | None = None,
        workspace_id: int | None = None,
        rag_type: str = "vector",
    ) -> ChatSession:
        """Create a new chat session (single-user system)."""
        query = """
            INSERT INTO chat_sessions (workspace_id, title, rag_type, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.fetch_one(
            query,
            (
                workspace_id,
                title,
                rag_type,
                datetime.utcnow(),
                datetime.utcnow(),
            ),
        )

        if result:
            return ChatSession(
                id=result["id"],
                workspace_id=workspace_id,
                title=title,
                rag_type=rag_type,
            )

        raise RuntimeError("Failed to create chat session")

    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get session by ID."""
        query = """
            SELECT id, workspace_id, title, rag_type, created_at, updated_at
            FROM chat_sessions WHERE id = %s
        """
        result = self.db.fetch_one(query, (session_id,))
        if result:
            return ChatSession(**result)
        return None

    def get_all(self, skip: int = 0, limit: int = 50) -> list[ChatSession]:
        """Get all chat session (single-user system)."""
        query = """
            SELECT id, workspace_id, title, rag_type, created_at, updated_at
            FROM chat_sessions
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        results = self.db.fetch_all(query, (limit, skip))
        return [ChatSession(**result) for result in results]

    def get_by_workspace(
        self, workspace_id: int, skip: int = 0, limit: int = 50
    ) -> list[ChatSession]:
        """Get session by workspace ID with pagination."""
        query = """
            SELECT id, workspace_id, title, rag_type, created_at, updated_at
            FROM chat_sessions WHERE workspace_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        results = self.db.fetch_all(query, (workspace_id, limit, skip))
        return [ChatSession(**result) for result in results]

    def update(self, session_id: int, **kwargs) -> Optional[ChatSession]:
        """Update session fields."""
        # Get current session
        session = self.get_by_id(session_id)
        if not session:
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        session.updated_at = datetime.utcnow()

        # Update in database
        query = """
            UPDATE chat_sessions
            SET title = %s, rag_type = %s, updated_at = %s
            WHERE id = %s
        """
        self.db.execute(
            query,
            (
                session.title,
                session.rag_type,
                session.updated_at,
                session_id,
            ),
        )

        return session

    def delete(self, session_id: int) -> bool:
        """Delete session by ID."""
        query = "DELETE FROM chat_sessions WHERE id = %s"
        affected_rows = self.db.execute(query, (session_id,))
        return affected_rows > 0
