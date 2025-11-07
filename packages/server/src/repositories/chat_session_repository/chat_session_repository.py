"""Chat session repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.models import ChatSession


class ChatSessionRepository(ABC):
    """Interface for ChatSession repository operations."""

    @abstractmethod
    def create(
        self, user_id: int, title: Optional[str] = None, rag_type: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session."""
        pass

    @abstractmethod
    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get session by ID."""
        pass

    @abstractmethod
    def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatSession]:
        """Get sessions by user ID with pagination."""
        pass

    @abstractmethod
    def update(self, session_id: int, **kwargs: str) -> Optional[ChatSession]:
        """Update session fields."""
        pass

    @abstractmethod
    def delete(self, session_id: int) -> bool:
        """Delete session by ID."""
        pass
