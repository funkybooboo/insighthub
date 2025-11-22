"""
Enrichment Worker - Wikipedia knowledge augmentation via MCP.

Enriches documents with Wikipedia knowledge using Model Context Protocol (MCP).

Consumes: document.uploaded
Produces: document.enriched, document.enrichment.failed
"""

import os
from dataclasses import dataclass

from shared.logger import create_logger
from shared.messaging.events import DocumentUploadedEvent
from shared.types.common import MetadataDict, PayloadDict
from shared.worker import Worker

logger = create_logger(__name__)

# Configuration
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://insighthub:insighthub_dev@rabbitmq:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "insighthub")
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "2"))

# Wikipedia MCP Configuration
MCP_WIKIPEDIA_ENDPOINT = os.getenv("MCP_WIKIPEDIA_ENDPOINT", "http://localhost:8080")


@dataclass
class DocumentEnrichedEvent:
    """Event published when document enrichment completes."""

    document_id: str
    workspace_id: str
    enrichments: list[dict[str, str]]
    entity_count: int
    enrichment_count: int
    metadata: MetadataDict


@dataclass
class DocumentEnrichmentFailedEvent:
    """Event published when document enrichment fails."""

    document_id: str
    workspace_id: str
    error: str
    metadata: MetadataDict


class EnricherWorker(Worker):
    """Enrichment worker for Wikipedia knowledge augmentation."""

    def __init__(self) -> None:
        """Initialize the enricher worker."""
        super().__init__(
            worker_name="enricher",
            rabbitmq_url=RABBITMQ_URL,
            exchange=RABBITMQ_EXCHANGE,
            exchange_type="topic",
            consume_routing_key="document.uploaded",
            consume_queue="enricher.document.uploaded",
            prefetch_count=WORKER_CONCURRENCY,
        )
        self._mcp_endpoint = MCP_WIKIPEDIA_ENDPOINT

    def process_event(self, event_data: PayloadDict) -> None:
        """
        Process document.uploaded event.

        Args:
            event_data: Parsed event data as dictionary
        """
        document_id = str(event_data.get("document_id", ""))
        workspace_id = str(event_data.get("workspace_id", ""))
        metadata = dict(event_data.get("metadata", {}))

        try:
            event = DocumentUploadedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                filename=str(event_data.get("filename", "")),
                storage_path=str(event_data.get("storage_path", "")),
                metadata=metadata,
            )

            logger.info(
                "Enriching document",
                document_id=event.document_id,
                filename=event.filename,
            )

            # TODO: Fetch document text from storage
            # text = blob_storage.get(event.storage_path)
            text = ""  # Placeholder

            # Extract entities and enrich
            entities = self._extract_entities(text)
            enrichments: list[dict[str, str]] = []

            for entity in entities:
                wiki_data = self._query_wikipedia_mcp(entity)
                if wiki_data:
                    enrichments.append({"entity": entity, "data": str(wiki_data)})

            # Publish success event
            enriched_event = DocumentEnrichedEvent(
                document_id=event.document_id,
                workspace_id=event.workspace_id,
                enrichments=enrichments,
                entity_count=len(entities),
                enrichment_count=len(enrichments),
                metadata=metadata,
            )
            self.publish_event("document.enriched", {
                "document_id": enriched_event.document_id,
                "workspace_id": enriched_event.workspace_id,
                "enrichments": enriched_event.enrichments,
                "entity_count": enriched_event.entity_count,
                "enrichment_count": enriched_event.enrichment_count,
                "metadata": enriched_event.metadata,
            })

            logger.info(
                "Document enrichment completed",
                document_id=event.document_id,
                entity_count=len(entities),
                enrichment_count=len(enrichments),
            )

        except Exception as e:
            logger.error(
                "Document enrichment failed",
                document_id=document_id,
                error=str(e),
            )
            # Publish failure event
            failure = DocumentEnrichmentFailedEvent(
                document_id=document_id,
                workspace_id=workspace_id,
                error=str(e),
                metadata=metadata,
            )
            self.publish_event("document.enrichment.failed", {
                "document_id": failure.document_id,
                "workspace_id": failure.workspace_id,
                "error": failure.error,
                "metadata": failure.metadata,
            })
            raise

    def _extract_entities(self, text: str) -> list[str]:
        """
        Extract key entities/concepts from document text.

        TODO: Implement entity extraction:
        1. Use NLP techniques (spaCy, NLTK, or LLM-based extraction)
        2. Filter entities by relevance and type
        3. Return list of entity strings

        Args:
            text: Document text content

        Returns:
            List of extracted entity strings
        """
        logger.info("Extracting entities from document text")
        # TODO: Implement entity extraction
        # import spacy
        # nlp = spacy.load("en_core_web_sm")
        # doc = nlp(text)
        # entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PERSON", "GPE"]]
        # return entities
        return []

    def _query_wikipedia_mcp(self, entity: str) -> dict[str, str] | None:
        """
        Query Wikipedia MCP server for entity information.

        TODO: Implement MCP protocol communication:
        1. Send search query for entity
        2. Parse Wikipedia results (summary, categories, links)
        3. Handle errors and rate limiting
        4. Return structured Wikipedia data

        Args:
            entity: Entity name to search for

        Returns:
            Wikipedia data dictionary or None if not found
        """
        logger.info("Querying Wikipedia MCP", entity=entity)
        # TODO: Implement MCP Wikipedia query
        # import httpx
        # response = httpx.post(
        #     f"{self._mcp_endpoint}/search",
        #     json={"query": entity}
        # )
        # if response.status_code == 200:
        #     return response.json()
        # return None
        return None


def main() -> None:
    """Main entry point for enricher worker."""
    worker = EnricherWorker()
    worker.start()


if __name__ == "__main__":
    main()
