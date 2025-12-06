"""SQL implementation of ChatSessionRepository."""

from datetime import UTC, datetime
from typing import Optional

from returns.result import Failure, Result, Success

from src.domains.workspace.chat.session.models import ChatSession
from src.infrastructure.logger import create_logger
from src.infrastructure.sql_database import DatabaseException, SqlDatabase
from src.infrastructure.types import DatabaseError

logger = create_logger(__name__)


class ChatSessionRepository:
    """SQL implementation of chat session repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

    def create(
        self,
        title: Optional[str]= None,
        workspace_id: Optional[int]= None,
        rag_type: str = "vector",
    ) -> Result[ChatSession, DatabaseError]:
        """Create a new chat session (single-user system)."""
        query = """
            INSERT INTO chat_sessions (workspace_id, title, rag_type, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        try:
            result = self.db.fetch_one(
                query,
                (
                    workspace_id,
                    title,
                    rag_type,
                    datetime.now(UTC),
                    datetime.now(UTC),
                ),
            )
        except DatabaseException as e:
            logger.error(f"Database error creating chat session: {e}")
            return Failure(DatabaseError(e.message, operation="create_chat_session"))

        if not result:
            return Failure(
                DatabaseError("Insert returned no result", operation="create_chat_session")
            )

        return Success(
            ChatSession(
                id=result["id"],
                workspace_id=workspace_id if workspace_id is not None else 0,
                title=title,
                rag_type=rag_type,
            )
        )

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

        session.updated_at = datetime.now(UTC)

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
