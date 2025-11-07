"""Chat message repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.models import ChatMessage


class ChatMessageRepository(ABC):
    """Interface for ChatMessage repository operations."""

    @abstractmethod
    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: Optional[str] = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        pass

    @abstractmethod
    def get_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get message by ID."""
        pass

    @abstractmethod
    def get_by_session(
        self, session_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatMessage]:
        """Get messages by session ID with pagination."""
        pass

    @abstractmethod
    def delete(self, message_id: int) -> bool:
        """Delete message by ID."""
        pass
