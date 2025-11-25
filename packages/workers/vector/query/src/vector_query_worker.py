"""Vector query worker for vector-based retrieval."""

import logging
from typing import Any, Dict, List

from shared.config import Config
from shared.database.vector import create_vector_store
from shared.llm import create_llm_provider
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.worker import Worker

logger = logging.getLogger(__name__)


class VectorQueryWorker(Worker):
    """Worker for handling vector-based queries and retrieval."""

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: Config,
    ):
        """Initialize the vector query worker."""
        super().__init__(consumer, publisher, config)
        self.vector_store = create_vector_store("qdrant")
        self.llm_provider = create_llm_provider("ollama")

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process vector query message."""
        try:
            event_type = message.get("event_type")
            if event_type == "chat.vector_query":
                self._process_vector_query(message)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing vector query message: {e}")

    def _process_vector_query(self, message: Dict[str, Any]) -> None:
        """Process a vector-based query for retrieval."""
        query = message.get("query")
        workspace_id = message.get("workspace_id")
        session_id = message.get("session_id")
        top_k = message.get("top_k", 5)

        if not query or not workspace_id:
            logger.error("Missing query or workspace_id in message")
            return

        try:
            # Perform vector similarity search
            results = self._perform_vector_retrieval(query, workspace_id, top_k)

            # Publish results back to chat service
            self.publisher.publish_event(
                event_type="chat.vector_query_completed",
                session_id=session_id,
                workspace_id=workspace_id,
                query=query,
                results=results,
                result_count=len(results),
            )

            logger.info(f"Completed vector query for session {session_id} with {len(results)} results")

        except Exception as e:
            logger.error(f"Error processing vector query for session {session_id}: {e}")

            # Publish error event
            self.publisher.publish_event(
                event_type="chat.vector_query_failed",
                session_id=session_id,
                workspace_id=workspace_id,
                query=query,
                error=str(e),
            )

    def _perform_vector_retrieval(self, query: str, workspace_id: int, top_k: int) -> List[Dict[str, Any]]:
        """Perform vector-based retrieval for the query."""
        # Generate embedding for the query
        query_embedding = self.llm_provider.embed([query])[0]

        # Search vector store
        search_results = self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k,
            filter={"workspace_id": workspace_id}
        )

        # Format results
        results = []
        for result in search_results:
            results.append({
                "type": "vector_context",
                "content": result.get("text", ""),
                "score": result.get("score", 0.0),
                "source": "vector_similarity",
                "metadata": {
                    "document_id": result.get("document_id"),
                    "chunk_id": result.get("chunk_id"),
                    "workspace_id": workspace_id,
                }
            })

        return results


def create_vector_query_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: Config,
) -> VectorQueryWorker:
    """Create a vector query worker."""
    return VectorQueryWorker(consumer, publisher, config)