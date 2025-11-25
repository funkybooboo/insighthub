"""Entity extraction worker for Graph RAG."""

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


class EntityExtractionWorker(Worker):
    """Worker for extracting entities from document chunks for Graph RAG."""

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: Config,
    ):
        """Initialize the entity extraction worker."""
        super().__init__(consumer, publisher, config)
        self.document_repo = create_document_repository()
        self.llm_provider = create_llm_provider("ollama")

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process entity extraction message."""
        try:
            event_type = message.get("event_type")
            if event_type == "document.chunked":
                self._process_chunked_document(message)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing entity extraction message: {e}")
            # TODO: Send failure event

    def _process_chunked_document(self, message: Dict[str, Any]) -> None:
        """Process a chunked document for entity extraction."""
        document_id = message.get("document_id")
        workspace_id = message.get("workspace_id")

        if not document_id or not workspace_id:
            logger.error("Missing document_id or workspace_id in message")
            return

        try:
            # Get document chunks
            chunks = self._get_document_chunks(document_id, workspace_id)
            if not chunks:
                logger.warning(f"No chunks found for document {document_id}")
                return

            # Extract entities from chunks
            entities = []
            for chunk in chunks:
                chunk_entities = self._extract_entities_from_chunk(chunk)
                entities.extend(chunk_entities)

            # Store extracted entities
            self._store_extracted_entities(document_id, workspace_id, entities)

            # Publish completion event
            self.publisher.publish_event(
                event_type="document.entities_extracted",
                document_id=document_id,
                workspace_id=workspace_id,
                entity_count=len(entities),
            )

            logger.info(f"Extracted {len(entities)} entities from document {document_id}")

        except Exception as e:
            logger.error(f"Error extracting entities from document {document_id}: {e}")

    def _get_document_chunks(self, document_id: str, workspace_id: int) -> List[Dict[str, Any]]:
        """Get chunks for a document."""
        # TODO: Implement chunk retrieval
        # This would query the database for chunks of the document
        return []

    def _extract_entities_from_chunk(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract entities from a single chunk."""
        text = chunk.get("text", "")
        if not text:
            return []

        # Use LLM to extract entities
        prompt = f"""
        Extract named entities from the following text. Return a JSON array of entities with type and confidence.

        Text: {text}

        Return format:
        [
            {{"entity": "entity_name", "type": "PERSON|ORG|GPE|etc", "confidence": 0.95}},
            ...
        ]
        """

        try:
            response = self.llm_provider.generate(
                system_prompt="You are an expert at named entity recognition. Extract entities accurately.",
                user_prompt=prompt,
                max_tokens=1000,
            )

            # Parse JSON response
            entities = json.loads(response.strip())
            return entities if isinstance(entities, list) else []

        except Exception as e:
            logger.error(f"Error extracting entities from chunk: {e}")
            return []

    def _store_extracted_entities(
        self,
        document_id: str,
        workspace_id: int,
        entities: List[Dict[str, Any]]
    ) -> None:
        """Store extracted entities."""
        # TODO: Implement entity storage
        # This would store entities in the database for later use by relationship extraction
        pass


def create_entity_extraction_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: Config,
) -> EntityExtractionWorker:
    """Create an entity extraction worker."""
    return EntityExtractionWorker(consumer, publisher, config)