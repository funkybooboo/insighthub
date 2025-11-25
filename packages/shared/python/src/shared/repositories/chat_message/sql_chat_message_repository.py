"""SQL implementation of chat message repository using PostgresSqlDatabase."""

from typing import Optional

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase
from shared.models.chat import ChatMessage

from .chat_message_repository import ChatMessageRepository


class SqlChatMessageRepository(ChatMessageRepository):
    """Repository for ChatMessage operations using direct SQL queries."""

    def __init__(self, db: PostgresSqlDatabase) -> None:
        """
        Initialize repository with PostgresSqlDatabase.

        Args:
            db: PostgresSqlDatabase instance
        """
        self._db = db

    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: str | None = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        query = """
        INSERT INTO chat_messages (session_id, role, content, extra_metadata)
        VALUES (%(session_id)s, %(role)s, %(content)s, %(extra_metadata)s)
        RETURNING *;
        """
        params = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "extra_metadata": extra_metadata,
        }
        row = self._db.fetchone(query, params)
        if row is None:
            raise ValueError("Failed to create chat message")
        return ChatMessage(**row)

    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        query = "SELECT * FROM chat_messages WHERE id = %(id)s;"
        row = self._db.fetchone(query, {"id": message_id})
        if row is None:
            return None
        return ChatMessage(**row)

    def get_by_session(self, session_id: int, skip: int, limit: int) -> list[ChatMessage]:
        """Get all messages for a chat session with pagination."""
        query = """
        SELECT * FROM chat_messages
        WHERE session_id = %(session_id)s
        ORDER BY created_at
        OFFSET %(skip)s
        LIMIT %(limit)s;
        """
        rows = self._db.fetchall(query, {"session_id": session_id, "skip": skip, "limit": limit})
        return [ChatMessage(**row) for row in rows]

    def delete(self, message_id: int) -> bool:
        """Delete chat message by ID."""
        message = self.get_by_id(message_id)
        if message is None:
            return False

        query = "DELETE FROM chat_messages WHERE id = %(id)s;"
        self._db.execute(query, {"id": message_id})
        return True
