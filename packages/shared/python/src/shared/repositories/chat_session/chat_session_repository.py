"""Chat session repository interface."""

from abc import ABC, abstractmethod

from shared.models.chat import ChatSession
from shared.types.option import Option


class ChatSessionRepository(ABC):
    """Interface for ChatSession repository operations."""

    @abstractmethod
    def create(
        self, user_id: int, title: str | None = None, rag_type: str | None = None
    ) -> ChatSession:
        """
        Create a new chat session.

        Args:
            user_id: Owner user ID
            title: Optional session title
            rag_type: Optional RAG type (vector, graph)

        Returns:
            Created chat session
        """
        pass

    @abstractmethod
    def get_by_id(self, session_id: int) -> Option[ChatSession]:
        """
        Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Some(ChatSession) if found, Nothing() if not found
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
    def update(self, session_id: int, **kwargs: str) -> Option[ChatSession]:
        """
        Update session fields.

        Args:
            session_id: Session ID
            **kwargs: Fields to update

        Returns:
            Some(ChatSession) if found and updated, Nothing() if not found
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
