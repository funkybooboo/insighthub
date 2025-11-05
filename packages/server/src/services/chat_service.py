"""Chat service for business logic."""

import json
from typing import Optional

from src.db.interfaces import ChatMessageRepository, ChatSessionRepository
from src.db.models import ChatMessage, ChatSession


class ChatService:
    """Service for chat-related business logic."""

    def __init__(
        self, session_repository: ChatSessionRepository, message_repository: ChatMessageRepository
    ):
        self.session_repository = session_repository
        self.message_repository = message_repository

    def create_session(
        self,
        user_id: int,
        title: Optional[str] = None,
        rag_type: str = "vector",
        first_message: Optional[str] = None,
    ) -> ChatSession:
        """
        Create a new chat session.

        Args:
            user_id: The user ID
            title: Optional session title
            rag_type: Type of RAG to use (vector or graph)
            first_message: Optional first message to use as title if title not provided

        Returns:
            ChatSession: The newly created session
        """
        # Use first_message as title if title not provided
        if not title and first_message:
            title = first_message[:50] + "..." if len(first_message) > 50 else first_message

        return self.session_repository.create(user_id=user_id, title=title, rag_type=rag_type)

    def get_session_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get chat session by ID."""
        return self.session_repository.get_by_id(session_id)

    def list_user_sessions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatSession]:
        """List all chat sessions for a user with pagination."""
        return self.session_repository.get_by_user(user_id, skip=skip, limit=limit)

    def update_session(self, session_id: int, **kwargs: str) -> Optional[ChatSession]:
        """Update chat session fields."""
        return self.session_repository.update(session_id, **kwargs)

    def delete_session(self, session_id: int) -> bool:
        """Delete chat session by ID."""
        return self.session_repository.delete(session_id)

    def create_message(
        self,
        session_id: int,
        role: str,
        content: str,
        metadata: Optional[dict[str, str | int]] = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        metadata_json = json.dumps(metadata) if metadata else None
        return self.message_repository.create(
            session_id=session_id, role=role, content=content, extra_metadata=metadata_json
        )

    def get_message_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        return self.message_repository.get_by_id(message_id)

    def list_session_messages(
        self, session_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatMessage]:
        """List all messages for a chat session with pagination."""
        return self.message_repository.get_by_session(session_id, skip=skip, limit=limit)

    def delete_message(self, message_id: int) -> bool:
        """Delete chat message by ID."""
        return self.message_repository.delete(message_id)

    def get_or_create_session(
        self, user_id: int, session_id: Optional[int] = None, first_message: Optional[str] = None
    ) -> ChatSession:
        """
        Get existing session or create a new one.

        Args:
            user_id: The user ID
            session_id: Optional existing session ID
            first_message: Optional first message to use as title for new sessions

        Returns:
            ChatSession: The retrieved or newly created session
        """
        if session_id:
            session = self.get_session_by_id(session_id)
            if session:
                return session

        # Create new session
        return self.create_session(user_id=user_id, first_message=first_message)
