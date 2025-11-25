"""Chat service implementation."""

import json
import threading
from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from shared.cache import Cache
from shared.llm import LlmProvider
from shared.logger import create_logger
from shared.models import ChatMessage, ChatSession
from shared.repositories import ChatMessageRepository, ChatSessionRepository

from .dtos import ChatResponse as ChatResponseDTO, ContextChunk
from .dtos import SessionListResponse, SessionMessagesResponse, StreamEvent
from .exceptions import EmptyMessageError
from .mappers import ChatMapper

logger = create_logger(__name__)


# ChatContext is now imported from dtos as ContextChunk


@dataclass
class ChatResponse:
    """Result of processing a chat message."""

    answer: str
    context: list[ContextChunk]
    session_id: int
    user_message: ChatMessage
    assistant_message: ChatMessage


class ChatService:
    """Service for chat-related business logic."""

    def __init__(
        self,
        session_repository: ChatSessionRepository,
        message_repository: ChatMessageRepository,
        rag_system=None,
        message_publisher=None,
        cache: Cache = None
    ):
        """
        Initialize service with repositories.

        Args:
            session_repository: Chat session repository implementation
            message_repository: Chat message repository implementation
            rag_system: Optional RAG system for context retrieval
            message_publisher: Optional message publisher for async processing
            cache: Optional cache instance for performance optimization
        """
        self.session_repository = session_repository
        self.message_repository = message_repository
        self._rag_system = rag_system
        self._message_publisher = message_publisher
        self._cache = cache
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
        workspace_id: int | None = None,
        title: str | None = None,
        rag_type: str = "vector",
        first_message: str | None = None,
    ) -> ChatSession:
        """
        Create a new chat session.

        Args:
            user_id: The user ID
            workspace_id: Optional workspace ID to associate the session with
            title: Optional session title
            rag_type: Type of RAG to use (vector or graph)
            first_message: Optional first message to use as title if title not provided

        Returns:
            ChatSession: The newly created session
        """
        # Use first_message as title if title not provided
        if not title and first_message:
            title = first_message[:50] + "..." if len(first_message) > 50 else first_message

        logger.info(f"Creating chat session: user_id={user_id}, workspace_id={workspace_id}, rag_type={rag_type}, title={title}")
        session = self.session_repository.create(user_id=user_id, workspace_id=workspace_id, title=title, rag_type=rag_type)
        logger.info(f"Chat session created: session_id={session.id}, user_id={user_id}, workspace_id={workspace_id}")
        return session

    def get_session_by_id(self, session_id: int) -> Optional[ChatSession]:
        """Get chat session by ID."""
        return self.session_repository.get_by_id(session_id)

    def list_user_sessions(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatSession]:
        """List all chat sessions for a user with pagination."""
        return self.session_repository.get_by_user(user_id, skip=skip, limit=limit)

    def list_workspace_sessions(
        self, workspace_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatSession]:
        """List all chat sessions for a workspace with pagination."""
        return self.session_repository.get_by_workspace(workspace_id, skip=skip, limit=limit)

    def update_session(self, session_id: int, **kwargs: str) -> Optional[ChatSession]:
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
        message = self.message_repository.create(
            session_id=session_id, role=role, content=content, extra_metadata=metadata_json
        )

        # Invalidate cache for this session's messages
        if self._cache:
            # Clear common cache patterns for this session
            for limit in [10, 20, 50]:
                cache_key = f"chat_session_messages:{session_id}:{limit}"
                self._cache.delete(cache_key)
            logger.debug(f"Invalidated message cache for session: session_id={session_id}")

        return message

    def get_message_by_id(self, message_id: int) -> Optional[ChatMessage]:
        """Get chat message by ID."""
        return self.message_repository.get_by_id(message_id)

    def list_session_messages(
        self, session_id: int, skip: int = 0, limit: int = 100
    ) -> list[ChatMessage]:
        """List all messages for a chat session with pagination."""
        # Try cache first for recent messages (skip=0, reasonable limit)
        if self._cache and skip == 0 and limit <= 50:
            cache_key = f"chat_session_messages:{session_id}:{limit}"
            cached_messages = self._cache.get(cache_key)
            if cached_messages is not None:
                logger.debug(f"Cache hit for session messages: session_id={session_id}")
                return cached_messages

        # Fetch from database
        messages = self.message_repository.get_by_session(session_id, skip=skip, limit=limit)

        # Cache the result if it's a common query pattern
        if self._cache and skip == 0 and limit <= 50 and messages:
            cache_key = f"chat_session_messages:{session_id}:{limit}"
            self._cache.set(cache_key, messages, ttl=300)  # Cache for 5 minutes
            logger.debug(f"Cached session messages: session_id={session_id}")

        return messages

    def delete_message(self, message_id: int) -> bool:
        """Delete chat message by ID."""
        return self.message_repository.delete(message_id)

    def get_or_create_session(
        self, user_id: int, workspace_id: int | None = None, session_id: int | None = None, first_message: str | None = None
    ) -> ChatSession:
        """
        Get existing session or create a new one.

        Args:
            user_id: The user ID
            workspace_id: Optional workspace ID for new sessions
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
        return self.create_session(user_id=user_id, workspace_id=workspace_id, first_message=first_message)

    def process_chat_message(
        self,
        user_id: int,
        message: str,
        llm_provider: LlmProvider,
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

        # Use the LLM processing method for consistent behavior
        # This method handles RAG querying, LLM generation, and response formatting
        response_dto = self.process_chat_message_with_llm(
            user_id=user_id,
            message=message,
            llm_provider=llm_provider,
            session_id=session_id,
            rag_type=rag_type,
            ignore_rag=False,
            top_k=8
        )

        # Convert DTO to response object
        answer = response_dto.answer
        context_chunks = response_dto.context

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
        workspace_id: int | None = None,
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
                workspace_id=workspace_id,
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

            # RAG INTEGRATION - Retrieval for Streaming Chat
            enhanced_history = conversation_history.copy()
            rag_context_found = False
            if rag_type == "vector" and self._rag_system:
                try:
                    # Query RAG system for relevant context, filtered by workspace
                    workspace_id = session.workspace_id
                    rag_results = self._rag_system.query(message, workspace_id=workspace_id, top_k=8)
                    if rag_results:
                        # Check if we have meaningful context
                        meaningful_context = [result for result in rag_results if result.score > 0.1]
                        if meaningful_context:
                            context_str = "\n\n".join([
                                f"[{i+1}] {result.chunk.text}"
                                for i, result in enumerate(meaningful_context)
                            ])
                            system_message = f"Use the following context to answer the user's question:\n{context_str}"
                            enhanced_history.insert(0, {"role": "system", "content": system_message})
                            rag_context_found = True
                            logger.debug(f"RAG context added for streaming: session_id={session.id}, chunks={len(meaningful_context)}")
                        else:
                            # No meaningful context found - will emit no_context_found event
                            logger.debug(f"No meaningful RAG context found for streaming: session_id={session.id}")
                    else:
                        logger.debug(f"No RAG results found for streaming: session_id={session.id}")
                except Exception as e:
                    logger.warning(f"RAG retrieval failed for streaming: {e}")

            # If no context found and RAG is enabled, store query for auto-retry
            if not rag_context_found and rag_type == "vector" and self._rag_system:
                # Store the original query for potential auto-retry after document upload/Wikipedia fetch
                self._store_pending_rag_query(
                    workspace_id=workspace_id,
                    session_id=session.id,
                    user_id=user_id,
                    query=message,
                    request_id=request_id or ""
                )
                logger.info(f"No context found for query: session_id={session.id}, query='{message[:50]}...', stored for auto-retry")

            # Stream LLM response
            logger.debug(f"Starting LLM streaming: session_id={session.id}")
            full_response = ""
            chunk_count = 0
            cancelled = False

            try:
                for chunk in llm_provider.chat_stream(message, enhanced_history):
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
            except AttributeError:
                # If chat_stream is not available, fall back to regular chat
                logger.warning("LLM provider does not support streaming, falling back to regular chat")
                full_response = llm_provider.chat(message, enhanced_history)
                # Yield the full response as a single chunk
                yield StreamEvent.chunk(full_response)

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

    def send_message(
        self,
        workspace_id: int | None,
        session_id: int | None,
        user_id: int,
        content: str,
        message_type: str = "user",
        ignore_rag: bool = False,
    ) -> str:
        """
        Send a chat message to a workspace session.

        This method handles storing the user message and triggering the async
        chat processing workflow.

        Args:
            workspace_id: ID of the workspace
            session_id: ID of the chat session
            user_id: ID of the user sending the message
            content: Message content
            message_type: Type of message ("user" or "system")
            ignore_rag: Whether to skip RAG processing

        Returns:
            Message ID of the stored user message
        """
        # For WebSocket connections, session_id might be None initially
        # We'll create a temporary session or handle this case
        actual_session_id: int
        if session_id is None:
            # Create a temporary session for WebSocket messages
            temp_session = self.create_session(
                user_id=user_id,
                workspace_id=workspace_id,
                title=f"WebSocket Session - {content[:50]}..."
            )
            actual_session_id = temp_session.id
        else:
            actual_session_id = session_id

        logger.info(
            f"Sending chat message: workspace_id={workspace_id}, session_id={actual_session_id}, "
            f"user_id={user_id}, message_type={message_type}, ignore_rag={ignore_rag}"
        )

        # Validate message
        self.validate_message(content)

        # Store user message
        user_message = self.create_message(
            session_id=actual_session_id,
            role=message_type,
            content=content,
        )
        logger.debug(f"User message stored: message_id={user_message.id}")

        # Publish chat.message_received event to trigger async processing
        # This will be handled by a chat orchestrator worker that:
        # 1. Retrieves RAG context (if not ignore_rag)
        # 2. Calls LLM with context
        # 3. Streams response back via WebSocket

        try:
            # Get message publisher from context
            message_publisher = getattr(self, '_message_publisher', None)
            if message_publisher:
                event_data = {
                    "message_id": str(user_message.id),
                    "session_id": actual_session_id,
                    "workspace_id": workspace_id,
                    "user_id": user_id,
                    "content": content,
                    "message_type": message_type,
                    "ignore_rag": ignore_rag,
                    "request_id": f"chat-{actual_session_id}-{user_message.id}",
                }

                message_publisher.publish(
                    routing_key="chat.message_received",
                    message=event_data,
                )

                logger.info(
                    f"Chat message event published: workspace_id={workspace_id}, session_id={actual_session_id}, "
                    f"message_id={user_message.id}, request_id={event_data['request_id']}"
                )
            else:
                logger.warning("Message publisher not available, falling back to synchronous processing")

                # Fallback to synchronous processing if message publisher is not available
                from src.context import create_llm
                llm_provider = create_llm()

                response_dto = self.process_chat_message_with_llm(
                    user_id=user_id,
                    message=content,
                    llm_provider=llm_provider,
                    session_id=session_id,
                    rag_type="vector",
                    ignore_rag=ignore_rag,
                    top_k=8
                )

                logger.info(
                    f"Chat message processed synchronously: workspace_id={workspace_id}, session_id={session_id}, "
                    f"message_id={user_message.id}, response_length={len(response_dto.answer)}"
                )
        except Exception as e:
            logger.error(f"Failed to process chat message: {e}")

        return str(user_message.id)

    def cancel_message(
        self,
        workspace_id: int,
        session_id: int,
        user_id: int,
        message_id: str | None = None,
    ) -> None:
        """
        Cancel a streaming chat message.

        Args:
            workspace_id: ID of the workspace
            session_id: ID of the chat session
            user_id: ID of the user
            message_id: Optional message ID to cancel (for future use)
        """
        logger.info(
            f"Cancelling chat message: workspace_id={workspace_id}, session_id={session_id}, "
            f"user_id={user_id}, message_id={message_id}"
        )

        # For now, we just log the cancellation
        # In a full implementation, this would signal the LLM generation to stop
        # and potentially clean up any partial responses

        logger.info("Chat message cancellation requested")

    def process_chat_message_with_llm(
        self,
        user_id: int,
        message: str,
        llm_provider: LlmProvider,
        session_id: int | None = None,
        rag_type: str = "vector",
        documents_count: int = 0,
        ignore_rag: bool = False,
        top_k: int = 8,
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
            workspace_id=None,  # For now, allow workspace-less sessions for backward compatibility
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

        # RAG INTEGRATION - Retrieval for Chat
        context_chunks = []
        rag_context_found = False
        if not ignore_rag and rag_type == "vector" and self._rag_system:
            try:
                # Query RAG system for relevant context, filtered by workspace
                workspace_id = session.workspace_id
                rag_results = self._rag_system.query(message, workspace_id=workspace_id, top_k=top_k)
                context_chunks = [
                    ContextChunk(
                        text=result.chunk.text,
                        score=result.score,
                        metadata=result.chunk.metadata or {}
                    )
                    for result in rag_results
                ]

                # Check if we have meaningful context (score > threshold)
                meaningful_context = [chunk for chunk in context_chunks if chunk.score > 0.1]
                rag_context_found = len(meaningful_context) > 0

                logger.debug(f"RAG context retrieved: session_id={session.id}, chunks={len(context_chunks)}, meaningful={len(meaningful_context)}")
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")
                context_chunks = []
                rag_context_found = False

        # Format context for LLM if available
        enhanced_history = conversation_history.copy()
        if context_chunks:
            context_str = "\n\n".join([
                f"[{i+1}] {chunk.text}"
                for i, chunk in enumerate(context_chunks)
            ])
            system_message = f"Use the following context to answer the user's question:\n{context_str}"
            enhanced_history.insert(0, {"role": "system", "content": system_message})

        # Generate LLM response
        logger.debug(f"Generating LLM response: session_id={session.id}")
        llm_answer = llm_provider.chat(message, enhanced_history)
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
            context=context_chunks,
            session_id=session.id,
            documents_count=documents_count,
            no_context_found=not rag_context_found and not ignore_rag,
        )

    def _store_pending_rag_query(
        self,
        workspace_id: int | None,
        session_id: int,
        user_id: int,
        query: str,
        request_id: str | None,
    ) -> None:
        """
        Store a query that had no RAG context for potential auto-retry.

        This allows the system to automatically re-submit queries when new
        documents are added or Wikipedia articles are fetched.
        """
        if not workspace_id:
            return  # Only store for workspace-scoped queries

        try:
            # For now, store in a simple in-memory cache
            # In production, this should be stored in database or Redis
            cache_key = f"pending_rag_query:{workspace_id}:{user_id}"
            pending_data = {
                "session_id": session_id,
                "query": query,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
            }

            # Store in instance cache (in production, use Redis/database)
            if not hasattr(self, '_pending_queries'):
                self._pending_queries = {}
            self._pending_queries[cache_key] = pending_data

            print(f"Stored pending RAG query for workspace {workspace_id}, user {user_id}")

        except Exception as e:
            print(f"Failed to store pending RAG query: {e}")

    def get_pending_rag_queries(self, workspace_id: int, user_id: int) -> list[dict]:
        """
        Get pending RAG queries for a workspace and user.
        """
        if not hasattr(self, '_pending_queries'):
            return []

        cache_key = f"pending_rag_query:{workspace_id}:{user_id}"
        pending_data = self._pending_queries.get(cache_key)
        return [pending_data] if pending_data else []

    def clear_pending_rag_queries(self, workspace_id: int, user_id: int) -> None:
        """
        Clear pending RAG queries after successful auto-retry.
        """
        if hasattr(self, '_pending_queries'):
            cache_key = f"pending_rag_query:{workspace_id}:{user_id}"
            self._pending_queries.pop(cache_key, None)

    def retry_pending_rag_queries(
        self,
        workspace_id: int,
        user_id: int,
        llm_provider: LlmProvider,
    ) -> None:
        """
        Retry pending RAG queries that may now have context available.
        """
        pending_queries = self.get_pending_rag_queries(workspace_id, user_id)
        if not pending_queries:
            return

        for pending in pending_queries:
            try:
                print(f"Retrying pending RAG query for workspace {workspace_id}")

                # Re-run the query with current RAG context
                response_dto = self.process_chat_message_with_llm(
                    user_id=user_id,
                    message=pending["query"],
                    llm_provider=llm_provider,
                    session_id=pending["session_id"],
                    rag_type="vector",
                    ignore_rag=False,
                    top_k=8
                )

                # If we got a response with context, clear the pending query
                if response_dto.context and len(response_dto.context) > 0:
                    self.clear_pending_rag_queries(workspace_id, user_id)
                    print(f"Successfully retried RAG query for workspace {workspace_id}")
                    break  # Only retry one query at a time

            except Exception as e:
                print(f"Failed to retry pending RAG query: {e}")

    def _generate_llm_response(
        self,
        message: str,
        context_chunks: list[ContextChunk],
        conversation_history: list[dict],
        llm_provider: LlmProvider,
        rag_context_found: bool
    ) -> str:
        """
        Generate a response using the LLM with optional RAG context.

        Args:
            message: User message
            context_chunks: Relevant context from RAG system
            conversation_history: Previous conversation messages
            llm_provider: LLM provider instance
            rag_context_found: Whether RAG context was available

        Returns:
            Generated response string
        """
        try:
            # Build context from RAG results
            context_text = ""
            if context_chunks:
                context_parts = []
                for i, chunk in enumerate(context_chunks, 1):
                    context_parts.append(f"[Context {i}] {chunk.text}")
                context_text = "\n\n".join(context_parts)

            # Build conversation context
            conversation_context = ""
            if conversation_history:
                # Include last few messages for context
                recent_messages = conversation_history[-6:]  # Last 3 exchanges
                conversation_lines = []
                for msg in recent_messages:
                    role = "User" if msg.get("role") == "user" else "Assistant"
                    content = msg.get("content", "")[:200]  # Truncate long messages
                    conversation_lines.append(f"{role}: {content}")
                conversation_context = "\n".join(conversation_lines)

            # Build prompt
            system_prompt = """You are an intelligent assistant helping users analyze documents and research papers.
You have access to relevant context from the user's documents when available.

Guidelines:
- Be helpful, accurate, and concise
- Cite specific information from provided context when relevant
- If you don't have relevant context, clearly state this and suggest alternatives
- Maintain conversation context and coherence
- Use markdown formatting for better readability"""

            user_prompt = f"User Query: {message}"

            if context_text:
                user_prompt += f"\n\nRelevant Context:\n{context_text}"

            if conversation_context:
                user_prompt += f"\n\nRecent Conversation:\n{conversation_context}"

            # Generate response using LLM
            response = llm_provider.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=1000,
                temperature=0.7
            )

            return response.strip()

        except Exception as e:
            logger.error(f"LLM response generation failed: {e}")
            raise

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
