"""Chat message repository interface."""

from abc import ABC, abstractmethod

from shared.models.chat import ChatMessage
from shared.types.option import Option


class ChatMessageRepository(ABC):
    """Interface for ChatMessage repository operations."""

    @abstractmethod
    def create(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: str | None = None,
    ) -> ChatMessage:
        """
        Create a new chat message.

        Args:
            session_id: Parent session ID
            role: Message role (user, assistant, system)
            content: Message content
            extra_metadata: Optional JSON metadata

        Returns:
            Created chat message
        """
        pass

    @abstractmethod
    def get_by_id(self, message_id: int) -> Option[ChatMessage]:
        """
        Get message by ID.

        Args:
            message_id: Message ID

        Returns:
            Some(ChatMessage) if found, Nothing() if not found
        """
        pass

    @abstractmethod
    def get_by_session(self, session_id: int, skip: int, limit: int) -> list[ChatMessage]:
        """
        Get messages by session ID with pagination.

        Args:
            session_id: Session ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of chat messages ordered by creation time
        """
        pass

    @abstractmethod
    def delete(self, message_id: int) -> bool:
        """
        Delete message by ID.

        Args:
            message_id: Message ID

        Returns:
            True if deleted, False if not found
        """
        pass
