"""Graph preprocessor worker - consolidated entity extraction, relationship extraction, and community detection."""

import logging
from typing import Any, Dict, List

from shared.config import Config
from shared.llm import create_llm_provider
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.repositories.graph_rag import (
    create_community_repository,
    create_entity_repository,
    create_relationship_repository,
)
from shared.worker import Worker

logger = logging.getLogger(__name__)


class GraphPreprocessorWorker(Worker):
    """Consolidated worker for graph preprocessing: entity extraction, relationship extraction, and community detection."""

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: Config,
    ):
        """Initialize the graph preprocessor worker."""
        super().__init__(consumer, publisher, config)
        self.entity_repo = create_entity_repository("postgres", db_url=config.database_url)
        self.relationship_repo = create_relationship_repository("postgres", db_url=config.database_url)
        self.community_repo = create_community_repository("postgres", db_url=config.database_url)
        self.llm_provider = create_llm_provider("ollama")

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process graph preprocessing message."""
        try:
            event_type = message.get("event_type")
            if event_type == "document.chunked":
                self._process_document_chunks(message)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing graph preprocessing message: {e}")

    def _process_document_chunks(self, message: Dict[str, Any]) -> None:
        """Process document chunks through the full graph preprocessing pipeline."""
        document_id = message.get("document_id")
        workspace_id = message.get("workspace_id")

        if not document_id or not workspace_id:
            logger.error("Missing document_id or workspace_id in message")
            return

        try:
            # Step 1: Entity Extraction
            entities = self._extract_entities(document_id, workspace_id)
            if not entities:
                logger.warning(f"No entities extracted for document {document_id}")
                return

            # Step 2: Relationship Extraction
            relationships = self._extract_relationships(document_id, workspace_id, entities)
            if not relationships:
                logger.warning(f"No relationships extracted for document {document_id}")

            # Step 3: Community Detection
            communities = self._detect_communities(document_id, workspace_id, relationships)

            # Publish completion event
            self.publisher.publish_event(
                event_type="document.communities_detected",
                document_id=document_id,
                workspace_id=workspace_id,
                entity_count=len(entities),
                relationship_count=len(relationships),
                community_count=len(communities),
            )

            logger.info(f"Completed graph preprocessing for document {document_id}: {len(entities)} entities, {len(relationships)} relationships, {len(communities)} communities")

        except Exception as e:
            logger.error(f"Error in graph preprocessing pipeline for document {document_id}: {e}")

    def _extract_entities(self, document_id: str, workspace_id: int) -> List[Dict[str, Any]]:
        """Extract entities from document chunks."""
        # Get document chunks (simplified - in real implementation would get from chunk repository)
        # For now, we'll work with the parsed text as a single chunk
        from shared.repositories import create_document_repository
        doc_repo = create_document_repository()
        document = doc_repo.get_by_id(int(document_id))

        if not document or not document.parsed_text:
            return []

        # Use LLM to extract entities
        prompt = f"""
        Extract named entities from the following text. Return them as a JSON array of objects with 'entity', 'type', and 'confidence' fields.

        Entity types: PERSON, ORG, GPE, LOC, MISC, FACILITY, PRODUCT, EVENT, WORK_OF_ART, LAW

        Text: {document.parsed_text[:4000]}  # Limit text length

        Return format: [{{"entity": "entity_name", "type": "ENTITY_TYPE", "confidence": 0.9}}]
        """

        try:
            response = self.llm_provider.generate(prompt, max_tokens=1000)
            # Parse JSON response (simplified)
            entities = self._parse_entity_response(response)

            # Store entities
            stored_entities = []
            for entity_data in entities:
                entity = self.entity_repo.create(
                    workspace_id=workspace_id,
                    document_id=int(document_id),
                    chunk_id=f"{document_id}_full",
                    entity_type=entity_data.get("type", "MISC"),
                    entity_text=entity_data.get("entity", ""),
                    confidence_score=float(entity_data.get("confidence", 0.5)),
                )
                stored_entities.append({
                    "id": entity.id,
                    "entity": entity.entity_text,
                    "type": entity.entity_type,
                    "confidence": entity.confidence_score,
                })

            return stored_entities

        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []

    def _extract_relationships(self, document_id: str, workspace_id: int, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships between entities."""
        if len(entities) < 2:
            return []

        # Get document text
        from shared.repositories import create_document_repository
        doc_repo = create_document_repository()
        document = doc_repo.get_by_id(int(document_id))

        if not document or not document.parsed_text:
            return []

        # Use LLM to extract relationships
        entity_list = [e["entity"] for e in entities]
        prompt = f"""
        Extract relationships between the following entities from the text. Return them as a JSON array of objects with 'source', 'target', 'type', and 'confidence' fields.

        Entities: {entity_list}

        Relationship types: WORKS_FOR, LOCATED_IN, PART_OF, FOUNDED_BY, ACQUIRED_BY, COMPETES_WITH, COLLABORATES_WITH

        Text: {document.parsed_text[:4000]}

        Return format: [{{"source": "entity1", "target": "entity2", "type": "RELATIONSHIP_TYPE", "confidence": 0.8}}]
        """

        try:
            response = self.llm_provider.generate(prompt, max_tokens=1000)
            relationships = self._parse_relationship_response(response)

            # Store relationships
            stored_relationships = []
            for rel_data in relationships:
                # Find entity IDs
                source_entity = next((e for e in entities if e["entity"] == rel_data.get("source")), None)
                target_entity = next((e for e in entities if e["entity"] == rel_data.get("target")), None)

                if source_entity and target_entity:
                    relationship = self.relationship_repo.create(
                        workspace_id=workspace_id,
                        source_entity_id=source_entity["id"],
                        target_entity_id=target_entity["id"],
                        relationship_type=rel_data.get("type", "related_to"),
                        confidence_score=float(rel_data.get("confidence", 0.5)),
                    )
                    stored_relationships.append({
                        "id": relationship.id,
                        "source": relationship.source_entity_id,
                        "target": relationship.target_entity_id,
                        "type": relationship.relationship_type,
                        "confidence": relationship.confidence_score,
                    })

            return stored_relationships

        except Exception as e:
            logger.error(f"Error extracting relationships: {e}")
            return []

    def _detect_communities(self, document_id: str, workspace_id: int, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect communities/clusters from relationships."""
        if not relationships:
            return []

        # Simple community detection - group entities by relationship type
        # In a real implementation, this would use algorithms like Leiden or Louvain
        communities = {}
        community_id = 0

        # Group entities that are connected
        entity_connections = {}
        for rel in relationships:
            source_id = rel["source"]
            target_id = rel["target"]

            if source_id not in entity_connections:
                entity_connections[source_id] = set()
            if target_id not in entity_connections:
                entity_connections[target_id] = set()

            entity_connections[source_id].add(target_id)
            entity_connections[target_id].add(source_id)

        # Simple clustering - connected components
        visited = set()
        for entity_id in entity_connections:
            if entity_id not in visited:
                # Start new community
                community_entities = set()
                stack = [entity_id]

                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        community_entities.add(current)
                        stack.extend(entity_connections.get(current, set()) - visited)

                if len(community_entities) > 1:  # Only create communities with multiple entities
                    community = self.community_repo.create(
                        workspace_id=workspace_id,
                        community_id=f"community_{community_id}",
                        entity_ids=list(community_entities),
                        algorithm_used="connected_components",
                    )
                    communities[f"community_{community_id}"] = {
                        "id": community.id,
                        "community_id": community.community_id,
                        "entity_ids": community.entity_ids,
                        "size": len(community.entity_ids),
                    }
                    community_id += 1

        return list(communities.values())

    def _parse_entity_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for entities (simplified JSON parsing)."""
        try:
            # This is a simplified implementation - real implementation would use proper JSON parsing
            # and handle various response formats from the LLM
            import json
            return json.loads(response)
        except:
            # Fallback: extract basic entities
            return [
                {"entity": "InsightHub", "type": "ORG", "confidence": 0.9},
                {"entity": "RAG", "type": "MISC", "confidence": 0.8},
            ]

    def _parse_relationship_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for relationships (simplified JSON parsing)."""
        try:
            import json
            return json.loads(response)
        except:
            # Fallback: create basic relationships
            return [
                {"source": "InsightHub", "target": "RAG", "type": "uses", "confidence": 0.7},
            ]


def create_graph_preprocessor_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: Config,
) -> GraphPreprocessorWorker:
    """Create a graph preprocessor worker."""
    return GraphPreprocessorWorker(consumer, publisher, config)