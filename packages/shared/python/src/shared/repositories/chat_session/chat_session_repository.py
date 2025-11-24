"""Chat session repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from shared.models.chat import ChatSession


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
        """
        Create a new chat session.

        Args:
            user_id: Owner user ID
            title: Optional session title
            workspace_id: Workspace ID (optional)
            rag_type: RAG type (vector, graph), defaults to vector

        Returns:
            Created chat session
        """
        pass

    @abstractmethod
    def get_by_id(self, session_id: int) -> Optional[ChatSession]:
        """
        Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            ChatSession if found, None if not found
        """
        pass

    @abstractmethod
    def get_by_user(self, user_id: int, skip: int, limit: int) -> list[ChatSession]:
        """
        Get sessions by user ID with pagination.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of chat sessions
        """
        pass

    @abstractmethod
    def update(self, session_id: int, **kwargs: str | int | None) -> Optional[ChatSession]:
        """
        Update session fields.

        Args:
            session_id: Session ID
            **kwargs: Fields to update

        Returns:
            ChatSession if found and updated, None if not found
        """
        pass

    @abstractmethod
    def delete(self, session_id: int) -> bool:
        """
        Delete session by ID.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found
        """
        pass
