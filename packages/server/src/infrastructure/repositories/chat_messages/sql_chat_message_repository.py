"""SQL implementation of ChatMessageRepository."""

from datetime import datetime
from typing import Optional

from src.infrastructure.database import SqlDatabase
from src.infrastructure.models import ChatMessage

from .chat_message_repository import ChatMessageRepository


class SqlChatMessageRepository(ChatMessageRepository):
    """SQL implementation of chat messages repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: str | None = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        query = """
            INSERT INTO chat_messages (session_id, role, content, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.fetch_one(
            query,
            (
                session_id,
                role,
                content,
                datetime.utcnow(),
            ),
        )

        if result:
            return ChatMessage(
                id=result["id"],
                session_id=session_id,
                role=role,
                content=content,
                extra_metadata=extra_metadata,
            )

        raise RuntimeError("Failed to create chat message")

    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get message by ID."""
        query = """
            SELECT id, session_id, role, content, created_at
            FROM chat_messages WHERE id = %s
        """
        result = self.db.fetch_one(query, (message_id,))
        if result:
            return ChatMessage(**result)
        return None

    def get_by_session(self, session_id: int, skip: int = 0, limit: int = 50) -> list[ChatMessage]:
        """Get messages for a session with pagination."""
        query = """
            SELECT id, session_id, role, content, created_at
            FROM chat_messages WHERE session_id = %s
            ORDER BY created_at ASC
            LIMIT %s OFFSET %s
        """
        results = self.db.fetch_all(query, (session_id, limit, skip))
        return [ChatMessage(**result) for result in results]

    def delete(self, message_id: int) -> bool:
        """Delete message by ID."""
        query = "DELETE FROM chat_messages WHERE id = %s"
        affected_rows = self.db.execute(query, (message_id,))
        return affected_rows > 0