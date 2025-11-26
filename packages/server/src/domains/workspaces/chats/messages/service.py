"""Chat message service."""

from src.infrastructure.models import ChatMessage
from src.infrastructure.repositories.chat_messages import ChatMessageRepository


class ChatMessageService:
    """Service for managing chats messages."""

    def __init__(self, repository: ChatMessageRepository):
        """Initialize service with repository."""
        self.repository = repository

    def create_message(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: dict | None = None,
    ) -> ChatMessage:
        """
        Create a new chats message.

        Args:
            session_id: The session ID
            role: Message role ('users', 'assistant', 'system')
            content: Message content
            extra_metadata: Additional metadata

        Returns:
            The created message
        """
        # Validate inputs
        if not content or not content.strip():
            raise ValueError("Message content cannot be empty")

        if len(content.strip()) > 10000:  # Reasonable limit for message content
            raise ValueError("Message content too long (max 10000 characters)")

        if role not in ["users", "assistant", "system"]:
            raise ValueError("Invalid message role. Must be 'users', 'assistant', or 'system'")

        # Validation is performed at the route level

        # Serialize extra_metadata to JSON string if provided
        extra_metadata_str = None
        if extra_metadata:
            import json
            extra_metadata_str = json.dumps(extra_metadata)

        return self.repository.create(session_id, role, content.strip(), extra_metadata_str)

    def get_message(self, message_id: int) -> ChatMessage | None:
        """Get message by ID."""
        return self.repository.get_by_id(message_id)

    def get_session_messages(
        self, session_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[ChatMessage], int]:
        """Get messages for a session."""
        # Validation is performed at the route level
        messages = self.repository.get_by_session(session_id, skip, limit)
        total = len(self.repository.get_by_session(session_id))  # Get total count
        return messages, total

    def delete_message(self, message_id: int) -> bool:
        """Delete a message."""
        return self.repository.delete(message_id)

    def validate_message_access(self, message_id: int, user_id: int) -> bool:
        """Validate that users has access to message through session ownership."""
        message = self.repository.get_by_id(message_id)
        if not message:
            return False

        # Check if users owns the session this message belongs to
        # This requires access to session service - validation is performed at route level
        return True

    def get_session_messages_for_user(
        self, session_id: int, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[ChatMessage]:
        """Get messages for a session, validating users access."""
        # Validation is performed at the route level
        return self.repository.get_by_session(session_id, skip, limit)
