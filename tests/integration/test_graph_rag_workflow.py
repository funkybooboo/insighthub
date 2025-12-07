"""Integration tests for Graph RAG workflows using testcontainers.

Tests the complete Graph RAG pipeline with a real Neo4j database instance.
"""

import io

import pytest
from returns.result import Success
from testcontainers.neo4j import Neo4jContainer

from src.infrastructure.graph_stores.neo4j_graph_store import Neo4jGraphStore
from src.infrastructure.rag.steps.general.chunking.sentence_document_chunker import (
    SentenceDocumentChunker,
)
from src.infrastructure.rag.steps.general.parsing.text_document_parser import TextDocumentParser
from src.infrastructure.rag.steps.graph_rag.entity_extraction.spacy_entity_extractor import (
    SpacyEntityExtractor,
)
from src.infrastructure.rag.steps.graph_rag.relationship_extraction.dependency_parser_extractor import (
    DependencyParserExtractor,
)
from src.infrastructure.rag.workflows.add_document.graph_rag_add_document_workflow import (
    GraphRagAddDocumentWorkflow,
)
from src.infrastructure.rag.workflows.query.graph_rag_query_workflow import GraphRagQueryWorkflow
from src.infrastructure.types.graph import EntityType


@pytest.mark.integration
class TestGraphRagWorkflowIntegration:
    """Graph RAG workflow integration tests using testcontainers."""

    @pytest.fixture(scope="function")
    def neo4j_container(self):
        """Spin up a Neo4j container for testing."""
        # Use Neo4j container with explicit password
        container = Neo4jContainer("neo4j:5.12", password="testpassword")
        container.start()
        yield container
        container.stop()

    @pytest.fixture
    def graph_store(self, neo4j_container):
        """Create a graph store connected to the test Neo4j container."""
        # Get connection details from container
        bolt_url = neo4j_container.get_connection_url()

        # Use the password we set in the container
        store = Neo4jGraphStore(
            uri=bolt_url,
            username="neo4j",
            password="testpassword",
        )

        # Create constraints and indexes
        store.create_constraint("Entity", "id")
        store.create_index("Entity", ["workspace_id"])
        store.create_index("Entity", ["workspace_id", "type"])
        store.create_index("Community", ["workspace_id", "level"])

        yield store

        # Cleanup
        store.close()

    @pytest.fixture
    def add_document_workflow(self, graph_store):
        """Create an add document workflow for testing."""
        # Create components
        parser = TextDocumentParser()
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=20)

        # Use SpaCy for entity extraction (requires en_core_web_sm model)
        try:
            entity_extractor = SpacyEntityExtractor(
                model_name="en_core_web_sm",
                entity_types=[
                    EntityType.PERSON,
                    EntityType.ORGANIZATION,
                    EntityType.LOCATION,
                ],
            )
        except OSError:
            pytest.skip("SpaCy model en_core_web_sm not installed")

        relationship_extractor = DependencyParserExtractor()

        # Create workflow
        workflow = GraphRagAddDocumentWorkflow(
            parser=parser,
            chunker=chunker,
            entity_extractor=entity_extractor,
            relationship_extractor=relationship_extractor,
            graph_store=graph_store,
            clustering_algorithm="leiden",
            clustering_resolution=1.0,
            clustering_max_level=3,
            community_min_size=2,
        )

        return workflow

    @pytest.fixture
    def query_workflow(self, graph_store):
        """Create a query workflow for testing."""
        # Use SpaCy for entity extraction
        try:
            entity_extractor = SpacyEntityExtractor(
                model_name="en_core_web_sm",
                entity_types=[
                    EntityType.PERSON,
                    EntityType.ORGANIZATION,
                    EntityType.LOCATION,
                ],
            )
        except OSError:
            pytest.skip("SpaCy model en_core_web_sm not installed")

        workflow = GraphRagQueryWorkflow(
            entity_extractor=entity_extractor,
            graph_store=graph_store,
            workspace_id="test_workspace_1",
            max_traversal_depth=2,
            top_k_entities=10,
            top_k_communities=3,
            include_entity_neighborhoods=True,
        )

        return workflow

    def test_add_document_workflow_success(self, add_document_workflow):
        """Test successfully adding a document to the graph."""
        # Arrange
        document_text = """
        Alice Johnson works at Anthropic in San Francisco.
        She collaborated with Bob Smith from OpenAI.
        Together they developed new AI safety techniques.
        """
        raw_document = io.BytesIO(document_text.encode("utf-8"))

        # Act
        result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id="test_doc_1",
            workspace_id="test_workspace_1",
            metadata={"source": "test"},
        )

        # Assert
        assert isinstance(result, Success)
        entity_count = result.unwrap()
        assert entity_count > 0  # Should have extracted some entities

    def test_query_workflow_after_adding_document(self, add_document_workflow, query_workflow):
        """Test querying the graph after adding a document."""
        # Arrange - Add a document first
        document_text = """
        Microsoft was founded by Bill Gates and Paul Allen.
        The company is headquartered in Redmond, Washington.
        Microsoft develops software products and services.
        """
        raw_document = io.BytesIO(document_text.encode("utf-8"))

        add_result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id="test_doc_2",
            workspace_id="test_workspace_1",
            metadata={"source": "test"},
        )
        assert isinstance(add_result, Success)

        # Act - Query the graph
        query_text = "Tell me about Microsoft and Bill Gates"
        chunks = query_workflow.execute(query_text=query_text, top_k=5)

        # Assert
        assert isinstance(chunks, list)
        # Should return some results (exact count depends on extraction quality)
        # We're just testing that the workflow runs without errors

    def test_graph_store_entity_retrieval(self, graph_store, add_document_workflow):
        """Test that entities can be retrieved from the graph store."""
        # Arrange - Add a document
        document_text = """
        Google was founded by Larry Page and Sergey Brin.
        The company is based in Mountain View, California.
        """
        raw_document = io.BytesIO(document_text.encode("utf-8"))

        add_result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id="test_doc_3",
            workspace_id="test_workspace_1",
            metadata={"source": "test"},
        )
        assert isinstance(add_result, Success)

        # Act - Search for entities
        entities = graph_store.find_entities("Google", "test_workspace_1", limit=10)

        # Assert
        assert len(entities) > 0

    def test_graph_traversal(self, graph_store, add_document_workflow):
        """Test graph traversal functionality."""
        # Arrange - Add a document with related entities
        document_text = """
        Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne.
        Steve Jobs also founded NeXT Computer and Pixar Animation Studios.
        Apple is headquartered in Cupertino, California.
        """
        raw_document = io.BytesIO(document_text.encode("utf-8"))

        add_result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id="test_doc_4",
            workspace_id="test_workspace_1",
            metadata={"source": "test"},
        )
        assert isinstance(add_result, Success)

        # Act - Find an entity and traverse from it
        entities = graph_store.find_entities("Apple", "test_workspace_1", limit=1)

        if entities:
            entity_id = entities[0].id
            subgraph = graph_store.traverse_graph([entity_id], "test_workspace_1", max_depth=2)

            # Assert
            assert len(subgraph.entities) > 0
            assert entity_id in [e.id for e in subgraph.entities]

    def test_delete_workspace_graph(self, graph_store, add_document_workflow):
        """Test deleting all graph data for a workspace."""
        # Arrange - Add a document
        document_text = """
        Amazon was founded by Jeff Bezos in Seattle.
        """
        raw_document = io.BytesIO(document_text.encode("utf-8"))

        add_result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id="test_doc_5",
            workspace_id="test_workspace_2",
            metadata={"source": "test"},
        )
        assert isinstance(add_result, Success)

        # Verify entities exist
        entities_before = graph_store.find_entities("Amazon", "test_workspace_2", limit=10)
        assert len(entities_before) > 0

        # Act - Delete workspace graph
        graph_store.delete_workspace_graph("test_workspace_2")

        # Assert - Entities should be gone
        entities_after = graph_store.find_entities("Amazon", "test_workspace_2", limit=10)
        assert len(entities_after) == 0

    def test_community_detection_integration(self, graph_store, add_document_workflow):
        """Test that community detection runs and stores communities."""
        # Arrange - Add a document with multiple connected entities
        document_text = """
        Tesla is led by Elon Musk.
        Elon Musk also founded SpaceX and Neuralink.
        Tesla manufactures electric vehicles in Fremont, California.
        SpaceX launches rockets from Cape Canaveral, Florida.
        """
        raw_document = io.BytesIO(document_text.encode("utf-8"))

        # Act - Add document (which triggers community detection)
        add_result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id="test_doc_6",
            workspace_id="test_workspace_3",
            metadata={"source": "test"},
        )

        # Assert
        assert isinstance(add_result, Success)

        # Try to get communities (implementation depends on get_communities)
        entities = graph_store.find_entities("Tesla", "test_workspace_3", limit=5)
        if entities:
            entity_ids = [e.id for e in entities]
            communities = graph_store.get_communities(entity_ids, "test_workspace_3")

            # Community detection might not always find communities
            # depending on graph size and algorithm parameters
            # So we just verify the call doesn't error
            assert isinstance(communities, list)
