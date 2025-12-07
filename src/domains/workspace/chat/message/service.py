"""Chat message service."""

from typing import Any, Callable, Optional

from returns.result import Failure, Result, Success

from src.domains.workspace.chat.message.data_access import ChatMessageDataAccess
from src.domains.workspace.chat.message.models import ChatMessage
from src.domains.workspace.chat.session.data_access import ChatSessionDataAccess
from src.domains.workspace.data_access import WorkspaceDataAccess
from src.domains.workspace.rag_config_provider import RagConfigProviderFactory
from src.infrastructure.llm.llm_provider import LlmProvider
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.query import QueryWorkflowFactory
from src.infrastructure.types import (
    DatabaseError,
    NotFoundError,
    Pagination,
    PaginatedResult,
    ValidationError,
)

logger = create_logger(__name__)


class ChatMessageService:
    """Service for managing chat message."""

    def __init__(
        self,
        data_access: ChatMessageDataAccess,
        session_data_access: ChatSessionDataAccess,
        workspace_data_access: WorkspaceDataAccess,
        llm_provider: LlmProvider,
        config_provider_factory: RagConfigProviderFactory,
    ):
        """Initialize service with data access layers."""
        self.data_access = data_access
        self.session_data_access = session_data_access
        self.workspace_data_access = workspace_data_access
        self.llm_provider = llm_provider
        self.config_provider_factory = config_provider_factory

    def create_message(
        self,
        session_id: int,
        role: str,
        content: str,
        extra_metadata: Optional[dict] = None,
    ) -> Result[ChatMessage, ValidationError | DatabaseError]:
        """
        Create a new chat message.

        Args:
            session_id: The session ID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            extra_metadata: Additional metadata

        Returns:
            Result with ChatMessage on success or ValidationError/DatabaseError on failure
        """
        logger.info(
            f"Creating chat message: session_id={session_id}, role='{role}', content_length={len(content)}"
        )

        # Validate inputs
        if not content or not content.strip():
            logger.error(f"Message creation failed: empty content (session_id={session_id})")
            return Failure(ValidationError("Message content cannot be empty", field="content"))

        if len(content.strip()) > 10000:  # Reasonable limit for message content
            logger.error(
                f"Message creation failed: content too long {len(content)} chars (session_id={session_id})"
            )
            return Failure(
                ValidationError("Message content too long (max 10000 characters)", field="content")
            )

        if role not in ["user", "assistant", "system"]:
            logger.error(
                f"Message creation failed: invalid role '{role}' (session_id={session_id})"
            )
            return Failure(
                ValidationError(
                    "Invalid message role. Must be 'user', 'assistant', or 'system'", field="role"
                )
            )

        # Serialize extra_metadata to JSON string if provided
        extra_metadata_str = None
        if extra_metadata:
            import json

            extra_metadata_str = json.dumps(extra_metadata)

        create_result = self.data_access.create(
            session_id, role, content.strip(), extra_metadata_str
        )
        if isinstance(create_result, Failure):
            return Failure(create_result.failure())

        message = create_result.unwrap()
        logger.info(f"Chat message created: message_id={message.id}, session_id={session_id}")

        return Success(message)

    def get_message(self, message_id: int) -> Optional[ChatMessage]:
        """Get message by ID."""
        return self.data_access.get_by_id(message_id)

    def get_session_messages(
        self, session_id: int, pagination: Pagination
    ) -> PaginatedResult[ChatMessage]:
        """Get message for a session."""
        skip, limit = pagination.offset_limit()
        logger.info(
            f"Retrieving session message: session_id={session_id}, skip={skip}, limit={limit}"
        )

        # Validation is performed at the route level
        result = self.data_access.get_by_session(session_id, pagination)

        logger.info(
            f"Retrieved {result.current_page_size} message for session {session_id} "
            f"(total: {result.total_count})"
        )

        return result

    def delete_message(self, message_id: int) -> bool:
        """Delete a message."""
        logger.info(f"Deleting chat message: message_id={message_id}")

        deleted = self.data_access.delete(message_id)

        if deleted:
            logger.info(f"Chat message deleted: message_id={message_id}")
        else:
            logger.warning(
                f"Chat message deletion failed: message not found (message_id={message_id})"
            )

        return deleted

    def send_message_with_rag(
        self,
        session_id: int,
        message_content: str,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> Result[tuple[ChatMessage, ChatMessage], NotFoundError | ValidationError]:
        """Send a message with RAG context and get streaming LLM response.

        Args:
            session_id: Chat session ID
            message_content: User message content
            stream_callback: Optional callback for streaming chunks

        Returns:
            Result with tuple of (user_message, assistant_message) on success or error on failure
        """
        logger.info(f"Sending message with RAG: session_id={session_id}")

        # Get session
        session = self.session_data_access.get_by_id(session_id)
        if not session:
            return Failure(NotFoundError("chat_session", session_id))

        # Create user message
        user_message_result = self.create_message(session_id, "user", message_content)
        if isinstance(user_message_result, Failure):
            return Failure(user_message_result.failure())

        user_message = user_message_result.unwrap()

        # Build conversation history (last 10 messages for context)
        # Get a large enough page to include recent history
        history_pagination = Pagination.create(skip=0, limit=100).unwrap()
        all_messages_result = self.data_access.get_by_session(session_id, history_pagination)
        all_messages = all_messages_result.items
        history_messages = all_messages[-11:-1] if len(all_messages) > 1 else []
        conversation_history = [
            {"role": msg.role, "content": msg.content} for msg in history_messages
        ]

        # Query RAG for relevant context if session has a workspace
        rag_context = ""
        if session.workspace_id:
            try:
                rag_context = self._retrieve_rag_context(session.workspace_id, message_content)
            except Exception as e:
                logger.warning(f"Failed to retrieve RAG context: {e}")

        # Augment user message with RAG context
        augmented_message = message_content
        if rag_context:
            augmented_message = f"{message_content}{rag_context}\n\nPlease answer the question using the context provided above."

        # Stream response from LLM
        response_chunks: list[str] = []
        for chunk in self.llm_provider.chat_stream(augmented_message, conversation_history):
            if stream_callback:
                stream_callback(chunk)
            response_chunks.append(chunk)

        # Save assistant response
        assistant_content = "".join(response_chunks)
        assistant_message_result = self.create_message(session_id, "assistant", assistant_content)
        if isinstance(assistant_message_result, Failure):
            return Failure(assistant_message_result.failure())

        assistant_message = assistant_message_result.unwrap()

        logger.info(
            f"Message sent with RAG: user_message_id={user_message.id}, assistant_message_id={assistant_message.id}"
        )

        return Success((user_message, assistant_message))

    def _retrieve_rag_context(self, workspace_id: int, query_text: str) -> str:
        """Retrieve RAG context from workspace documents.

        Args:
            workspace_id: Workspace ID
            query_text: Query text

        Returns:
            Formatted RAG context string
        """
        # Get workspace
        workspace = self.workspace_data_access.get_by_id(workspace_id)
        if not workspace:
            return ""

        # Use provider pattern to build query configuration
        provider = self.config_provider_factory.get_provider(workspace.rag_type)
        if not provider:
            logger.warning(f"Unknown RAG type: {workspace.rag_type}")
            return ""

        rag_config = provider.build_query_settings(workspace_id)

        # Create and execute query workflow
        workflow = QueryWorkflowFactory.create(rag_config)
        top_k = rag_config.get("top_k", 5)
        chunks = workflow.execute(
            query_text=query_text,
            top_k=top_k,
            filters={"workspace_id": str(workspace.id)},
        )

        if not chunks:
            return ""

        # Format context
        context_parts = ["\n\nRelevant context from documents:\n"]
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"\n[{i}] {chunk.text}\n")

        return "".join(context_parts)
