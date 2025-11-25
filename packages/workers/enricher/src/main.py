"""
Enricher Worker - Document enrichment and metadata augmentation.

Consumes: document.indexed, graph.updated
Produces: document.enriched
"""

import json
from dataclasses import asdict, dataclass
from typing import Any

from shared.config import config
from shared.logger import create_logger
from shared.worker import Worker

logger = create_logger(__name__)

# Use unified config
RABBITMQ_URL = config.rabbitmq_url
RABBITMQ_EXCHANGE = config.rabbitmq_exchange
DATABASE_URL = config.database_url
WORKER_CONCURRENCY = config.worker_concurrency


@dataclass
class DocumentEnrichedEvent:
    """Event emitted when document is enriched."""

    document_id: str
    workspace_id: str
    enrichments: list[dict[str, Any]]
    entity_count: int
    enrichment_count: int
    metadata: dict[str, Any]


class EnricherWorker(Worker):
    """Document enricher worker for metadata augmentation."""

    def __init__(self) -> None:
        """Initialize the enricher worker."""
        super().__init__(
            worker_name="enricher",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="document.indexed",  # Also listen to graph.updated
            consume_queue="enricher.document.indexed",
            prefetch_count=WORKER_CONCURRENCY,
        )

    def process_event(self, event_data: dict[str, Any]) -> None:
        """
        Process document.indexed or graph.updated event to enrich document metadata.

        Args:
            event_data: Event data containing document_id, workspace_id, etc.
            message_context: Message context information
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        metadata = event_data.get("metadata", {})

        logger.info(
            "Enriching document metadata",
            extra={
                "document_id": document_id,
                "workspace_id": workspace_id,
            },
        )

        try:
            # TODO: Implement document enrichment
            # 1. Gather data from vector index and graph database
            # 2. Extract entities, relationships, and metadata
            # 3. Generate summaries, keywords, topics
            # 4. Store enrichment data

            enrichments: list[dict[str, Any]] = []  # Placeholder
            entity_count = 0  # Placeholder
            enrichment_count = 0  # Placeholder

            # Update document status
            self._update_document_status(
                document_id,
                "enriched",
                {"entity_count": entity_count, "enrichment_count": enrichment_count},
            )

            # Publish document.enriched event
            enriched_event = DocumentEnrichedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                enrichments=enrichments,
                entity_count=entity_count,
                enrichment_count=enrichment_count,
                metadata=metadata,
            )
            self.publish_event(
                routing_key="document.enriched",
                event=asdict(enriched_event),
            )

            logger.info(
                "Successfully enriched document",
                extra={
                    "document_id": document_id,
                    "entity_count": entity_count,
                    "enrichment_count": enrichment_count,
                },
            )

        except Exception as e:
            logger.error(
                "Failed to enrich document",
                extra={"document_id": document_id, "error": str(e)},
            )
            # TODO: Update document status to failed
            self._update_document_status(document_id, "failed", {"error": str(e)})
            raise

    def _update_document_status(
        self,
        document_id: str,
        status: str,
        metadata: dict[str, Any] | None = None,
        db_url: str | None = None,
    ) -> None:
        """Update document processing status."""
        from shared.database.sql import PostgresSqlDatabase

        try:
            # Create database connection
            database_url = db_url or DATABASE_URL
            db = PostgresSqlDatabase(db_url=database_url)

            # Prepare metadata for JSON storage
            processing_metadata = metadata or {}

            # Update document status and metadata
            query = """
            UPDATE documents
            SET processing_status = %(status)s, processing_metadata = %(metadata)s, updated_at = NOW()
            WHERE id = %(id)s
            """
            db.execute(
                query,
                {
                    "status": status,
                    "metadata": json.dumps(processing_metadata),
                    "id": document_id,
                },
            )

            logger.info(
                "Updated document status",
                extra={
                    "document_id": document_id,
                    "status": status,
                    "metadata": processing_metadata,
                },
            )

        except Exception as e:
            logger.error(
                "Failed to update document status",
                extra={"document_id": document_id, "status": status, "error": str(e)},
            )
            raise


def main() -> None:
    """Main entry point."""
    worker = EnricherWorker()
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Stopping enricher worker")
        worker.stop()


if __name__ == "__main__":
    main()
