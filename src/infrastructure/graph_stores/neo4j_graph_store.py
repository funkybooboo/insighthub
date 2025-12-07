"""Neo4j implementation of the graph store.

This module provides a Neo4j-backed implementation of the GraphStore interface
for storing and querying knowledge graphs in Graph RAG.
"""

import json
from typing import Optional

from neo4j import Driver, GraphDatabase

from src.infrastructure.graph_stores.graph_store import GraphStore
from src.infrastructure.logger import create_logger
from src.infrastructure.types.graph import (
    Community,
    CommunityMetadata,
    Entity,
    EntityMetadata,
    EntityType,
    GraphSubgraph,
    Relationship,
    RelationshipMetadata,
    RelationType,
)

logger = create_logger(__name__)


class Neo4jGraphStore(GraphStore):
    """Neo4j implementation of the graph store.

    This implementation uses Neo4j as the backend for storing entities,
    relationships, and communities. It supports workspace-based isolation.
    """

    def __init__(self, uri: str, username: str, password: str):
        """Initialize Neo4j graph store.

        Args:
            uri: Neo4j connection URI (e.g., "bolt://localhost:7687")
            username: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.driver: Driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info(f"Connected to Neo4j at {uri}")

    def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def _execute_write(self, query: str, parameters: dict) -> None:
        """Execute a write query."""
        with self.driver.session() as session:
            session.run(query, parameters)

    def _execute_read(self, query: str, parameters: dict) -> list:
        """Execute a read query and return results."""
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return list(result)

    def create_constraint(self, label: str, property: str) -> None:
        """Create a uniqueness constraint on a node label property."""
        query = f"""
        CREATE CONSTRAINT {label.lower()}_{property}_unique IF NOT EXISTS
        FOR (n:{label})
        REQUIRE n.{property} IS UNIQUE
        """
        try:
            self._execute_write(query, {})
            logger.info(f"Created constraint on {label}.{property}")
        except Exception as e:
            logger.warning(f"Constraint creation skipped or failed: {e}")

    def create_index(self, label: str, properties: list[str]) -> None:
        """Create an index on node label properties."""
        props_str = ", ".join([f"n.{prop}" for prop in properties])
        index_name = f"{label.lower()}_{'_'.join(properties)}_index"
        query = f"""
        CREATE INDEX {index_name} IF NOT EXISTS
        FOR (n:{label})
        ON ({props_str})
        """
        try:
            self._execute_write(query, {})
            logger.info(f"Created index on {label}({', '.join(properties)})")
        except Exception as e:
            logger.warning(f"Index creation skipped or failed: {e}")

    def upsert_entities(self, entities: list[Entity], workspace_id: str) -> None:
        """Upsert entities into Neo4j."""
        if not entities:
            return

        for entity in entities:
            query = """
            MERGE (e:Entity {id: $id, workspace_id: $workspace_id})
            SET e.text = $text,
                e.type = $type,
                e.confidence = $confidence,
                e.metadata = $metadata,
                e.document_ids = CASE
                    WHEN e.document_ids IS NULL THEN [$document_id]
                    WHEN NOT $document_id IN e.document_ids THEN e.document_ids + $document_id
                    ELSE e.document_ids
                END
            """
            parameters = {
                "id": entity.id,
                "workspace_id": workspace_id,
                "text": entity.text,
                "type": entity.type.value,
                "confidence": entity.confidence,
                "metadata": json.dumps(dict(entity.metadata)),  # Serialize to JSON string
                "document_id": entity.metadata.get("document_id", ""),
            }
            self._execute_write(query, parameters)

        logger.info(f"Upserted {len(entities)} entities for workspace {workspace_id}")

    def upsert_relationships(self, relationships: list[Relationship], workspace_id: str) -> None:
        """Upsert relationships into Neo4j.

        Note: This requires APOC plugin for dynamic relationship types.
        If APOC is not available, relationships will be created with a generic type
        and the actual type stored as a property.
        """
        if not relationships:
            return

        for rel in relationships:
            # Try using APOC for dynamic relationship types
            query = """
            MATCH (source:Entity {id: $source_id, workspace_id: $workspace_id})
            MATCH (target:Entity {id: $target_id, workspace_id: $workspace_id})
            CALL apoc.merge.relationship(
                source,
                $relation_type,
                {id: $id},
                {
                    confidence: $confidence,
                    context: $context,
                    metadata: $metadata
                },
                target,
                {}
            ) YIELD rel
            RETURN rel
            """

            # Fallback query if APOC is not available
            fallback_query = """
            MATCH (source:Entity {id: $source_id, workspace_id: $workspace_id})
            MATCH (target:Entity {id: $target_id, workspace_id: $workspace_id})
            MERGE (source)-[r:RELATED {id: $id}]->(target)
            SET r.type = $relation_type,
                r.confidence = $confidence,
                r.context = $context,
                r.metadata = $metadata
            """

            parameters = {
                "id": rel.id,
                "source_id": rel.source_entity_id,
                "target_id": rel.target_entity_id,
                "relation_type": rel.relation_type.value,
                "confidence": rel.confidence,
                "context": rel.context,
                "metadata": json.dumps(dict(rel.metadata)),  # Serialize to JSON string
                "workspace_id": workspace_id,
            }

            try:
                self._execute_write(query, parameters)
            except Exception as e:
                logger.warning(f"APOC not available, using fallback relationship creation: {e}")
                self._execute_write(fallback_query, parameters)

        logger.info(f"Upserted {len(relationships)} relationships for workspace {workspace_id}")

    def upsert_communities(self, communities: list[Community], workspace_id: str) -> None:
        """Upsert communities into Neo4j."""
        if not communities:
            return

        for community in communities:
            # Create or update community node
            query = """
            MERGE (c:Community {id: $id, workspace_id: $workspace_id})
            SET c.level = $level,
                c.summary = $summary,
                c.score = $score,
                c.metadata = $metadata
            """
            parameters = {
                "id": community.id,
                "workspace_id": workspace_id,
                "level": community.level,
                "summary": community.summary,
                "score": community.score,
                "metadata": json.dumps(dict(community.metadata)),  # Serialize to JSON string
            }
            self._execute_write(query, parameters)

            # Link community to its member entities
            if community.entity_ids:
                link_query = """
                MATCH (c:Community {id: $community_id, workspace_id: $workspace_id})
                MATCH (e:Entity {workspace_id: $workspace_id})
                WHERE e.id IN $entity_ids
                MERGE (e)-[:BELONGS_TO]->(c)
                """
                link_parameters = {
                    "community_id": community.id,
                    "workspace_id": workspace_id,
                    "entity_ids": community.entity_ids,
                }
                self._execute_write(link_query, link_parameters)

        logger.info(f"Upserted {len(communities)} communities for workspace {workspace_id}")

    def get_entity_by_id(self, entity_id: str, workspace_id: str) -> Optional[Entity]:
        """Retrieve a single entity by its ID."""
        query = """
        MATCH (e:Entity {id: $id, workspace_id: $workspace_id})
        RETURN e
        """
        parameters = {"id": entity_id, "workspace_id": workspace_id}
        results = self._execute_read(query, parameters)

        if not results:
            return None

        record = results[0]
        node = record["e"]
        return self._node_to_entity(node)

    def find_entities(self, query: str, workspace_id: str, limit: int) -> list[Entity]:
        """Find entities matching the query string using text search."""
        cypher_query = """
        MATCH (e:Entity {workspace_id: $workspace_id})
        WHERE toLower(e.text) CONTAINS toLower($query)
        RETURN e
        ORDER BY e.confidence DESC
        LIMIT $limit
        """
        parameters = {"query": query, "workspace_id": workspace_id, "limit": limit}
        results = self._execute_read(cypher_query, parameters)

        entities = []
        for record in results:
            entities.append(self._node_to_entity(record["e"]))

        logger.info(f"Found {len(entities)} entities matching '{query}'")
        return entities

    def traverse_graph(
        self, entity_ids: list[str], workspace_id: str, max_depth: int
    ) -> GraphSubgraph:
        """Traverse the graph from starting entities up to max_depth."""
        if not entity_ids:
            return GraphSubgraph(entities=[], relationships=[], central_entities=[])

        query = (
            """
        MATCH path = (start:Entity)-[*0..%d]-(connected:Entity)
        WHERE start.id IN $entity_ids
          AND start.workspace_id = $workspace_id
          AND connected.workspace_id = $workspace_id
        WITH collect(DISTINCT start) + collect(DISTINCT connected) AS nodes,
             CASE WHEN size([r IN relationships(path) | r]) > 0
                  THEN [r IN relationships(path) | r]
                  ELSE []
             END AS all_rels
        UNWIND nodes AS n
        WITH collect(DISTINCT n) AS unique_nodes, all_rels
        UNWIND CASE WHEN size(all_rels) = 0 THEN [null] ELSE all_rels END AS r
        WITH unique_nodes, [rel IN collect(DISTINCT r) WHERE rel IS NOT NULL] AS unique_rels
        RETURN unique_nodes, unique_rels
        """
            % max_depth
        )

        parameters = {"entity_ids": entity_ids, "workspace_id": workspace_id}
        results = self._execute_read(query, parameters)

        if not results:
            return GraphSubgraph(entities=[], relationships=[], central_entities=entity_ids)

        record = results[0]
        entities = [self._node_to_entity(node) for node in record["unique_nodes"]]
        relationships = [self._rel_to_relationship(rel) for rel in record["unique_rels"]]

        logger.info(
            f"Traversed graph: {len(entities)} entities, {len(relationships)} relationships"
        )
        return GraphSubgraph(
            entities=entities,
            relationships=relationships,
            central_entities=entity_ids,
        )

    def get_communities(self, entity_ids: list[str], workspace_id: str) -> list[Community]:
        """Get communities associated with the given entities."""
        query = """
        MATCH (c:Community {workspace_id: $workspace_id})
        WHERE ANY(entity_id IN $entity_ids WHERE entity_id IN c.entity_ids)
        RETURN c
        ORDER BY c.score DESC
        """
        parameters = {"entity_ids": entity_ids, "workspace_id": workspace_id}
        results = self._execute_read(query, parameters)

        communities = []
        for record in results:
            communities.append(self._node_to_community(record["c"]))

        logger.info(f"Found {len(communities)} communities for {len(entity_ids)} entities")
        return communities

    def delete_document_graph(self, document_id: str, workspace_id: str) -> None:
        """Delete all entities and relationships associated with a document."""
        # Remove document_id from entity document_ids arrays
        query_update = """
        MATCH (e:Entity {workspace_id: $workspace_id})
        WHERE $document_id IN e.document_ids
        SET e.document_ids = [id IN e.document_ids WHERE id <> $document_id]
        """
        self._execute_write(
            query_update, {"document_id": document_id, "workspace_id": workspace_id}
        )

        # Delete entities with empty document_ids
        query_delete = """
        MATCH (e:Entity {workspace_id: $workspace_id})
        WHERE size(e.document_ids) = 0
        DETACH DELETE e
        """
        self._execute_write(query_delete, {"workspace_id": workspace_id})

        logger.info(f"Deleted graph data for document {document_id} in workspace {workspace_id}")

    def delete_workspace_graph(self, workspace_id: str) -> None:
        """Delete all entities, relationships, and communities for a workspace."""
        # Delete all entities and their relationships
        # DETACH DELETE removes both nodes and their relationships
        query_entities = """
        MATCH (e:Entity {workspace_id: $workspace_id})
        DETACH DELETE e
        """
        self._execute_write(query_entities, {"workspace_id": workspace_id})

        # Delete all communities
        query_communities = """
        MATCH (c:Community {workspace_id: $workspace_id})
        DELETE c
        """
        self._execute_write(query_communities, {"workspace_id": workspace_id})

        logger.info(f"Deleted all graph data for workspace {workspace_id}")

    def export_subgraph(self, workspace_id: str) -> tuple[list[Entity], list[Relationship]]:
        """Export the entire graph for a workspace."""
        # Get all entities
        entities_query = """
        MATCH (e:Entity {workspace_id: $workspace_id})
        RETURN e
        """
        entity_results = self._execute_read(entities_query, {"workspace_id": workspace_id})
        entities = [self._node_to_entity(record["e"]) for record in entity_results]

        # Get all relationships
        rels_query = """
        MATCH (source:Entity {workspace_id: $workspace_id})-[r]->(target:Entity {workspace_id: $workspace_id})
        RETURN r, source.id AS source_id, target.id AS target_id
        """
        rel_results = self._execute_read(rels_query, {"workspace_id": workspace_id})
        relationships = [
            self._rel_to_relationship(record["r"], record.get("source_id"), record.get("target_id"))
            for record in rel_results
        ]

        logger.info(f"Exported {len(entities)} entities and {len(relationships)} relationships")
        return entities, relationships

    def _node_to_entity(self, node) -> Entity:
        """Convert a Neo4j node to an Entity object."""
        # Deserialize metadata from JSON string
        metadata_str = node.get("metadata", "{}")
        metadata: EntityMetadata = (
            json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
        )
        return Entity(
            id=node["id"],
            text=node["text"],
            type=EntityType(node["type"]),
            confidence=node["confidence"],
            metadata=metadata,
        )

    def _rel_to_relationship(
        self, rel, source_id: Optional[str] = None, target_id: Optional[str] = None
    ) -> Relationship:
        """Convert a Neo4j relationship to a Relationship object."""
        # Deserialize metadata from JSON string
        metadata_str = rel.get("metadata", "{}")
        metadata: RelationshipMetadata = (
            json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
        )

        # Handle both APOC dynamic types and fallback RELATED type
        rel_type_str = rel.type if hasattr(rel, "type") else rel.get("type", "RELATED_TO")

        # Try to convert to RelationType enum, fallback to RELATED_TO if not recognized
        try:
            rel_type = RelationType(rel_type_str)
        except ValueError:
            rel_type = RelationType.RELATED_TO

        return Relationship(
            id=rel.get("id", f"{source_id}_{rel_type_str}_{target_id}"),
            source_entity_id=source_id or "",
            target_entity_id=target_id or "",
            relation_type=rel_type,
            confidence=rel.get("confidence", 0.0),
            context=rel.get("context", ""),
            metadata=metadata,
        )

    def _node_to_community(self, node) -> Community:
        """Convert a Neo4j node to a Community object."""
        # Deserialize metadata from JSON string
        metadata_str = node.get("metadata", "{}")
        metadata: CommunityMetadata = (
            json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
        )
        return Community(
            id=node["id"],
            workspace_id=node["workspace_id"],
            entity_ids=node["entity_ids"],
            level=node["level"],
            summary=node.get("summary", ""),
            score=node.get("score", 0.0),
            metadata=metadata,
        )
