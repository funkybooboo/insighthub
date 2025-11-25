"""
Chat Orchestrator Worker - Processes chat messages with RAG and LLM.

Consumes: chat.message_received
Produces: chat.response_chunk, chat.response_complete, chat.error, chat.no_context_found
"""

from dataclasses import asdict, dataclass
from typing import Any

from shared.config import config
from shared.logger import create_logger
from shared.messaging import RabbitMQPublisher
from shared.types.common import PayloadDict
from shared.worker import Worker

logger = create_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
OLLAMA_BASE_URL = config.ollama_base_url
OLLAMA_LLM_MODEL = "llama3.2"  # Hardcoded for now
OLLAMA_EMBEDDING_MODEL = config.ollama_embedding_model
QDRANT_URL = f"http://{config.vector_store.qdrant_host}:{config.vector_store.qdrant_port}"
QDRANT_COLLECTION = config.vector_store.qdrant_collection_name
WORKER_CONCURRENCY = config.worker_concurrency


@dataclass
class ChatResponseChunkEvent:
    """Event emitted for each chunk of chat response."""

    session_id: int
    message_id: str
    request_id: str
    chunk: str


@dataclass
class ChatResponseCompleteEvent:
    """Event emitted when chat response is complete."""

    session_id: int
    message_id: str
    request_id: str
    full_response: str


@dataclass
class ChatErrorEvent:
    """Event emitted when chat processing fails."""

    session_id: int
    message_id: str
    request_id: str
    error: str


@dataclass
class ChatNoContextFoundEvent:
    """Event emitted when no RAG context is found."""

    session_id: int
    message_id: str
    request_id: str
    query: str


