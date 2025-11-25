"""
Chat Orchestrator Worker - Processes chat messages with RAG and LLM.

Consumes: chat.message_received
Produces: chat.response_chunk, chat.response_complete, chat.error, chat.no_context_found
"""

from dataclasses import asdict, dataclass
from typing import Any

from shared.config import config
from shared.database.sql.postgres import PostgresConnection
from shared.logger import get_logger
from shared.worker.worker import Worker as BaseWorker

logger = get_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
OLLAMA_BASE_URL = config.ollama_base_url
OLLAMA_LLM_MODEL = config.ollama_llm_model
OLLAMA_EMBEDDING_MODEL = config.ollama_embedding_model
QDRANT_URL = f"http://{config.qdrant_host}:{config.qdrant_port}"
WORKER_CONCURRENCY = config.worker_concurrency


@dataclass
class ChatResponseChunkEvent:
    """Event emitted for each chunk of chat response."""

    session_id: int
    message_id: str
    chunk: str


@dataclass
class ChatResponseCompleteEvent:
    """Event emitted when chat response is complete."""

    session_id: int
    message_id: str
    full_response: str


@dataclass
class ChatErrorEvent:
    """Event emitted when chat processing fails."""

    session_id: int
    message_id: str
    error: str


@dataclass
class ChatNoContextFoundEvent:
    """Event emitted when no RAG context is found."""

    session_id: int
    message_id: str
    query: str


class ChatOrchestratorWorker(BaseWorker):
    """Chat orchestrator worker that processes chat messages with RAG and LLM."""

    def __init__(self) -> None:
        """Initialize the chat orchestrator worker."""
        super().__init__(
            worker_name="chat_orchestrator",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="chat.message_received",
            consume_queue="chat.message_received",
            prefetch_count=WORKER_CONCURRENCY,
        )

        self.db_connection = PostgresConnection(db_url=DATABASE_URL)
        self.db_connection.connect()
        self._rag_system = None
        self._llm_provider = None

    def _init_rag_system(self, workspace_id: int) -> None:
        """Initialize RAG system if not already done."""
        if self._rag_system is not None:
            return

        try:
            from shared.database.vector import create_vector_store
            from shared.documents.embedding import create_embedding_encoder
            from shared.orchestrators import VectorRAG

            collection_name = self._get_workspace_collection(workspace_id)
            rag_config = self._get_rag_config(workspace_id)

            vector_store = create_vector_store(
                db_type="qdrant",
                url=QDRANT_URL,
                collection_name=collection_name,
                vector_size=rag_config.get("embedding_dim", 768),
            )

            if not vector_store:
                raise ValueError("Failed to initialize vector store")

            embedder = create_embedding_encoder(
                encoder_type="ollama",
                model=rag_config.get("embedding_model", OLLAMA_EMBEDDING_MODEL),
                base_url=OLLAMA_BASE_URL,
            )

            if not embedder:
                raise ValueError("Failed to initialize embedding encoder")

            self._rag_system = VectorRAG(embedder=embedder, vector_store=vector_store)
            logger.info("RAG system initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            self._rag_system = None
            raise

    def _init_llm_provider(self) -> None:
        """Initialize LLM provider if not already done."""
        if self._llm_provider is not None:
            return
        try:
            from shared.llm import create_llm_provider

            self._llm_provider = create_llm_provider(
                provider_type="ollama",
                base_url=OLLAMA_BASE_URL,
                model_name=OLLAMA_LLM_MODEL,
            )
            logger.info("LLM provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}")
            self._llm_provider = None
            raise

    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process chat.message_received event.
        """
        message_id = str(event_data.get("message_id", ""))
        session_id = int(event_data.get("session_id", 0))
        workspace_id = int(event_data.get("workspace_id", 0))
        content = str(event_data.get("content", ""))
        ignore_rag = bool(event_data.get("ignore_rag", False))

        logger.info("Processing chat message", extra=event_data)

        try:
            self._init_rag_system(workspace_id)
            self._init_llm_provider()

            if not self._llm_provider:
                raise Exception("LLM provider not available")

            rag_config = self._get_rag_config(workspace_id)
            top_k = rag_config.get("top_k", 8)

            context_chunks = []
            if not ignore_rag and self._rag_system:
                rag_results = self._rag_system.query(content, top_k=top_k)
                if rag_results:
                    context_chunks = [
                        {"text": result.chunk.text, "score": result.score} for result in rag_results
                    ]

            if not context_chunks and not ignore_rag:
                event = ChatNoContextFoundEvent(
                    session_id=session_id, message_id=message_id, query=content
                )
                self.publish_event("chat.no_context_found", asdict(event))
                return

            conversation_history = self._get_conversation_history(session_id)

            enhanced_history = conversation_history.copy()
            if context_chunks:
                context_str = "\n\n".join(
                    [f"[{i+1}] {chunk['text']}" for i, chunk in enumerate(context_chunks)]
                )
                system_message = (
                    f"Use the following context to answer the user's question:\n{context_str}"
                )
                enhanced_history.insert(0, {"role": "system", "content": system_message})

            full_response = ""
            for chunk in self._llm_provider.chat_stream(content, enhanced_history):
                full_response += chunk
                chunk_event = ChatResponseChunkEvent(
                    session_id=session_id, message_id=message_id, chunk=chunk
                )
                self.publish_event("chat.response_chunk", asdict(chunk_event))

            complete_event = ChatResponseCompleteEvent(
                session_id=session_id, message_id=message_id, full_response=full_response
            )
            self.publish_event("chat.response_complete", asdict(complete_event))

        except Exception as e:
            logger.error(
                "Failed to process chat message", extra={"message_id": message_id, "error": str(e)}
            )
            error_event = ChatErrorEvent(session_id=session_id, message_id=message_id, error=str(e))
            self.publish_event("chat.error", asdict(error_event))

    def _get_conversation_history(self, session_id: int) -> list[dict]:
        """Get conversation history from the database."""
        logger.info("Getting conversation history", extra={"session_id": session_id})
        try:
            with self.db_connection.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    "SELECT role, content FROM chat_messages WHERE session_id = %s ORDER BY created_at ASC",
                    (session_id,),
                )
                return cursor.fetchall()  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(
                "Failed to get conversation history",
                extra={"session_id": session_id, "error": str(e)},
            )
            return []

    def _get_workspace_collection(self, workspace_id: int) -> str:
        """Get the Qdrant collection name for the workspace."""
        try:
            with self.db_connection.get_cursor(as_dict=True) as cursor:
                cursor.execute(
                    "SELECT rag_collection FROM workspaces WHERE id = %s", (workspace_id,)
                )
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"Workspace {workspace_id} not found")
                return result["rag_collection"]  # type: ignore[no-any-return]
        except Exception as e:
            raise ValueError(
                f"Failed to get workspace collection for workspace {workspace_id}: {e}"
            ) from e

    def _get_rag_config(self, workspace_id: int) -> dict:
        """Get the RAG config for the workspace."""
        try:
            with self.db_connection.get_cursor(as_dict=True) as cursor:
                cursor.execute("SELECT * FROM rag_configs WHERE workspace_id = %s", (workspace_id,))
                result = cursor.fetchone()
                if not result:
                    raise ValueError(f"RAG config for workspace {workspace_id} not found")
                return result  # type: ignore[no-any-return]
        except Exception as e:
            raise ValueError(f"Failed to get RAG config for workspace {workspace_id}: {e}") from e


def main() -> None:
    """Main entry point."""
    worker = ChatOrchestratorWorker()
    worker.start()


if __name__ == "__main__":
    main()
