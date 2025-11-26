"""Chat worker for orchestrating RAG queries and LLM responses."""

import logging
from typing import Any, Dict, List

from shared.config import AppConfig
from shared.database.sql.postgres import PostgresConnection
from shared.llm import create_llm_provider
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.worker import Worker

logger = logging.getLogger(__name__)


class ChatWorker(Worker):
    """Worker for orchestrating chat messages with RAG and LLM."""

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: AppConfig,
    ):
        """Initialize the chat worker."""
        super().__init__(consumer, publisher, config)
        self.db_connection = PostgresConnection(db_url=config.database_url)
        self.db_connection.connect()

        # Create LLM provider with config
        self.llm_provider = create_llm_provider(
            provider="ollama",
            base_url=config.ollama_base_url,
            model=config.ollama_llm_model,
        )

        # Track pending queries: message_id -> query details
        self._pending_queries: Dict[str, Dict[str, Any]] = {}

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process chat-related messages."""
        try:
            event_type = message.get("event_type")
            if event_type == "chat.message_received":
                self._process_chat_message(message)
            elif event_type == "chat.vector_query_completed":
                self._process_vector_query_completed(message)
            elif event_type == "chat.graph_query_completed":
                self._process_graph_query_completed(message)
            elif event_type in ["chat.vector_query_failed", "chat.graph_query_failed"]:
                self._process_query_failed(message)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing chat message: {e}")

    def _process_chat_message(self, message: Dict[str, Any]) -> None:
        """Process a chat message by routing to appropriate query worker."""
        message_id = message.get("message_id")
        session_id = message.get("session_id")
        workspace_id = message.get("workspace_id")
        content = message.get("content", "")
        ignore_rag = message.get("ignore_rag", False)

        if not message_id or not session_id or not workspace_id:
            logger.error("Missing required fields in chat message")
            return

        logger.info(f"Processing chat message {message_id} for session {session_id}")

        try:
            # Determine RAG type from session
            rag_type = self._get_session_rag_type(session_id)

            if ignore_rag or rag_type == "none":
                # Skip RAG, go directly to LLM
                self._generate_llm_response(message_id, session_id, content, [])
                return

            # Store query details for when response comes back
            self._pending_queries[message_id] = {
                "session_id": session_id,
                "workspace_id": workspace_id,
                "content": content,
                "rag_type": rag_type,
            }

            # Route to appropriate query worker
            if rag_type == "vector":
                self._send_vector_query(message_id, session_id, workspace_id, content)
            elif rag_type == "graph":
                self._send_graph_query(message_id, session_id, workspace_id, content)
            else:
                logger.error(f"Unknown RAG type: {rag_type}")
                self._send_error_response(session_id, message_id, f"Unknown RAG type: {rag_type}")

        except Exception as e:
            logger.error(f"Error processing chat message {message_id}: {e}")
            self._send_error_response(session_id, message_id, str(e))

    def _process_vector_query_completed(self, message: Dict[str, Any]) -> None:
        """Process completed vector query results."""
        message_id = message.get("message_id")
        results = message.get("results", [])

        if message_id not in self._pending_queries:
            logger.warning(f"Received vector query completion for unknown message {message_id}")
            return

        query_details = self._pending_queries.pop(message_id)
        self._generate_llm_response(
            message_id,
            query_details["session_id"],
            query_details["content"],
            results
        )

    def _process_graph_query_completed(self, message: Dict[str, Any]) -> None:
        """Process completed graph query results."""
        message_id = message.get("message_id")
        results = message.get("results", [])

        if message_id not in self._pending_queries:
            logger.warning(f"Received graph query completion for unknown message {message_id}")
            return

        query_details = self._pending_queries.pop(message_id)
        self._generate_llm_response(
            message_id,
            query_details["session_id"],
            query_details["content"],
            results
        )

    def _process_query_failed(self, message: Dict[str, Any]) -> None:
        """Process failed query."""
        message_id = message.get("message_id")
        error = message.get("error", "Unknown query error")

        if message_id not in self._pending_queries:
            logger.warning(f"Received query failure for unknown message {message_id}")
            return

        query_details = self._pending_queries.pop(message_id)
        self._send_error_response(query_details["session_id"], message_id, error)

    def _send_vector_query(self, message_id: str, session_id: int, workspace_id: int, content: str) -> None:
        """Send query to vector query worker."""
        # Get RAG config for top_k
        rag_config = self._get_rag_config(workspace_id)
        top_k = rag_config.get("top_k", 8)

        self.publisher.publish_event(
            event_type="chat.vector_query",
            message_id=message_id,
            session_id=session_id,
            workspace_id=workspace_id,
            query=content,
            top_k=top_k,
        )

    def _send_graph_query(self, message_id: str, session_id: int, workspace_id: int, content: str) -> None:
        """Send query to graph query worker."""
        # Get RAG config for query parameters
        rag_config = self._get_rag_config(workspace_id)
        max_hops = rag_config.get("max_hops", 2)

        self.publisher.publish_event(
            event_type="chat.graph_query",
            message_id=message_id,
            session_id=session_id,
            workspace_id=workspace_id,
            query=content,
            max_hops=max_hops,
        )

    def _generate_llm_response(self, message_id: str, session_id: int, content: str, context_results: List[Dict[str, Any]]) -> None:
        """Generate LLM response using context and conversation history."""
        try:
            # Get conversation history
            conversation_history = self._get_conversation_history(session_id)

            # Prepare context
            context_chunks = []
            if context_results:
                context_chunks = [
                    {"text": result.get("content", ""), "score": result.get("score", 0.0)}
                    for result in context_results
                ]

            # Build enhanced history with context
            enhanced_history = conversation_history.copy()
            if context_chunks:
                context_str = "\n\n".join(
                    [f"[{i+1}] {chunk['text']}" for i, chunk in enumerate(context_chunks)]
                )
                system_message = (
                    f"Use the following context to answer the user's question:\n{context_str}"
                )
                enhanced_history.insert(0, {"role": "system", "content": system_message})

            # Check if we have context when RAG was expected
            if not context_chunks and self._pending_queries.get(message_id, {}).get("rag_type") in ["vector", "graph"]:
                # No context found
                self.publisher.publish_event(
                    event_type="chat.no_context_found",
                    session_id=session_id,
                    message_id=message_id,
                    query=content,
                )
                return

            # Generate streaming response
            full_response = ""
            for chunk in self.llm_provider.chat_stream(content, enhanced_history):
                full_response += chunk
                self.publisher.publish_event(
                    event_type="chat.response_chunk",
                    session_id=session_id,
                    message_id=message_id,
                    chunk=chunk,
                )

            # Send completion event
            self.publisher.publish_event(
                event_type="chat.response_complete",
                session_id=session_id,
                message_id=message_id,
                full_response=full_response,
            )

        except Exception as e:
            logger.error(f"Error generating LLM response for message {message_id}: {e}")
            self._send_error_response(session_id, message_id, str(e))

    def _send_error_response(self, session_id: int, message_id: str, error: str) -> None:
        """Send error response."""
        self.publisher.publish_event(
            event_type="chat.error",
            session_id=session_id,
            message_id=message_id,
            error=error,
        )

    def _get_session_rag_type(self, session_id: int) -> str:
        """Get the RAG type for a chat session."""
        try:
            with self.db_connection.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    "SELECT rag_type FROM chat_sessions WHERE id = %s",
                    (session_id,)
                )
                result = cursor.fetchone()
                return result["rag_type"] if result else "vector"
        except Exception as e:
            logger.error(f"Error getting RAG type for session {session_id}: {e}")
            return "vector"

    def _get_conversation_history(self, session_id: int) -> List[Dict[str, Any]]:
        """Get conversation history for a session."""
        try:
            with self.db_connection.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                    (session_id,)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting conversation history for session {session_id}: {e}")
            return []

    def _get_rag_config(self, workspace_id: int) -> Dict[str, Any]:
        """Get RAG configuration for a workspace."""
        try:
            with self.db_connection.get_cursor(as_dict=True) as cursor:
                # Try vector config first
                cursor.execute(
                    "SELECT * FROM vector_rag_configs WHERE workspace_id = %s",
                    (workspace_id,)
                )
                result = cursor.fetchone()
                if result:
                    return result

                # Try graph config
                cursor.execute(
                    "SELECT * FROM graph_rag_configs WHERE workspace_id = %s",
                    (workspace_id,)
                )
                result = cursor.fetchone()
                if result:
                    return result

                # Fallback to old rag_configs table
                cursor.execute(
                    "SELECT * FROM rag_configs WHERE workspace_id = %s",
                    (workspace_id,)
                )
                result = cursor.fetchone()
                return result if result else {}

        except Exception as e:
            logger.error(f"Error getting RAG config for workspace {workspace_id}: {e}")
            return {}


def create_chat_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: AppConfig,
) -> ChatWorker:
    """Create a chat worker."""
    return ChatWorker(consumer, publisher, config)