"""Chat message service."""

from src.infrastructure.logger import create_logger
from src.infrastructure.models import ChatMessage
from src.infrastructure.repositories import ChatMessageRepository

logger = create_logger(__name__)


class ChatMessageService:
    """Service for managing chat message."""

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
        Create a new chat message.

        Args:
            session_id: The session ID
            role: Message role ('users', 'assistant', 'system')
            content: Message content
            extra_metadata: Additional metadata

        Returns:
            The created message
        """
        logger.info(
            f"Creating chat message: session_id={session_id}, role='{role}', content_length={len(content)}"
        )

        # Validate inputs
        if not content or not content.strip():
            logger.error(f"Message creation failed: empty content (session_id={session_id})")
            raise ValueError("Message content cannot be empty")

        if len(content.strip()) > 10000:  # Reasonable limit for message content
            logger.error(
                f"Message creation failed: content too long {len(content)} chars (session_id={session_id})"
            )
            raise ValueError("Message content too long (max 10000 characters)")

        if role not in ["user", "assistant", "system"]:
            logger.error(
                f"Message creation failed: invalid role '{role}' (session_id={session_id})"
            )
            raise ValueError("Invalid message role. Must be 'user', 'assistant', or 'system'")

        # Validation is performed at the route level

        # Serialize extra_metadata to JSON string if provided
        extra_metadata_str = None
        if extra_metadata:
            import json

            extra_metadata_str = json.dumps(extra_metadata)

        message = self.repository.create(session_id, role, content.strip(), extra_metadata_str)
        logger.info(f"Chat message created: message_id={message.id}, session_id={session_id}")

        return message

    def get_message(self, message_id: int) -> ChatMessage | None:
        """Get message by ID."""
        return self.repository.get_by_id(message_id)

    def get_session_messages(
        self, session_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[ChatMessage], int]:
        """Get message for a session."""
        logger.info(
            f"Retrieving session message: session_id={session_id}, skip={skip}, limit={limit}"
        )

        # Validation is performed at the route level
        messages = self.repository.get_by_session(session_id, skip, limit)
        total = len(self.repository.get_by_session(session_id))  # Get total count

        logger.info(f"Retrieved {len(messages)} message for session {session_id} (total: {total})")

        return messages, total

    def delete_message(self, message_id: int) -> bool:
        """Delete a message."""
        logger.info(f"Deleting chat message: message_id={message_id}")

        deleted = self.repository.delete(message_id)

        if deleted:
            logger.info(f"Chat message deleted: message_id={message_id}")
        else:
            logger.warning(
                f"Chat message deletion failed: message not found (message_id={message_id})"
            )

        return deleted
