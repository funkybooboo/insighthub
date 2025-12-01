"""Chat session repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.infrastructure.models import ChatSession


class ChatSessionRepository(ABC):
    """Interface for ChatSession repository operations."""

    @abstractmethod
    def create(
        self,
        user_id: int,
        title: str | None = None,
        workspace_id: int | None = None,
        rag_type: str = "vector",
    ) -> ChatSession:
        """Create a new chats session."""
        pass

    @abstractmethod
    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get session by ID."""
        pass

    @abstractmethod
    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 50) -> list[ChatSession]:
        """Get sessions by users ID with pagination."""
        pass

    @abstractmethod
    def get_by_workspace(
        self, workspace_id: int, skip: int = 0, limit: int = 50
    ) -> list[ChatSession]:
        """Get sessions by workspace ID with pagination."""
        pass

    @abstractmethod
    def update(self, session_id: int, **kwargs) -> Optional[ChatSession]:
        """Update session fields."""
        pass

    @abstractmethod
    def delete(self, session_id: int) -> bool:
        """Delete session by ID."""
        pass
