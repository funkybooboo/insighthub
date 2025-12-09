"""Integration tests for QdrantVectorStore using testcontainers."""

import re
from collections.abc import Generator

import pytest
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.qdrant import QdrantContainer

from src.infrastructure.types.common import MetadataDict
from src.infrastructure.vector_stores.qdrant_vector_store import QdrantVectorStore


@pytest.mark.integration
class TestQdrantVectorStoreIntegration:
    """QdrantVectorStore integration tests using testcontainers."""

    @pytest.fixture(scope="function")
    def qdrant_container_instance(self) -> QdrantContainer:
        """Spin up a Qdrant container for testing."""
        container = QdrantContainer("qdrant/qdrant:v1.16.1")
        # Use structured wait strategy instead of deprecated @wait_container_is_ready
        container = container.waiting_for(
            LogMessageWaitStrategy(
                re.compile(r".*Actix runtime found; starting in Actix runtime.*")
            )
        )
        container.start()
        yield container
        container.stop()

    @pytest.fixture(scope="function")
    def qdrant_store(
        self, qdrant_container_instance: QdrantContainer
    ) -> Generator[QdrantVectorStore, None, None]:
        """Fixture to create a QdrantVectorStore instance."""
        host = qdrant_container_instance.get_container_host_ip()
        port = qdrant_container_instance.get_exposed_port(6333)
        store = QdrantVectorStore(
            url=f"http://{host}:{port}", collection_name="test_collection", vector_size=4
        )
        yield store
        store.clear()  # Clean up collection after each test

    def test_add_and_search(self, qdrant_store: QdrantVectorStore):
        """Test adding vectors and performing a search."""
        # Arrange
        vectors = [[0.1, 0.2, 0.3, 0.4]]
        ids = ["test_id_1"]
        payloads: list[MetadataDict] = [{"text": "hello world", "source": "test_document"}]

        # Act
        qdrant_store.add(vectors, ids, payloads)
        results = qdrant_store.search([0.1, 0.2, 0.3, 0.4], top_k=1)

        # Assert
        assert len(results) == 1
        chunk, score = results[0]
        assert chunk.id == "test_id_1"
        assert chunk.text == "hello world"
        assert score > 0.9  # Cosine similarity with itself should be high

    def test_add_batch(self, qdrant_store: QdrantVectorStore):
        """Test adding multiple vectors in a batch."""
        # Arrange
        vectors = [[0.5, 0.6, 0.7, 0.8], [0.9, 1.0, 1.1, 1.2]]
        ids = ["id_2", "id_3"]
        payloads: list[MetadataDict] = [
            {"text": "item 2", "document_id": "doc1"},
            {"text": "item 3", "document_id": "doc1"},
        ]

        # Act
        qdrant_store.add(vectors, ids, payloads)
        results = qdrant_store.search([0.5, 0.6, 0.7, 0.8], top_k=2)

        # Assert
        assert len(results) == 2

    def test_delete_by_filter(self, qdrant_store: QdrantVectorStore):
        """Test deleting vectors based on a metadata filter."""
        # Arrange
        vectors = [
            [0.1, 0.1, 0.1, 0.1],
            [0.2, 0.2, 0.2, 0.2],
            [0.3, 0.3, 0.3, 0.3],
        ]
        ids = ["doc_a_chunk_1", "doc_a_chunk_2", "doc_b_chunk_1"]
        payloads: list[MetadataDict] = [
            {"document_id": "doc_a", "text": "chunk 1", "version": 1},
            {"document_id": "doc_a", "text": "chunk 2", "version": 2},
            {"document_id": "doc_b", "text": "chunk 1", "version": 1},
        ]
        qdrant_store.add(vectors, ids, payloads)

        # Act
        deleted_count = qdrant_store.delete({"document_id": "doc_a"})

        # Assert
        assert deleted_count == 2
        # Verify remaining vectors
        results = qdrant_store.search([0.3, 0.3, 0.3, 0.3], top_k=3)
        assert len(results) == 1
        assert results[0][0].id == "doc_b_chunk_1"

    def test_clear_collection(self, qdrant_store: QdrantVectorStore):
        """Test clearing the entire collection."""
        # Arrange
        payloads: list[MetadataDict] = [{"text": "test"}]
        qdrant_store.add([[0.1, 0.2, 0.3, 0.4]], ["id_4"], payloads)
        results_before = qdrant_store.search([0.1, 0.2, 0.3, 0.4], top_k=1)
        assert len(results_before) == 1

        # Act
        qdrant_store.clear()
        results_after = qdrant_store.search([0.1, 0.2, 0.3, 0.4], top_k=1)

        # Assert
        assert len(results_after) == 0

    def test_search_with_filters(self, qdrant_store: QdrantVectorStore):
        """Test searching with metadata filters."""
        # Arrange
        vectors = [
            [1.0, 0.0, 0.0, 0.0],
            [0.9, 0.1, 0.0, 0.0],
            [0.1, 0.9, 0.0, 0.0],
        ]
        ids = ["vec_1", "vec_2", "vec_3"]
        payloads: list[MetadataDict] = [
            {"document_id": "doc_a", "text": "vec 1"},
            {"document_id": "doc_a", "text": "vec 2"},
            {"document_id": "doc_b", "text": "vec 3"},
        ]
        qdrant_store.add(vectors, ids, payloads)

        # Act
        results_filtered = qdrant_store.search(
            [1.0, 0.0, 0.0, 0.0], top_k=3, filters={"document_id": "doc_a"}
        )
        results_unfiltered = qdrant_store.search([1.0, 0.0, 0.0, 0.0], top_k=3)

        # Assert
        assert len(results_filtered) == 2
        assert all(chunk.document_id == "doc_a" for chunk, _ in results_filtered)
        assert len(results_unfiltered) == 3
