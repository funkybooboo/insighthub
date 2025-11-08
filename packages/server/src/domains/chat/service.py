"""Chat service implementation."""

import json
from dataclasses import dataclass

from .models import ChatMessage, ChatSession
from .repositories import ChatMessageRepository, ChatSessionRepository


@dataclass
class ChatContext:
    """Context chunk retrieved from RAG system."""

    text: str
    score: float
    metadata: dict[str, str]


@dataclass
class ChatResponse:
    """Result of processing a chat message."""

    answer: str
    context: list[ChatContext]
    session_id: int
    user_message: ChatMessage
    assistant_message: ChatMessage


class ChatService:
    """Service for chat-related business logic."""

    def __init__(
        self, session_repository: ChatSessionRepository, message_repository: ChatMessageRepository
    ):
        """
        Initialize service with repositories.

        Args:
            session_repository: Chat session repository implementation
            message_repository: Chat message repository implementation
        """
        self.session_repository = session_repository
        self.message_repository = message_repository

    def create_session(
        self,
        user_id: int,
        title: str | None = None,
        rag_type: str = "vector",
        first_message: str | None = None,
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

    def get_session_by_id(self, session_id: int) -> ChatSession | None:
        """Get chat session by ID."""
        return self.session_repository.get_by_id(session_id)

    def list_user_sessions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatSession]:
        """List all chat sessions for a user with pagination."""
        return self.session_repository.get_by_user(user_id, skip=skip, limit=limit)

    def update_session(self, session_id: int, **kwargs: str) -> ChatSession | None:
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
        metadata: dict[str, str | int] | None = None,
    ) -> ChatMessage:
        """Create a new chat message."""
        metadata_json = json.dumps(metadata) if metadata else None
        return self.message_repository.create(
            session_id=session_id, role=role, content=content, extra_metadata=metadata_json
        )

    def get_message_by_id(self, message_id: int) -> ChatMessage | None:
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
        self, user_id: int, session_id: int | None = None, first_message: str | None = None
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

    def process_chat_message(
        self,
        user_id: int,
        message: str,
        session_id: int | None = None,
        rag_type: str = "vector",
    ) -> ChatResponse:
        """
        High-level orchestration method for processing a chat message.

        Handles the complete workflow including session management,
        message storage, RAG querying, and response generation.

        Args:
            user_id: ID of the user sending the message
            message: The user's message
            session_id: Optional existing session ID
            rag_type: Type of RAG to use (vector or graph)

        Returns:
            ChatResponse with answer, context, and message records
        """
        # Get or create session
        session = self.get_or_create_session(
            user_id=user_id,
            session_id=session_id,
            first_message=message,
        )

        # Store user message
        user_message = self.create_message(
            session_id=session.id,
            role="user",
            content=message,
        )

        # TODO: Query RAG system
        # from src.rag.factory import create_rag
        # rag = create_rag(rag_type=rag_type, ...)
        # results = rag.query(message, top_k=5)
        # answer = results["answer"]
        # context_chunks = results["context"]

        # Mock response for now
        answer = f"Mock response to: {message}"
        context_chunks = [
            ChatContext(
                text="Sample context chunk 1",
                score=0.85,
                metadata={"source": "document_1"},
            ),
        ]

        # Store assistant response
        assistant_message = self.create_message(
            session_id=session.id,
            role="assistant",
            content=answer,
            metadata={
                "context_chunks": len(context_chunks),
                "rag_type": rag_type,
            },
        )

        return ChatResponse(
            answer=answer,
            context=context_chunks,
            session_id=session.id,
            user_message=user_message,
            assistant_message=assistant_message,
        )
