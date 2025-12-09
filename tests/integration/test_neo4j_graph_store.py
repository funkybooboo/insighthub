"""Integration tests for Neo4jGraphStore using testcontainers."""

import re
from collections.abc import Generator

import pytest
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.neo4j import Neo4jContainer

from src.infrastructure.graph_stores.neo4j_graph_store import Neo4jGraphStore
from src.infrastructure.types.graph import Community, Entity, EntityType, Relationship, RelationType


@pytest.mark.integration
class TestNeo4jGraphStoreIntegration:
    """Neo4jGraphStore integration tests using testcontainers."""

    @pytest.fixture(scope="class")
    def neo4j_container_instance(self) -> Generator[Neo4jContainer, None, None]:
        """Spin up a Neo4j container for testing."""
        container = Neo4jContainer("neo4j:5.12", password="testpassword")
        # Use structured wait strategy instead of deprecated @wait_container_is_ready
        container = container.waiting_for(
            LogMessageWaitStrategy(re.compile(r".*Remote interface available at.*"))
        )
        container.start()
        yield container
        container.stop()

    @pytest.fixture(scope="function")
    def graph_store(
        self, neo4j_container_instance: Neo4jContainer
    ) -> Generator[Neo4jGraphStore, None, None]:
        """Fixture to create a Neo4jGraphStore instance and ensure clean state."""
        bolt_url = neo4j_container_instance.get_connection_url()
        store = Neo4jGraphStore(uri=bolt_url, username="neo4j", password="testpassword")

        # Ensure initial constraints/indexes for basic ops
        store.create_constraint("Entity", "id")
        store.create_index("Entity", ["workspace_id"])

        yield store

        # Clean up database after each test
        with store.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        store.close()

    def test_create_and_drop_constraint(self, graph_store: Neo4jGraphStore):
        """Test creating and dropping a uniqueness constraint."""
        # Arrange - already created in fixture
        # Test dropping
        graph_store.drop_constraint("Entity", "id")

        # Assert - attempt to create duplicate without constraint should succeed (no error)
        # This is a bit indirect, but Neo4j doesn't have a direct "list constraints" API easily consumable
        with graph_store.driver.session() as session:
            session.run("CREATE (e:Entity {id: 'c1', workspace_id: 'ws1'})")
            session.run(
                "CREATE (e:Entity {id: 'c1', workspace_id: 'ws1'})"
            )  # Should not raise error now

        # Recreate to ensure clean state for other tests
        graph_store.create_constraint("Entity", "id")

    def test_create_index(self, graph_store: Neo4jGraphStore):
        """Test creating an index."""
        # Arrange - already created in fixture
        # Act - try creating again, should not fail
        graph_store.create_index("Entity", ["workspace_id", "type"])

        # Assert - no exception indicates success

    def test_upsert_entity_and_get_by_id(self, graph_store: Neo4jGraphStore):
        """Test upserting an entity and retrieving it by ID."""
        # Arrange
        entity = Entity(
            id="ent1",
            text="Person A",
            type=EntityType.PERSON,
            confidence=0.9,
            metadata={"document_id": "doc1"},
        )
        workspace_id = "ws1"

        # Act
        graph_store.upsert_entities([entity], workspace_id)
        retrieved_entity = graph_store.get_entity_by_id("ent1", workspace_id)

        # Assert
        assert retrieved_entity is not None
        assert retrieved_entity.id == entity.id
        assert retrieved_entity.text == entity.text
        assert retrieved_entity.type == entity.type
        assert retrieved_entity.confidence == entity.confidence
        assert retrieved_entity.metadata["document_id"] == "doc1"

    def test_upsert_entity_updates_existing(self, graph_store: Neo4jGraphStore):
        """Test that upserting an entity with the same ID updates it."""
        # Arrange
        entity1 = Entity(
            id="ent2",
            text="Initial Text",
            type=EntityType.ORGANIZATION,
            confidence=0.5,
            metadata={"version": 1, "document_id": "doc_a"},
        )
        entity2 = Entity(
            id="ent2",
            text="Updated Text",
            type=EntityType.ORGANIZATION,
            confidence=0.8,
            metadata={"version": 2, "document_id": "doc_b"},
        )
        workspace_id = "ws1"

        graph_store.upsert_entities([entity1], workspace_id)

        # Act
        graph_store.upsert_entities([entity2], workspace_id)
        retrieved_entity = graph_store.get_entity_by_id("ent2", workspace_id)

        # Assert
        assert retrieved_entity is not None
        assert retrieved_entity.text == "Updated Text"
        assert retrieved_entity.confidence == 0.8
        assert retrieved_entity.metadata["version"] == 2  # Check if metadata is updated
        assert "doc_a" in retrieved_entity.metadata["document_ids"]  # document_ids should be merged
        assert "doc_b" in retrieved_entity.metadata["document_ids"]

    def test_upsert_relationship(self, graph_store: Neo4jGraphStore):
        """Test upserting a relationship between two entities."""
        # Arrange
        entity1 = Entity(
            id="e3a",
            text="Node A",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        entity2 = Entity(
            id="e3b",
            text="Node B",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        workspace_id = "ws1"
        graph_store.upsert_entities([entity1, entity2], workspace_id)

        relationship = Relationship(
            id="rel1",
            source_entity_id="e3a",
            target_entity_id="e3b",
            relation_type=RelationType.RELATED_TO,
            confidence=0.7,
            context="context string",
            metadata={"source": "extraction"},
        )

        # Act
        graph_store.upsert_relationships([relationship], workspace_id)

        # Assert (indirectly by traversing)
        subgraph = graph_store.traverse_graph(["e3a"], workspace_id, max_depth=1)
        assert len(subgraph.relationships) == 1
        assert subgraph.relationships[0].id == relationship.id
        assert subgraph.relationships[0].source_entity_id == relationship.source_entity_id
        assert subgraph.relationships[0].target_entity_id == relationship.target_entity_id

    def test_upsert_community(self, graph_store: Neo4jGraphStore):
        """Test upserting a community and linking it to entities."""
        # Arrange
        entity1 = Entity(
            id="c_e1",
            text="Entity 1",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        entity2 = Entity(
            id="c_e2",
            text="Entity 2",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        workspace_id = "ws1"
        graph_store.upsert_entities([entity1, entity2], workspace_id)

        community = Community(
            id="comm1",
            workspace_id=workspace_id,
            entity_ids=["c_e1", "c_e2"],
            level=1,
            summary="Two related entities",
            score=0.8,
            metadata={"algo": "leiden"},
        )

        # Act
        graph_store.upsert_communities([community], workspace_id)

        # Assert (check community node and relationships)
        with graph_store.driver.session() as session:
            result = session.run(
                f"""
                MATCH (c:Community {{id: '{community.id}', workspace_id: '{workspace_id}'}})
                RETURN c
            """
            )
            record = result.single()
            assert record is not None
            retrieved_node = record["c"]
            assert retrieved_node is not None
            assert retrieved_node["summary"] == community.summary

            # Check links
            result = session.run(
                f"""
                MATCH (e:Entity)-[:BELONGS_TO]->(c:Community {{id: '{community.id}', workspace_id: '{workspace_id}'}})
                RETURN e.id
            """
            )
            linked_entity_ids = {r["e.id"] for r in result}
            assert linked_entity_ids == {"c_e1", "c_e2"}

    def test_find_entities(self, graph_store: Neo4jGraphStore):
        """Test finding entities by text query."""
        # Arrange
        entity1 = Entity(
            id="f_e1",
            text="Apple Inc.",
            type=EntityType.ORGANIZATION,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        entity2 = Entity(
            id="f_e2",
            text="Orange Corp.",
            type=EntityType.ORGANIZATION,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        workspace_id = "ws1"
        graph_store.upsert_entities([entity1, entity2], workspace_id)

        # Act
        found_entities = graph_store.find_entities("apple", workspace_id, limit=5)

        # Assert
        assert len(found_entities) == 1
        assert found_entities[0].id == "f_e1"

    def test_delete_document_graph(self, graph_store: Neo4jGraphStore):
        """Test deleting graph data associated with a document."""
        # Arrange
        entity1 = Entity(
            id="ddg_e1",
            text="Doc Entity 1",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc_to_delete"},
        )
        entity2 = Entity(
            id="ddg_e2",
            text="Doc Entity 2",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc_to_delete"},
        )
        entity3 = Entity(
            id="ddg_e3",
            text="Other Doc Entity",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "other_doc"},
        )
        workspace_id = "ws1"
        graph_store.upsert_entities([entity1, entity2, entity3], workspace_id)

        # Act
        graph_store.delete_document_graph("doc_to_delete", workspace_id)

        # Assert
        assert graph_store.get_entity_by_id("ddg_e1", workspace_id) is None
        assert graph_store.get_entity_by_id("ddg_e2", workspace_id) is None
        assert graph_store.get_entity_by_id("ddg_e3", workspace_id) is not None

    def test_export_subgraph(self, graph_store: Neo4jGraphStore):
        """Test exporting all entities and relationships for a workspace."""
        # Arrange
        entity1 = Entity(
            id="es_e1",
            text="Export A",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        entity2 = Entity(
            id="es_e2",
            text="Export B",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        workspace_id = "ws1"
        graph_store.upsert_entities([entity1, entity2], workspace_id)
        relationship = Relationship(
            id="es_rel1",
            source_entity_id="es_e1",
            target_entity_id="es_e2",
            relation_type=RelationType.RELATED_TO,
            confidence=0.7,
            context="export context",
            metadata={},
        )
        graph_store.upsert_relationships([relationship], workspace_id)

        # Act
        entities, relationships = graph_store.export_subgraph(workspace_id)

        # Assert
        assert len(entities) == 2
        assert len(relationships) == 1
        assert any(e.id == "es_e1" for e in entities)
        assert any(r.id == "es_rel1" for r in relationships)

    def test_traverse_graph(self, graph_store: Neo4jGraphStore):
        """Test graph traversal functionality."""
        # Arrange
        entity1 = Entity(
            id="t_e1",
            text="Main Node",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        entity2 = Entity(
            id="t_e2",
            text="Connected Node",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        entity3 = Entity(
            id="t_e3",
            text="Further Node",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        workspace_id = "ws1"
        graph_store.upsert_entities([entity1, entity2, entity3], workspace_id)
        graph_store.upsert_relationships(
            [
                Relationship(
                    id="t_rel1",
                    source_entity_id="t_e1",
                    target_entity_id="t_e2",
                    relation_type=RelationType.RELATED_TO,
                    confidence=1.0,
                    context="",
                    metadata={},
                ),
                Relationship(
                    id="t_rel2",
                    source_entity_id="t_e2",
                    target_entity_id="t_e3",
                    relation_type=RelationType.RELATED_TO,
                    confidence=1.0,
                    context="",
                    metadata={},
                ),
            ],
            workspace_id,
        )

        # Act
        subgraph = graph_store.traverse_graph(["t_e1"], workspace_id, max_depth=2)

        # Assert
        assert len(subgraph.entities) == 3
        assert len(subgraph.relationships) == 2
        assert "t_e1" in [e.id for e in subgraph.entities]
        assert "t_e2" in [e.id for e in subgraph.entities]
        assert "t_e3" in [e.id for e in subgraph.entities]
        assert "t_rel1" in [r.id for r in subgraph.relationships]
        assert "t_rel2" in [r.id for r in subgraph.relationships]

    def test_delete_workspace_graph(self, graph_store: Neo4jGraphStore):
        """Test deleting all entities, relationships, and communities for a workspace."""
        # Arrange
        entity = Entity(
            id="dwg_e1",
            text="Workspace Entity",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        workspace_id = "ws2"
        graph_store.upsert_entities([entity], workspace_id)
        community = Community(
            id="dwg_comm1",
            workspace_id=workspace_id,
            entity_ids=["dwg_e1"],
            level=1,
            summary="Test Community",
            score=1.0,
            metadata={},
        )
        graph_store.upsert_communities([community], workspace_id)

        # Act
        graph_store.delete_workspace_graph(workspace_id)

        # Assert
        assert graph_store.get_entity_by_id("dwg_e1", workspace_id) is None
        with graph_store.driver.session() as session:
            result = session.run(f"MATCH (c:Community {{workspace_id: '{workspace_id}'}}) RETURN c")
            assert result.single() is None

    def test_get_communities(self, graph_store: Neo4jGraphStore):
        """Test retrieving communities linked to entities."""
        # Arrange
        entity1 = Entity(
            id="gc_e1",
            text="Community Entity 1",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        entity2 = Entity(
            id="gc_e2",
            text="Community Entity 2",
            type=EntityType.PERSON,
            confidence=1.0,
            metadata={"document_id": "doc1"},
        )
        workspace_id = "ws1"
        graph_store.upsert_entities([entity1, entity2], workspace_id)

        community1 = Community(
            id="gc_comm1",
            workspace_id=workspace_id,
            entity_ids=["gc_e1"],
            level=1,
            summary="Community 1",
            score=0.9,
            metadata={},
        )
        community2 = Community(
            id="gc_comm2",
            workspace_id=workspace_id,
            entity_ids=["gc_e1", "gc_e2"],
            level=2,
            summary="Community 2",
            score=0.8,
            metadata={},
        )
        graph_store.upsert_communities([community1, community2], workspace_id)

        # Act
        found_communities = graph_store.get_communities(["gc_e1"], workspace_id)

        # Assert
        assert len(found_communities) == 2
        assert any(c.id == "gc_comm1" for c in found_communities)
        assert any(c.id == "gc_comm2" for c in found_communities)

    def test_traverse_graph_with_empty_ids(self, graph_store: Neo4jGraphStore):
        """Test that traversing with empty entity IDs returns an empty subgraph."""
        # Act
        subgraph = graph_store.traverse_graph([], "ws1", max_depth=2)

        # Assert
        assert len(subgraph.entities) == 0
        assert len(subgraph.relationships) == 0
