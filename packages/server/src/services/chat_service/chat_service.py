"""Chat service interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.models import ChatMessage, ChatSession


class ChatService(ABC):
    """Interface for chat-related business logic."""

    @abstractmethod
    def create_session(
        self,
        user_id: int,
        title: Optional[str] = None,
        rag_type: str = "vector",
        first_message: Optional[str] = None,
    ) -> ChatSession:
        """Create a new chat session."""
        pass

    @abstractmethod
    def get_session_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get chat session by ID."""
        pass

    @abstractmethod
    def list_user_sessions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatSession]:
        """List all chat sessions for a user with pagination."""
        pass

    @abstractmethod
    def update_session(self, session_id: int, **kwargs: str) -> Optional[ChatSession]:
        """Update chat session fields."""
        pass

    @abstractmethod
    def delete_session(self, session_id: int) -> bool:
        """Delete chat session by ID."""
        pass

    @abstractmethod
    def create_message(
        self,
        session_id: int,
        role: str,
        content: str,
        metadata: Optional[dict[str, str | int]] = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        pass

    @abstractmethod
    def get_message_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        pass

    @abstractmethod
    def list_session_messages(
        self, session_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatMessage]:
        """List all messages for a chat session with pagination."""
        pass

    @abstractmethod
    def delete_message(self, message_id: int) -> bool:
        """Delete chat message by ID."""
        pass

    @abstractmethod
    def get_or_create_session(
        self, user_id: int, session_id: Optional[int] = None, first_message: Optional[str] = None
    ) -> ChatSession:
        """Get existing session or create a new one."""
        pass
