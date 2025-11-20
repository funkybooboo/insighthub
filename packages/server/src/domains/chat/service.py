"""Chat service implementation."""

import json
import logging
import threading
from collections.abc import Generator
from dataclasses import dataclass

from shared.llm import LlmProvider
from shared.models import ChatMessage, ChatSession
from shared.repositories import ChatMessageRepository, ChatSessionRepository

from .dtos import ChatResponse as ChatResponseDTO
from .dtos import SessionListResponse, SessionMessagesResponse, StreamEvent
from .exceptions import EmptyMessageError
from .mappers import ChatMapper

logger = logging.getLogger(__name__)


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
        self._cancel_flags: dict[str, threading.Event] = {}
        self._cancel_flags_lock = threading.Lock()

    def validate_message(self, message: str) -> None:
        """
        Validate chat message content.

        Args:
            message: The message to validate

        Raises:
            EmptyMessageError: If message is empty or whitespace
        """
        if not message or not message.strip():
            logger.warning("Chat message validation failed: empty message")
            raise EmptyMessageError()

    def cancel_stream(self, request_id: str) -> None:
        """
        Cancel an active streaming request.

        Args:
            request_id: The unique identifier for the streaming request
        """
        with self._cancel_flags_lock:
            if request_id in self._cancel_flags:
                logger.info(f"Cancelling streaming request: request_id={request_id}")
                self._cancel_flags[request_id].set()
            else:
                logger.warning(f"No active stream found for request_id={request_id}")

    def _get_cancel_flag(self, request_id: str) -> threading.Event:
        """
        Get or create a cancel flag for a streaming request.

        Args:
            request_id: The unique identifier for the streaming request

        Returns:
            threading.Event: The cancel flag for this request
        """
        with self._cancel_flags_lock:
            if request_id not in self._cancel_flags:
                self._cancel_flags[request_id] = threading.Event()
            return self._cancel_flags[request_id]

    def _cleanup_cancel_flag(self, request_id: str) -> None:
        """
        Clean up cancel flag after streaming completes.

        Args:
            request_id: The unique identifier for the streaming request
        """
        with self._cancel_flags_lock:
            if request_id in self._cancel_flags:
                del self._cancel_flags[request_id]

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

        logger.info(f"Creating chat session: user_id={user_id}, rag_type={rag_type}, title={title}")
        session = self.session_repository.create(user_id=user_id, title=title, rag_type=rag_type)
        logger.info(f"Chat session created: session_id={session.id}, user_id={user_id}")
        return session

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
        logger.info(f"Deleting chat session: session_id={session_id}")
        result = self.session_repository.delete(session_id)
        if result:
            logger.info(f"Chat session deleted: session_id={session_id}")
        else:
            logger.warning(f"Chat session deletion failed: session_id={session_id} not found")
        return result

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
        logger.info(
            f"Processing chat message: user_id={user_id}, session_id={session_id}, "
            f"message_length={len(message)}, rag_type={rag_type}"
        )

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
        logger.debug(f"User message stored: message_id={user_message.id}, session_id={session.id}")

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
        logger.debug(
            f"Assistant message stored: message_id={assistant_message.id}, session_id={session.id}"
        )

        logger.info(
            f"Chat message processed: user_id={user_id}, session_id={session.id}, "
            f"context_chunks={len(context_chunks)}"
        )

        return ChatResponse(
            answer=answer,
            context=context_chunks,
            session_id=session.id,
            user_message=user_message,
            assistant_message=assistant_message,
        )

    def stream_chat_response(
        self,
        user_id: int,
        message: str,
        llm_provider: LlmProvider,
        session_id: int | None = None,
        rag_type: str = "vector",
        request_id: str | None = None,
    ) -> Generator[StreamEvent, None, None]:
        """
        Stream a chat response with full session management.

        This method handles the complete workflow for streaming chat:
        - Get or create session
        - Build conversation history
        - Store user message
        - Stream LLM response
        - Store assistant response
        - Emit stream events

        Args:
            user_id: ID of the user sending the message
            message: The user's message
            llm_provider: LLM provider for generating responses
            session_id: Optional existing session ID
            rag_type: Type of RAG to use (vector or graph)
            request_id: Optional unique identifier for this streaming request (for cancellation)

        Yields:
            StreamEvent objects with chunk data or completion metadata
        """
        logger.info(
            f"Starting streaming chat: user_id={user_id}, session_id={session_id}, "
            f"message_length={len(message)}, rag_type={rag_type}, request_id={request_id}"
        )

        # Get cancel flag for this request
        cancel_flag = self._get_cancel_flag(request_id) if request_id else None

        try:
            # Get or create session
            session = self.get_or_create_session(
                user_id=user_id,
                session_id=session_id,
                first_message=message,
            )

            # Get conversation history
            messages = self.list_session_messages(session.id)
            conversation_history = [
                {"role": msg.role, "content": msg.content} for msg in messages[-10:]
            ]
            logger.debug(
                f"Retrieved conversation history: session_id={session.id}, message_count={len(messages)}"
            )

            # Store user message
            self.create_message(
                session_id=session.id,
                role="user",
                content=message,
            )

            # TODO: RAG INTEGRATION - Retrieval for Streaming Chat
            # Same as non-streaming chat - retrieve relevant context before streaming
            # See process_chat_message_with_llm() for detailed implementation steps
            # Key difference: Context should be prepended to conversation_history
            # before calling llm_provider.chat_stream()

            # Stream LLM response
            logger.debug(f"Starting LLM streaming: session_id={session.id}")
            full_response = ""
            chunk_count = 0
            cancelled = False

            for chunk in llm_provider.chat_stream(message, conversation_history):
                # Check for cancellation
                if cancel_flag and cancel_flag.is_set():
                    logger.info(
                        f"Stream cancelled: session_id={session.id}, request_id={request_id}, "
                        f"chunks_sent={chunk_count}"
                    )
                    cancelled = True
                    break

                full_response += chunk
                chunk_count += 1
                yield StreamEvent.chunk(chunk)

            if cancelled:
                logger.info(
                    f"Streaming chat cancelled: user_id={user_id}, session_id={session.id}, "
                    f"partial_response_length={len(full_response)}"
                )
                return

            logger.debug(
                f"LLM streaming completed: session_id={session.id}, chunks={chunk_count}, "
                f"response_length={len(full_response)}"
            )

            # Store assistant response
            self.create_message(
                session_id=session.id,
                role="assistant",
                content=full_response,
                metadata={"rag_type": rag_type},
            )

            logger.info(
                f"Streaming chat completed: user_id={user_id}, session_id={session.id}, "
                f"response_length={len(full_response)}"
            )

            # Send completion event
            yield StreamEvent.complete(session_id=session.id, full_response=full_response)

        finally:
            # Clean up cancel flag
            if request_id:
                self._cleanup_cancel_flag(request_id)

    def process_chat_message_with_llm(
        self,
        user_id: int,
        message: str,
        llm_provider: LlmProvider,
        session_id: int | None = None,
        rag_type: str = "vector",
        documents_count: int = 0,
    ) -> ChatResponseDTO:
        """
        Process a chat message and return a DTO (non-streaming).

        This method handles the complete chat workflow:
        - Get or create session
        - Build conversation history
        - Generate LLM response
        - Store messages
        - Return formatted response

        Args:
            user_id: ID of the user sending the message
            message: The user's message
            llm_provider: LLM provider for generating responses
            session_id: Optional existing session ID
            rag_type: Type of RAG to use (vector or graph)
            documents_count: Number of documents available for context

        Returns:
            ChatResponseDTO ready for JSON serialization
        """
        logger.info(
            f"Processing chat with LLM: user_id={user_id}, session_id={session_id}, "
            f"message_length={len(message)}, rag_type={rag_type}, documents_count={documents_count}"
        )

        # Get or create session
        session = self.get_or_create_session(
            user_id=user_id,
            session_id=session_id,
            first_message=message,
        )

        # Get conversation history
        messages = self.list_session_messages(session.id)
        conversation_history = [
            {"role": msg.role, "content": msg.content} for msg in messages[-10:]
        ]
        logger.debug(
            f"Retrieved conversation history: session_id={session.id}, message_count={len(messages)}"
        )

        # TODO: RAG INTEGRATION - Retrieval for Chat
        # Before generating LLM response, retrieve relevant context from RAG system
        #
        # Implementation steps:
        # 1. Import RAG system: from src.rag.factory import create_rag
        # 2. Initialize RAG with appropriate type:
        #    rag = create_rag(
        #        rag_type=rag_type,  # "vector" or "graph"
        #        embedding_type="ollama",
        #        ...
        #    )
        # 3. Retrieve relevant chunks:
        #    rag_results = rag.retrieve(query=message, top_k=5)
        # 4. Format context for LLM:
        #    context_str = "\n\n".join([
        #        f"[{i+1}] {chunk['text']}"
        #        for i, chunk in enumerate(rag_results)
        #    ])
        # 5. Prepend context to conversation or use system message:
        #    system_message = f"Use the following context to answer:\n{context_str}"
        # 6. Store context metadata in message for later analysis

        # Generate LLM response
        logger.debug(f"Generating LLM response: session_id={session.id}")
        llm_answer = llm_provider.chat(message, conversation_history)
        logger.debug(
            f"LLM response generated: session_id={session.id}, response_length={len(llm_answer)}"
        )

        # Store user message
        self.create_message(
            session_id=session.id,
            role="user",
            content=message,
        )

        # Store assistant response
        self.create_message(
            session_id=session.id,
            role="assistant",
            content=llm_answer,
            metadata={"rag_type": rag_type},
        )

        logger.info(
            f"Chat processed with LLM: user_id={user_id}, session_id={session.id}, "
            f"response_length={len(llm_answer)}"
        )

        # Build response DTO
        return ChatResponseDTO(
            answer=llm_answer,
            context=[],  # No RAG context for now
            session_id=session.id,
            documents_count=documents_count,
        )

    def list_user_sessions_as_dto(self, user_id: int) -> SessionListResponse:
        """
        List all sessions for a user as a DTO.

        Args:
            user_id: The user ID

        Returns:
            SessionListResponse DTO ready for JSON serialization
        """
        sessions = self.list_user_sessions(user_id)
        session_dtos = ChatMapper.sessions_to_dtos(sessions)

        return SessionListResponse(
            sessions=session_dtos,
            count=len(session_dtos),
        )

    def list_session_messages_as_dto(self, session_id: int) -> SessionMessagesResponse:
        """
        List all messages for a session as a DTO.

        Args:
            session_id: The session ID

        Returns:
            SessionMessagesResponse DTO ready for JSON serialization
        """
        messages = self.list_session_messages(session_id)
        message_dtos = ChatMapper.messages_to_dtos(messages)

        return SessionMessagesResponse(
            messages=message_dtos,
            count=len(message_dtos),
        )