class ChatOrchestratorWorker(Worker):
    """Chat orchestrator worker that processes chat messages with RAG and LLM."""

    def __init__(self) -> None:
        """Initialize the chat orchestrator worker."""
        super().__init__(
            worker_name="chat_orchestrator",
            rabbitmq_url=config.rabbitmq_url,
            exchange=config.rabbitmq_exchange,
            exchange_type="topic",
            consume_routing_key="chat.message_received",
            consume_queue="chat.message_received",
            prefetch_count=config.worker_concurrency,
        )

        # Initialize components
        self._database_url = config.database_url
        self._ollama_base_url = config.ollama_base_url
        self._ollama_llm_model = "llama3.2"  # Hardcoded for now, could be added to config
        self._ollama_embedding_model = config.ollama_embedding_model
        self._qdrant_url = config.qdrant_url
        self._qdrant_collection = config.qdrant_collection_name

        # Initialize RAG system and LLM (lazy loaded in process_event)
        self._rag_system = None
        self._llm_provider = None

    def _init_rag_system(self):
        """Initialize RAG system if not already done."""
        if self._rag_system is not None:
            return

        try:
            # Import here to avoid import errors if dependencies not available
            from shared.database.vector import create_vector_database
            from shared.documents.embedding import create_embedding_encoder
            from shared.orchestrators import VectorRAG

            # Create vector database
            vector_db = create_vector_database(
                db_type="qdrant",
                url=self._qdrant_url,
                collection_name=self._qdrant_collection,
                vector_size=768,  # Default embedding dimension
            )

            if not vector_db:
                logger.warning("Failed to initialize vector database")
                return

            # Create embedding encoder
            embedder = create_embedding_encoder(
                encoder_type="ollama",
                model=self._ollama_embedding_model,
                base_url=self._ollama_base_url,
            )

            if not embedder:
                logger.warning("Failed to initialize embedding encoder")
                return

            # Create VectorRAG orchestrator
            self._rag_system = VectorRAG(embedder=embedder, vector_store=vector_db)
            logger.info("RAG system initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            self._rag_system = None

    def _init_llm_provider(self):
        """Initialize LLM provider if not already done."""
        if self._llm_provider is not None:
            return

        try:
            # Import here to avoid import errors if dependencies not available
            from shared.llm import create_llm_provider

            self._llm_provider = create_llm_provider(
                provider_type="ollama",
                base_url=self._ollama_base_url,
                model_name=self._ollama_llm_model,
            )
            logger.info("LLM provider initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}")
            self._llm_provider = None

    def process_event(self, event_data: PayloadDict) -> None:
        """
        Process chat.message_received event.

        Args:
            event_data: Parsed event data as dictionary
        """
        message_id = str(event_data.get("message_id", ""))
        session_id = int(event_data.get("session_id", 0))
        workspace_id = int(event_data.get("workspace_id", 0))
        user_id = int(event_data.get("user_id", 0))
        content = str(event_data.get("content", ""))
        message_type = str(event_data.get("message_type", "user"))
        ignore_rag = bool(event_data.get("ignore_rag", False))
        request_id = str(event_data.get("request_id", f"chat-{session_id}-{message_id}"))

        logger.info(
            "Processing chat message",
            message_id=message_id,
            session_id=session_id,
            workspace_id=workspace_id,
            user_id=user_id,
            request_id=request_id,
            ignore_rag=ignore_rag,
        )

        try:
            # Initialize components
            self._init_rag_system()
            self._init_llm_provider()

            if not self._llm_provider:
                raise Exception("LLM provider not available")

            # Retrieve RAG context if not ignored
            context_chunks = []
            rag_context_found = False

            if not ignore_rag and self._rag_system:
                try:
                    # Query RAG system for relevant context
                    rag_results = self._rag_system.query(content, top_k=8)
                    if rag_results:
                        # Filter for meaningful context (score > 0.1)
                        meaningful_context = [result for result in rag_results if result.score > 0.1]
                        if meaningful_context:
                            context_chunks = [
                                {
                                    "text": result.chunk.text,
                                    "score": result.score,
                                    "metadata": result.chunk.metadata or {}
                                }
                                for result in meaningful_context
                            ]
                            rag_context_found = True
                            logger.debug(f"RAG context found: {len(context_chunks)} chunks")
                        else:
                            logger.debug("No meaningful RAG context found")
                    else:
                        logger.debug("No RAG results found")
                except Exception as e:
                    logger.warning(f"RAG retrieval failed: {e}")

            # Emit no_context_found event if no context and RAG enabled
            if not rag_context_found and not ignore_rag and self._rag_system:
                no_context_event = ChatNoContextFoundEvent(
                    session_id=session_id,
                    message_id=message_id,
                    request_id=request_id,
                    query=content,
                )
                self.publish_event("chat.no_context_found", asdict(no_context_event))
                logger.info("Emitted chat.no_context_found event")

            # Prepare conversation history (simplified - in production would fetch from DB)
            conversation_history = []

            # Format context for LLM if available
            enhanced_history = conversation_history.copy()
            if context_chunks:
                context_str = "\n\n".join([
                    f"[{i+1}] {chunk['text']}"
                    for i, chunk in enumerate(context_chunks)
                ])
                system_message = f"Use the following context to answer the user's question:\n{context_str}"
                enhanced_history.insert(0, {"role": "system", "content": system_message})

            # Generate LLM response with streaming
            full_response = ""
            try:
                for chunk in self._llm_provider.chat_stream(content, enhanced_history):
                    full_response += chunk

                    # Emit chunk event
                    chunk_event = ChatResponseChunkEvent(
                        session_id=session_id,
                        message_id=message_id,
                        request_id=request_id,
                        chunk=chunk,
                    )
                    self.publish_event("chat.response_chunk", asdict(chunk_event))

                # Emit completion event
                complete_event = ChatResponseCompleteEvent(
                    session_id=session_id,
                    message_id=message_id,
                    request_id=request_id,
                    full_response=full_response,
                )
                self.publish_event("chat.response_complete", asdict(complete_event))

                logger.info(
                    "Chat response completed",
                    message_id=message_id,
                    session_id=session_id,
                    request_id=request_id,
                    response_length=len(full_response),
                )

            except AttributeError:
                # If chat_stream is not available, fall back to regular chat
                logger.warning("LLM provider does not support streaming, falling back to regular chat")
                full_response = self._llm_provider.chat(content, enhanced_history)

                # Emit completion event with full response
                complete_event = ChatResponseCompleteEvent(
                    session_id=session_id,
                    message_id=message_id,
                    request_id=request_id,
                    full_response=full_response,
                )
                self.publish_event("chat.response_complete", asdict(complete_event))

                logger.info(
                    "Chat response completed (non-streaming)",
                    message_id=message_id,
                    session_id=session_id,
                    request_id=request_id,
                    response_length=len(full_response),
                )

        except Exception as e:
            logger.error(
                "Failed to process chat message",
                message_id=message_id,
                session_id=session_id,
                request_id=request_id,
                error=str(e),
            )

            # Emit error event
            error_event = ChatErrorEvent(
                session_id=session_id,
                message_id=message_id,
                request_id=request_id,
                error=str(e),
            )
            self.publish_event("chat.error", asdict(error_event))


def main() -> None:
    """Main entry point."""
    worker = ChatOrchestratorWorker()
    worker.start()


if __name__ == "__main__":
    main()