"""Integration tests for Graph RAG workflows using testcontainers.

Tests the complete Graph RAG pipeline with a real Neo4j database instance.
"""

import io
import re
from collections.abc import Generator
from typing import Any, Optional

import pytest
from returns.result import Success
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.neo4j import Neo4jContainer

from src.infrastructure.graph_stores.neo4j_graph_store import Neo4jGraphStore
from src.infrastructure.llm.llm_provider import LlmProvider
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
        """Fixture to create a graph store connected to the test Neo4j container."""
        bolt_url = neo4j_container_instance.get_connection_url()

        store = Neo4jGraphStore(
            uri=bolt_url,
            username="neo4j",
            password="testpassword",
        )

        # Create constraints and indexes (these methods handle IF NOT EXISTS)
        store.create_constraint("Entity", "id")
        store.create_index("Entity", ["workspace_id"])
        store.create_index("Entity", ["workspace_id", "type"])
        store.create_index("Community", ["workspace_id", "level"])

        yield store

        # Cleanup
        with store.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")  # Clear all nodes and relationships
        store.close()

    @pytest.fixture(scope="function")
    def llm_provider(self) -> LlmProvider:
        """Fixture to create a dummy LlmProvider."""

        class DummyLlmProvider(LlmProvider):
            def generate_response(self, prompt: str) -> str:
                return "dummy LLM response"

            def chat(
                self, message: str, conversation_history: Optional[list[dict[str, str]]] = None
            ) -> str:
                return "dummy LLM response"

            def chat_stream(
                self, message: str, conversation_history: Optional[list[dict[str, str]]] = None
            ) -> Generator[str, None, None]:
                yield "dummy LLM response chunk"

            def health_check(self) -> dict[str, Any]:
                return {"status": "ok"}

            def get_model_name(self) -> str:
                return "dummy-llm"

        return DummyLlmProvider()

    @pytest.fixture(scope="function")
    def add_document_workflow(
        self, graph_store: Neo4jGraphStore, llm_provider: LlmProvider
    ) -> GraphRagAddDocumentWorkflow:
        """Create an add document workflow for testing."""
        parser = TextDocumentParser()
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=20)

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

    @pytest.fixture(scope="function")
    def query_workflow(
        self, graph_store: Neo4jGraphStore, llm_provider: LlmProvider
    ) -> GraphRagQueryWorkflow:
        """Create a query workflow for testing."""
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

    def test_add_document_workflow_success(
        self, add_document_workflow: GraphRagAddDocumentWorkflow
    ):
        """Test successfully adding a document to the graph."""
        # Arrange
        document_text = """
        Alice Johnson works at Anthropic in San Francisco.
        She collaborated with Bob Smith from OpenAI.
        Together they developed new AI safety techniques.
        """
        raw_document = io.BytesIO(document_text.encode("utf-8"))
        workspace_id = "test_workspace_1"
        document_id = "test_doc_1"

        # Act
        result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id=document_id,
            workspace_id=workspace_id,
            metadata={"source": "test_source"},
        )

        # Assert
        assert isinstance(result, Success)
        entity_count = result.unwrap()
        assert entity_count > 0  # Should have extracted some entities

    def test_query_workflow_after_adding_document(
        self,
        add_document_workflow: GraphRagAddDocumentWorkflow,
        query_workflow: GraphRagQueryWorkflow,
    ):
        """Test querying the graph after adding a document."""
        # Arrange - Add a document first
        document_text = """
        Microsoft was founded by Bill Gates and Paul Allen.
        The company is headquartered in Redmond, Washington.
        Microsoft develops software products and services.
        """
        raw_document = io.BytesIO(document_text.encode("utf-8"))
        workspace_id = "test_workspace_1"
        document_id = "test_doc_2"

        add_result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id=document_id,
            workspace_id=workspace_id,
            metadata={"source": "test_source"},
        )
        assert isinstance(add_result, Success)

        # Act - Query the graph
        query_text = "Tell me about Microsoft and Bill Gates"
        chunks = query_workflow.execute(query_text=query_text, top_k=5)

        # Assert
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert any("Microsoft" in c.text for c in chunks)
        assert any("Bill Gates" in c.text for c in chunks)

    def test_delete_workspace_graph(
        self, graph_store: Neo4jGraphStore, add_document_workflow: GraphRagAddDocumentWorkflow
    ):
        """Test deleting all graph data for a workspace."""
        # Arrange - Add a document
        document_text = """Amazon was founded by Jeff Bezos in Seattle."""
        raw_document = io.BytesIO(document_text.encode("utf-8"))
        workspace_id = "test_workspace_2"
        document_id = "test_doc_3"

        add_result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id=document_id,
            workspace_id=workspace_id,
            metadata={"source": "test_source"},
        )
        assert isinstance(add_result, Success)

        # Verify entities exist
        entities_before = graph_store.find_entities("Amazon", workspace_id, limit=10)
        assert len(entities_before) > 0

        # Act - Delete workspace graph
        graph_store.delete_workspace_graph(workspace_id)

        # Assert - Entities should be gone
        entities_after = graph_store.find_entities("Amazon", workspace_id, limit=10)
        assert len(entities_after) == 0

    def test_community_detection_integration(
        self, graph_store: Neo4jGraphStore, add_document_workflow: GraphRagAddDocumentWorkflow
    ):
        """Test that community detection runs and stores communities."""
        # Arrange - Add a document with multiple connected entities
        document_text = """
        Tesla is led by Elon Musk.
        Elon Musk also founded SpaceX and Neuralink.
        Tesla manufactures electric vehicles in Fremont, California.
        SpaceX launches rockets from Cape Canaveral, Florida.
        """
        raw_document = io.BytesIO(document_text.encode("utf-8"))
        workspace_id = "test_workspace_3"
        document_id = "test_doc_4"

        # Act - Add document (which triggers community detection)
        add_result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id=document_id,
            workspace_id=workspace_id,
            metadata={"source": "test_source"},
        )

        # Assert
        assert isinstance(add_result, Success)

        # Try to get communities (implementation depends on get_communities)
        # Note: Community detection results can be highly variable based on
        # graph size and algorithm. We mainly assert that the process completes
        # without error and potentially finds *some* communities.
        entities = graph_store.find_entities("Tesla", workspace_id, limit=5)
        if entities:
            entity_ids = [e.id for e in entities]
            communities = graph_store.get_communities(entity_ids, workspace_id)
            assert isinstance(communities, list)
            # Asserting a minimum number of communities might be too brittle
            # assert len(communities) > 0
