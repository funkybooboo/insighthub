"""Document router worker for RAG pipeline orchestration."""

import logging
from typing import Any, Dict, List

from shared.config import AppConfig
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.worker import Worker

logger = logging.getLogger(__name__)


class DocumentRouterWorker(Worker):
    """Worker that routes documents to appropriate RAG pipelines."""

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: AppConfig,
    ):
        """Initialize the document router worker."""
        super().__init__(consumer, publisher, config)

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process document routing message."""
        try:
            event_type = message.get("event_type")
            if event_type == "document.chunked":
                self._route_document(message)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing document routing message: {e}")

    def _route_document(self, message: Dict[str, Any]) -> None:
        """Route document to appropriate RAG pipelines."""
        document_id = message.get("document_id")
        workspace_id = message.get("workspace_id")

        if not document_id or not workspace_id:
            logger.error("Missing document_id or workspace_id in message")
            return

        try:
            # For now, route to both pipelines (can be made configurable later)
            # In production, this could check workspace settings to determine which RAG systems to use

            # Always route to vector pipeline (embedder)
            self.publisher.publish_event(
                event_type="document.chunked",
                document_id=document_id,
                workspace_id=workspace_id,
                routing_key="vector.embedder",
            )

            # Always route to graph pipeline (entity extraction)
            self.publisher.publish_event(
                event_type="document.chunked",
                document_id=document_id,
                workspace_id=workspace_id,
                routing_key="graph.entity_extraction",
            )

            logger.info(f"Routed document {document_id} to vector and graph pipelines")

        except Exception as e:
            logger.error(f"Error routing document {document_id}: {e}")


def create_document_router_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: AppConfig,
) -> DocumentRouterWorker:
    """Create a document router worker."""
    return DocumentRouterWorker(consumer, publisher, config)