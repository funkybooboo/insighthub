"""Chat query worker for processing user queries with RAG."""

from flask_socketio import SocketIO

from src.infrastructure.llm import LlmProvider
from src.infrastructure.logger import create_logger
from src.infrastructure.rag.workflows.factory import WorkflowFactory
from src.infrastructure.repositories.chat_messages import ChatMessageRepository
from src.infrastructure.repositories.chat_sessions import ChatSessionRepository
from src.infrastructure.repositories.workspaces import WorkspaceRepository
from src.workers.tasks import run_async

logger = create_logger(__name__)


class ChatQueryWorker:
    """
    Chat query worker that processes user messages with RAG in background threads.

    The worker:
    1. Retrieves conversation history from the session
    2. Executes QueryWorkflow to retrieve relevant context from workspace documents
    3. Formats context and builds prompt with conversation history
    4. Generates LLM response using streaming
    5. Streams response chunks to client via WebSocket
    6. Saves complete assistant message to database
    """

    def __init__(
        self,
        message_repository: ChatMessageRepository,
        session_repository: ChatSessionRepository,
        workspace_repository: WorkspaceRepository,
        socketio: SocketIO,
        llm_provider: LlmProvider,
    ):
        """Initialize the chat query worker.

        Args:
            message_repository: Chat message repository for database operations
            session_repository: Chat session repository for session info
            workspace_repository: Workspace repository for RAG config lookup
            socketio: Socket.IO instance for real-time streaming
            llm_provider: LLM provider for text generation
        """
        self.message_repository = message_repository
        self.session_repository = session_repository
        self.workspace_repository = workspace_repository
        self.socketio = socketio
        self.llm_provider = llm_provider

    def process_query(
        self,
        session_id: int,
        workspace_id: int,
        query_text: str,
        user_id: int,
    ) -> None:
        """Start query processing in a background thread.

        Args:
            session_id: Chat session ID
            workspace_id: Workspace ID for context retrieval
            query_text: User's query text
            user_id: ID of the user making the query
        """
        logger.info(f"Starting background query processing for session {session_id}")

        # Execute query in background thread
        run_async(self._process_query_pipeline, session_id, workspace_id, query_text, user_id)

    def _process_query_pipeline(
        self,
        session_id: int,
        workspace_id: int,
        query_text: str,
        user_id: int,
    ) -> None:
        """Execute the chat query pipeline.

        Args:
            session_id: Chat session ID
            workspace_id: Workspace ID for context retrieval
            query_text: User's query text
            user_id: ID of the user making the query
        """
        try:
            # Broadcast query start
            self._broadcast_status(session_id, user_id, "processing", "Retrieving relevant context")

            # Retrieve conversation history
            logger.info(f"Retrieving conversation history for session {session_id}")
            conversation_history = self._get_conversation_history(session_id)

            # Get workspace RAG configuration
            logger.info(f"Looking up workspace {workspace_id} RAG config")
            workspace = self.workspace_repository.get_by_id(workspace_id)
            if not workspace:
                raise Exception(f"Workspace {workspace_id} not found")

            rag_config = self._build_rag_config(workspace)
            logger.info(f"Using RAG type: {rag_config.get('rag_type')}")

            # Create workflow dynamically based on workspace RAG config
            query_workflow = WorkflowFactory.create_query_workflow(rag_config)

            # Execute RAG query workflow to get relevant context
            logger.info(f"Executing query workflow for workspace {workspace_id}")
            context_chunks = query_workflow.execute(
                query_text=query_text,
                top_k=5,
                filters={"workspace_id": str(workspace_id)},
            )

            # Format context from retrieved chunks
            context_text = self._format_context(context_chunks)

            logger.info(f"Retrieved {len(context_chunks)} relevant chunks")

            # Build prompt with context and conversation history
            prompt = self._build_prompt(query_text, context_text)

            # Broadcast generation start
            self._broadcast_status(session_id, user_id, "generating", "Generating response")

            # Generate streaming response
            logger.info(f"Generating streaming response for session {session_id}")
            full_response = self._generate_streaming_response(
                session_id, user_id, prompt, conversation_history
            )

            # Save assistant message to database
            logger.info(f"Saving assistant message for session {session_id}")
            self.message_repository.create(
                session_id=session_id,
                role="assistant",
                content=full_response,
                extra_metadata=f"Retrieved {len(context_chunks)} chunks",
            )

            # Broadcast completion
            self._broadcast_status(session_id, user_id, "completed", "Response generated")

            logger.info(f"Query processing completed for session {session_id}")

        except Exception as e:
            logger.error(f"Query processing failed for session {session_id}: {e}", exc_info=True)

            # Broadcast error
            self._broadcast_status(
                session_id,
                user_id,
                "failed",
                f"Query processing failed: {str(e)}",
                error=str(e),
            )

    def _build_rag_config(self, workspace: object) -> dict:
        """Build RAG configuration dictionary from workspace model.

        Args:
            workspace: Workspace model with RAG configuration

        Returns:
            RAG configuration dictionary for WorkflowFactory
        """
        # Extract RAG config from workspace model
        # Default to vector RAG if not specified
        return {
            "rag_type": getattr(workspace, "rag_type", "vector"),
            "embedder_type": getattr(workspace, "embedder_type", "ollama"),
            "embedder_config": getattr(workspace, "embedder_config", {
                "base_url": "http://localhost:11434",
                "model_name": "nomic-embed-text",
            }),
            "vector_store_type": getattr(workspace, "vector_store_type", "qdrant"),
            "vector_store_config": getattr(workspace, "vector_store_config", {
                "host": "localhost",
                "port": 6333,
                "collection_name": f"workspace_{workspace.id}",
            }),
            "enable_reranking": getattr(workspace, "enable_reranking", False),
            "reranker_type": getattr(workspace, "reranker_type", "dummy"),
            "reranker_config": getattr(workspace, "reranker_config", {}),
        }

    def _get_conversation_history(self, session_id: int) -> list[dict[str, str]]:
        """Retrieve conversation history for the session.

        Args:
            session_id: Chat session ID

        Returns:
            List of message dicts with role and content
        """
        try:
            # Get recent messages (limit to last 20 for context window)
            messages = self.message_repository.get_by_session(session_id, skip=0, limit=20)

            # Format as list of dicts for LLM provider
            history = []
            for msg in reversed(messages):  # Reverse to get chronological order
                history.append({"role": msg.role, "content": msg.content})

            return history

        except Exception as e:
            logger.warning(f"Failed to retrieve conversation history: {e}")
            return []

    def _format_context(self, context_chunks: list) -> str:
        """Format retrieved chunks into context text.

        Args:
            context_chunks: List of ChunkData objects from query workflow

        Returns:
            Formatted context text
        """
        if not context_chunks:
            return "No relevant context found in the workspace documents."

        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            # Each chunk should have text and metadata
            chunk_text = chunk.get("text", chunk.get("content", ""))
            source = chunk.get("metadata", {}).get("filename", "Unknown")
            score = chunk.get("score", 0.0)

            context_parts.append(
                f"[Document {i}] (Source: {source}, Relevance: {score:.3f})\n{chunk_text}"
            )

        return "\n\n".join(context_parts)

    def _build_prompt(self, query_text: str, context_text: str) -> str:
        """Build prompt with context for LLM.

        Args:
            query_text: User's query
            context_text: Formatted context from retrieved chunks

        Returns:
            Complete prompt with instructions and context
        """
        prompt = f"""You are a helpful AI assistant with access to relevant documents.
Use the context below to answer the user's question. If the context doesn't contain
relevant information, say so clearly.

Context:
{context_text}

User Question: {query_text}

Please provide a clear, helpful answer based on the context provided."""

        return prompt

    def _generate_streaming_response(
        self,
        session_id: int,
        user_id: int,
        prompt: str,
        conversation_history: list[dict[str, str]],
    ) -> str:
        """Generate streaming LLM response and broadcast chunks.

        Args:
            session_id: Chat session ID
            user_id: User ID
            prompt: Complete prompt with context
            conversation_history: Conversation history for context

        Returns:
            Full generated response text
        """
        full_response = ""

        try:
            # Stream response from LLM
            for chunk in self.llm_provider.chat_stream(
                message=prompt, conversation_history=conversation_history
            ):
                full_response += chunk

                # Broadcast chunk to client
                self._broadcast_chunk(session_id, user_id, chunk)

            return full_response

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            error_message = f"I encountered an error while generating the response: {str(e)}"
            self._broadcast_chunk(session_id, user_id, error_message)
            return error_message

    def _broadcast_status(
        self,
        session_id: int,
        user_id: int,
        status: str,
        message: str,
        error: str | None = None,
    ) -> None:
        """Broadcast query processing status to client.

        Args:
            session_id: Chat session ID
            user_id: User ID
            status: Processing status
            message: Status message
            error: Error message if failed
        """
        try:
            status_data = {
                "session_id": session_id,
                "user_id": user_id,
                "status": status,
                "message": message,
                "error": error,
            }

            room = f"user_{user_id}"
            self.socketio.emit("chat_status", status_data, to=room, namespace="/")

        except Exception as e:
            logger.error(f"Failed to broadcast status: {e}")

    def _broadcast_chunk(self, session_id: int, user_id: int, chunk: str) -> None:
        """Broadcast response chunk to client.

        Args:
            session_id: Chat session ID
            user_id: User ID
            chunk: Text chunk to broadcast
        """
        try:
            chunk_data = {
                "session_id": session_id,
                "user_id": user_id,
                "chunk": chunk,
            }

            room = f"user_{user_id}"
            self.socketio.emit("chat_chunk", chunk_data, to=room, namespace="/")

        except Exception as e:
            logger.error(f"Failed to broadcast chunk: {e}")


# Global worker instance (will be initialized in context)
_chat_query_worker: ChatQueryWorker | None = None


def get_chat_query_worker() -> ChatQueryWorker:
    """Get the global chat query worker instance."""
    if _chat_query_worker is None:
        raise RuntimeError(
            "Chat query worker not initialized. Call initialize_chat_query_worker() first."
        )
    return _chat_query_worker


def initialize_chat_query_worker(
    message_repository: ChatMessageRepository,
    session_repository: ChatSessionRepository,
    workspace_repository: WorkspaceRepository,
    socketio: SocketIO,
    llm_provider: LlmProvider,
) -> ChatQueryWorker:
    """Initialize the global chat query worker instance.

    Args:
        message_repository: Chat message repository
        session_repository: Chat session repository
        workspace_repository: Workspace repository for RAG config lookup
        socketio: Socket.IO instance
        llm_provider: LLM provider for text generation

    Returns:
        The initialized chat query worker
    """
    global _chat_query_worker
    _chat_query_worker = ChatQueryWorker(
        message_repository, session_repository, workspace_repository, socketio, llm_provider
    )
    return _chat_query_worker
