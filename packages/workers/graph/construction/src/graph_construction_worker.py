"""Graph construction worker for Graph RAG."""

import logging
from typing import Any, Dict, List

from shared.config import AppConfig
from shared.database.graph import create_graph_store
from shared.messaging.consumer import MessageConsumer
from shared.messaging.publisher import MessagePublisher
from shared.repositories.graph_rag import (
    create_entity_repository,
    create_relationship_repository,
)
from shared.worker import Worker

logger = logging.getLogger(__name__)


class GraphConstructionWorker(Worker):
    """Worker for constructing Neo4j graphs from extracted entities and relationships."""

    def __init__(
        self,
        consumer: MessageConsumer,
        publisher: MessagePublisher,
        config: AppConfig,
    ):
        """Initialize the graph construction worker."""
        super().__init__(consumer, publisher, config)
        self.entity_repo = create_entity_repository("postgres", db_url=config.database_url)
        self.relationship_repo = create_relationship_repository("postgres", db_url=config.database_url)
        self.graph_store = create_graph_store("neo4j")

    def process_message(self, message: Dict[str, Any]) -> None:
        """Process graph construction message."""
        try:
            event_type = message.get("event_type")
            if event_type == "document.communities_detected":
                self._process_communities_detected(message)
            else:
                logger.warning(f"Unknown event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing graph construction message: {e}")

    def _process_communities_detected(self, message: Dict[str, Any]) -> None:
        """Process communities detected event to construct graph."""
        document_id = message.get("document_id")
        workspace_id = message.get("workspace_id")

        if not document_id or not workspace_id:
            logger.error("Missing document_id or workspace_id in message")
            return

        try:
            # Get all entities and relationships for this workspace
            # Note: In a production system, we might want to scope this to the document
            # But for now, we'll build the graph from all workspace data
            entities = self.entity_repo.get_by_workspace(workspace_id)
            relationships = self.relationship_repo.get_by_workspace(workspace_id)

            if not entities:
                logger.warning(f"No entities found for workspace {workspace_id}")
                return

            # Build graph structure
            graph_data = self._build_graph_structure(entities, relationships)

            # Store graph in Neo4j
            self.graph_store.add_graph(graph_data)

            # Publish completion event
            self.publisher.publish_event(
                event_type="document.graph_constructed",
                document_id=document_id,
                workspace_id=workspace_id,
                node_count=len(graph_data.get("nodes", [])),
                edge_count=len(graph_data.get("edges", [])),
            )

            logger.info(f"Constructed graph for workspace {workspace_id} with {len(graph_data.get('nodes', []))} nodes and {len(graph_data.get('edges', []))} edges")

        except Exception as e:
            logger.error(f"Error constructing graph for workspace {workspace_id}: {e}")

    def _build_graph_structure(self, entities: List[Any], relationships: List[Any]) -> Dict[str, Any]:
        """Build graph structure from entities and relationships."""
        # Convert entities to graph nodes
        nodes = []
        for entity in entities:
            node = {
                "id": f"entity_{entity.id}",
                "labels": ["Entity", entity.entity_type.upper()],
                "properties": {
                    "entity_id": entity.id,
                    "workspace_id": entity.workspace_id,
                    "document_id": entity.document_id,
                    "chunk_id": entity.chunk_id,
                    "entity_type": entity.entity_type,
                    "entity_text": entity.entity_text,
                    "confidence_score": entity.confidence_score,
                    "metadata": entity.metadata,
                }
            }
            nodes.append(node)

        # Convert relationships to graph edges
        edges = []
        for rel in relationships:
            edge = {
                "id": f"relationship_{rel.id}",
                "source": f"entity_{rel.source_entity_id}",
                "target": f"entity_{rel.target_entity_id}",
                "label": rel.relationship_type.upper(),
                "properties": {
                    "relationship_id": rel.id,
                    "workspace_id": rel.workspace_id,
                    "confidence_score": rel.confidence_score,
                    "metadata": rel.metadata,
                }
            }
            edges.append(edge)

        return {"nodes": nodes, "edges": edges}


def create_graph_construction_worker(
    consumer: MessageConsumer,
    publisher: MessagePublisher,
    config: AppConfig,
) -> GraphConstructionWorker:
    """Create a graph construction worker."""
    return GraphConstructionWorker(consumer, publisher, config)