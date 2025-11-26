"""Chat message service."""

from flask import g

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

    def validate_workspace_and_session_access(self, workspace_id: int, session_id: int, user_id: int) -> bool:
        """Validate that user has access to the workspace and session.

        Args:
            workspace_id: Workspace ID to validate
            session_id: Session ID to validate
            user_id: User ID performing the validation

        Returns:
            True if user has access, False otherwise
        """

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user_id):
            return False

        # Validate session access and workspace membership
        session_service = g.app_context.chat_session_service
        session = session_service.get_workspace_session(workspace_id, session_id, user_id)
        return session is not None

    def validate_message_access(self, message_id: int, session_id: int, user_id: int) -> bool:
        """Validate that user has access to the specific message.

        Args:
            message_id: Message ID to validate
            session_id: Expected session ID
            user_id: User ID performing the validation

        Returns:
            True if user has access to the message, False otherwise
        """
        # Get the message
        message = self.get_message(message_id)
        if not message:
            return False

        # Ensure message belongs to the specified session
        if message.session_id != session_id:
            return False

        # Validate that user has access to the session
        session_service = g.app_context.chat_session_service
        return session_service.validate_session_access(session_id, user_id)

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
