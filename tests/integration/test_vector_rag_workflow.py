"""Integration tests for Vector RAG workflows using testcontainers.

Tests the complete Vector RAG pipeline with a real Qdrant database instance.
"""

import io
from collections.abc import Generator

import pytest
from returns.result import Success
from testcontainers.qdrant import QdrantContainer

from src.infrastructure.rag.steps.general.chunking.sentence_document_chunker import (
    SentenceDocumentChunker,
)
from src.infrastructure.rag.steps.general.parsing.text_document_parser import TextDocumentParser
from src.infrastructure.rag.steps.vector_rag.embedding.dummy_embedding_provider import (
    DummyEmbeddingProvider,
)
from src.infrastructure.rag.workflows.add_document.vector_rag_add_document_workflow import (
    VectorRagAddDocumentWorkflow,
)
from src.infrastructure.rag.workflows.query.vector_rag_query_workflow import VectorRagQueryWorkflow
from src.infrastructure.vector_stores.qdrant_vector_store import QdrantVectorStore


@pytest.mark.integration
class TestVectorRagWorkflowIntegration:
    """Vector RAG workflow integration tests using testcontainers."""

    @pytest.fixture(scope="class")
    def qdrant_container_instance(self) -> Generator[QdrantContainer, None, None]:
        """Spin up a Qdrant container for testing."""
        container = QdrantContainer("qdrant/qdrant:latest")
        container.start()
        yield container
        container.stop()

    @pytest.fixture(scope="function")
    def vector_store(
        self, qdrant_container_instance: QdrantContainer
    ) -> Generator[QdrantVectorStore, None, None]:
        """Create a vector store connected to the test Qdrant container."""
        host = qdrant_container_instance.get_container_host_ip()
        port = qdrant_container_instance.get_exposed_port(6333)
        store = QdrantVectorStore(
            url=f"http://{host}:{port}", collection_name="test_collection", vector_size=4
        )
        yield store
        store.clear()  # Clean up collection after each test

    @pytest.fixture(scope="function")
    def embedding_provider(self) -> DummyEmbeddingProvider:
        """Fixture for a DummyEmbeddingProvider."""
        return DummyEmbeddingProvider(dimension=4)

    @pytest.fixture(scope="function")
    def add_document_workflow(
        self, vector_store: QdrantVectorStore, embedding_provider: DummyEmbeddingProvider
    ) -> VectorRagAddDocumentWorkflow:
        """Create an add document workflow for testing."""
        parser = TextDocumentParser()
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=20)

        workflow = VectorRagAddDocumentWorkflow(
            parser=parser,
            chunker=chunker,
            embedder=embedding_provider,
            vector_store=vector_store,
        )
        return workflow

    @pytest.fixture(scope="function")
    def query_workflow(
        self, vector_store: QdrantVectorStore, embedding_provider: DummyEmbeddingProvider
    ) -> VectorRagQueryWorkflow:
        """Create a query workflow for testing."""
        workflow = VectorRagQueryWorkflow(
            embedder=embedding_provider,
            vector_store=vector_store,
        )
        return workflow

    def test_add_document_and_query_workflow_success(
        self,
        add_document_workflow: VectorRagAddDocumentWorkflow,
        query_workflow: VectorRagQueryWorkflow,
    ):
        """Test successfully adding a document and then querying it."""
        # Arrange
        document_text = "This is a test document for the vector RAG workflow. It contains important information."
        raw_document = io.BytesIO(document_text.encode("utf-8"))
        workspace_id = "test_workspace_1"
        document_id = "test_doc_1"

        # Act - Add document
        add_result = add_document_workflow.execute(
            raw_document=raw_document,
            document_id=document_id,
            workspace_id=workspace_id,
            metadata={"source": "test_source"},
        )

        # Assert add operation
        assert isinstance(add_result, Success)
        chunk_count = add_result.unwrap()
        assert chunk_count > 0

        # Act - Query the vector store
        query_text = "What is this document about?"
        query_results = query_workflow.execute(
            query_text=query_text, top_k=1, filters={"workspace_id": workspace_id}
        )

        # Assert query operation
        assert isinstance(query_results, list)
        assert len(query_results) > 0
        assert "vector RAG workflow" in query_results[0].text
        assert query_results[0].document_id == document_id
        assert query_results[0].metadata["source"] == "test_source"
