"""Relationship extraction worker for Graph RAG."""

import json
import logging
from typing import Any, Dict, List

from shared.config import Config
from shared.llm import create_llm_provider
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.repositories import create_document_repository
from shared.worker import Worker

logger = logging.getLogger(__name__)


class RelationshipExtractionWorker(Worker):
    """Worker for extracting relationships between entities for Graph RAG."""

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: Config,
    ):
        """Initialize the relationship extraction worker."""
        super().__init__(consumer, publisher, config)
        self.document_repo = create_document_repository()
        self.llm_provider = create_llm_provider("ollama")

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process relationship extraction message."""
        try:
            event_type = message.get("event_type")
            if event_type == "document.entities_extracted":
                self._process_entities_extracted(message)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing relationship extraction message: {e}")

    def _process_entities_extracted(self, message: Dict[str, Any]) -> None:
        """Process extracted entities for relationship extraction."""
        document_id = message.get("document_id")
        workspace_id = message.get("workspace_id")

        if not document_id or not workspace_id:
            logger.error("Missing document_id or workspace_id in message")
            return

        try:
            # Get extracted entities
            entities = self._get_extracted_entities(document_id, workspace_id)
            if not entities:
                logger.warning(f"No entities found for document {document_id}")
                return

            # Extract relationships between entities
            relationships = self._extract_relationships(entities)

            # Store extracted relationships
            self._store_extracted_relationships(document_id, workspace_id, relationships)

            # Publish completion event
            self.publisher.publish_event(
                event_type="document.relationships_extracted",
                document_id=document_id,
                workspace_id=workspace_id,
                relationship_count=len(relationships),
            )

            logger.info(f"Extracted {len(relationships)} relationships from document {document_id}")

        except Exception as e:
            logger.error(f"Error extracting relationships from document {document_id}: {e}")

    def _get_extracted_entities(self, document_id: str, workspace_id: int) -> List[Dict[str, Any]]:
        """Get extracted entities for a document."""
        # TODO: Implement entity retrieval from database
        return []

    def _extract_relationships(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships between entities."""
        if len(entities) < 2:
            return []

        relationships = []

        # Simple co-occurrence based relationship extraction
        # TODO: Implement more sophisticated relationship extraction using LLM
        entity_names = [e["entity"] for e in entities]

        # Create relationships based on entity proximity/co-occurrence
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                # Check if entities appear in same context
                if self._entities_cooccur(entity1, entity2):
                    relationship = {
                        "source": entity1["entity"],
                        "target": entity2["entity"],
                        "type": "cooccurs_with",  # Default relationship type
                        "confidence": 0.7,
                        "source_type": entity1.get("type", "UNKNOWN"),
                        "target_type": entity2.get("type", "UNKNOWN"),
                    }
                    relationships.append(relationship)

        return relationships

    def _entities_cooccur(self, entity1: Dict[str, Any], entity2: Dict[str, Any]) -> bool:
        """Check if two entities co-occur in the same context."""
        # TODO: Implement proper co-occurrence detection
        # For now, assume they co-occur if they're in the same document
        return True

    def _store_extracted_relationships(
        self,
        document_id: str,
        workspace_id: int,
        relationships: List[Dict[str, Any]]
    ) -> None:
        """Store extracted relationships."""
        # TODO: Implement relationship storage
        pass


def create_relationship_extraction_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: Config,
) -> RelationshipExtractionWorker:
    """Create a relationship extraction worker."""
    return RelationshipExtractionWorker(consumer, publisher, config)