"""In-memory implementation of ChatMessageRepository."""

from typing import Optional

from src.infrastructure.models import ChatMessage
from .chat_message_repository import ChatMessageRepository


class InMemoryChatMessageRepository(ChatMessageRepository):
    """In-memory implementation of ChatMessageRepository for development/testing."""

    def __init__(self):
        """Initialize the repository."""
        self._messages: dict[int, ChatMessage] = {}
        self._next_id = 1

    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: str | None = None,
    ) -> ChatMessage:
        """Create a new chats message."""
        message = ChatMessage(
            id=self._next_id,
            session_id=session_id,
            role=role,
            content=content,
            extra_metadata=extra_metadata,
        )
        self._messages[self._next_id] = message
        self._next_id += 1
        return message

    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get message by ID."""
        return self._messages.get(message_id)

    def get_by_session(self, session_id: int, skip: int = 0, limit: int = 50) -> list[ChatMessage]:
        """Get messages for a session with pagination."""
        session_messages = [msg for msg in self._messages.values() if msg.session_id == session_id]
        # Sort by creation time (oldest first for conversations)
        session_messages.sort(key=lambda msg: msg.created_at)
        return session_messages[skip:skip + limit]

    def delete(self, message_id: int) -> bool:
        """Delete message by ID."""
        if message_id in self._messages:
            del self._messages[message_id]
            return True
        return False