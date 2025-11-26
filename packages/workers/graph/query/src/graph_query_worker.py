"""Graph query worker for Graph RAG retrieval."""

import logging
from typing import Any, Dict, List

from shared.config import AppConfig
from shared.database.graph import create_graph_store
from shared.llm import create_llm_provider
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.worker import Worker

logger = logging.getLogger(__name__)


class GraphQueryWorker(Worker):
    """Worker for handling graph-based queries and retrieval for Graph RAG."""

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: AppConfig,
    ):
        """Initialize the graph query worker."""
        super().__init__(consumer, publisher, config)
        self.graph_store = create_graph_store("neo4j")
        self.llm_provider = create_llm_provider("ollama")

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process graph query message."""
        try:
            event_type = message.get("event_type")
            if event_type == "chat.graph_query":
                self._process_graph_query(message)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing graph query message: {e}")

    def _process_graph_query(self, message: Dict[str, Any]) -> None:
        """Process a graph-based query for retrieval."""
        query = message.get("query")
        workspace_id = message.get("workspace_id")
        session_id = message.get("session_id")
        top_k = message.get("top_k", 5)

        if not query or not workspace_id:
            logger.error("Missing query or workspace_id in message")
            return

        try:
            # Perform graph-based retrieval
            results = self._perform_graph_retrieval(query, workspace_id, top_k)

            # Publish results back to chat service
            self.publisher.publish_event(
                event_type="chat.graph_query_completed",
                session_id=session_id,
                workspace_id=workspace_id,
                query=query,
                results=results,
                result_count=len(results),
            )

            logger.info(f"Completed graph query for session {session_id} with {len(results)} results")

        except Exception as e:
            logger.error(f"Error processing graph query for session {session_id}: {e}")

            # Publish error event
            self.publisher.publish_event(
                event_type="chat.graph_query_failed",
                session_id=session_id,
                workspace_id=workspace_id,
                query=query,
                error=str(e),
            )

    def _perform_graph_retrieval(self, query: str, workspace_id: int, top_k: int) -> List[Dict[str, Any]]:
        """Perform graph-based retrieval for the query."""
        # This is a simplified implementation
        # In a full implementation, this would:
        # 1. Extract entities from the query using LLM/NER
        # 2. Find matching entities in the graph
        # 3. Perform graph traversal (e.g., shortest paths, neighborhood expansion)
        # 4. Rank and return relevant information

        # For now, return a placeholder result
        return [
            {
                "type": "graph_context",
                "content": f"Graph-based context for query: {query}",
                "score": 0.8,
                "source": "graph_traversal",
                "metadata": {
                    "workspace_id": workspace_id,
                    "query": query,
                }
            }
        ]


def create_graph_query_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: AppConfig,
) -> GraphQueryWorker:
    """Create a graph query worker."""
    return GraphQueryWorker(consumer, publisher, config)