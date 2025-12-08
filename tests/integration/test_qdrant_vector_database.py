"""Integration tests for QdrantVectorDatabase using testcontainers."""

from collections.abc import Generator

import pytest
from testcontainers.qdrant import QdrantContainer

from src.infrastructure.vector_stores.qdrant_vector_database import QdrantVectorDatabase


@pytest.mark.integration
class TestQdrantVectorDatabaseIntegration:
    """QdrantVectorDatabase integration tests using testcontainers."""

    @pytest.fixture(scope="function")
    def qdrant_container_instance(self) -> QdrantContainer:
        """Spin up a Qdrant container for testing."""
        container = QdrantContainer("qdrant/qdrant:latest")
        container.start()
        yield container
        container.stop()

    @pytest.fixture(scope="function")
    def qdrant_db(
        self, qdrant_container_instance: QdrantContainer
    ) -> Generator[QdrantVectorDatabase, None, None]:
        """Fixture to create a QdrantVectorDatabase instance."""
        host = qdrant_container_instance.get_container_host_ip()
        port = qdrant_container_instance.get_exposed_port(6333)
        db = QdrantVectorDatabase(
            url=f"http://{host}:{port}", collection_name="test_collection", vector_size=4
        )
        yield db
        db.clear()  # Clean up collection after each test

    def test_upsert_and_similarity_search(self, qdrant_db: QdrantVectorDatabase):
        """Test upserting a single vector and performing a similarity search."""
        # Arrange
        vector_id = "test_id_1"
        vector = [0.1, 0.2, 0.3, 0.4]
        metadata: dict[str, str | int | float | bool | None] = {
            "text": "hello world",
            "source": "test_document",
        }

        # Act
        qdrant_db.upsert(vector_id, vector, metadata)
        results = qdrant_db.similarity_search(vector, top_k=1)

        # Assert
        assert len(results) == 1
        assert results[0].id == vector_id
        assert results[0].payload["text"] == "hello world"
        assert results[0].score > 0.9  # Cosine similarity with itself should be high

    def test_upsert_batch_and_count(self, qdrant_db: QdrantVectorDatabase):
        """Test upserting multiple vectors in a batch and checking the count."""
        # Arrange
        items: list[tuple[str, list[float], dict[str, str | int | float | bool | None]]] = [
            ("id_2", [0.5, 0.6, 0.7, 0.8], {"data": "item 2"}),
            ("id_3", [0.9, 1.0, 1.1, 1.2], {"data": "item 3"}),
        ]

        # Act
        qdrant_db.upsert_batch(items)
        count = qdrant_db.count()

        # Assert
        assert count == 2

    def test_delete_and_exists(self, qdrant_db: QdrantVectorDatabase):
        """Test deleting a vector and checking its existence."""
        # Arrange
        vector_id = "to_delete"
        qdrant_db.upsert(vector_id, [0.1, 0.1, 0.1, 0.1], {})
        assert qdrant_db.exists(vector_id) is True

        # Act
        deleted = qdrant_db.delete(vector_id)
        exists_after_delete = qdrant_db.exists(vector_id)

        # Assert
        assert deleted is True
        assert exists_after_delete is False

    def test_delete_batch(self, qdrant_db: QdrantVectorDatabase):
        """Test deleting multiple vectors in a batch."""
        # Arrange
        items: list[tuple[str, list[float], dict[str, str | int | float | bool | None]]] = [
            ("batch_id_1", [0.1, 0.1, 0.1, 0.1], {}),
            ("batch_id_2", [0.2, 0.2, 0.2, 0.2], {}),
            ("batch_id_3", [0.3, 0.3, 0.3, 0.3], {}),
        ]
        qdrant_db.upsert_batch(items)
        assert qdrant_db.count() == 3

        # Act
        deleted_count = qdrant_db.delete_batch(["batch_id_1", "batch_id_3"])

        # Assert
        assert deleted_count == 2
        assert qdrant_db.exists("batch_id_1") is False
        assert qdrant_db.exists("batch_id_2") is True
        assert qdrant_db.exists("batch_id_3") is False

    def test_clear_collection(self, qdrant_db: QdrantVectorDatabase):
        """Test clearing the entire collection."""
        # Arrange
        qdrant_db.upsert("id_4", [0.1, 0.2, 0.3, 0.4], {})
        assert qdrant_db.count() == 1

        # Act
        qdrant_db.clear()
        count_after_clear = qdrant_db.count()

        # Assert
        assert count_after_clear == 0

    def test_delete_by_filter(self, qdrant_db: QdrantVectorDatabase):
        """Test deleting vectors based on a metadata filter."""
        # Arrange
        qdrant_db.upsert(
            "doc_a_chunk_1", [0.1, 0.1, 0.1, 0.1], {"document_id": "doc_a", "version": 1}
        )
        qdrant_db.upsert(
            "doc_a_chunk_2", [0.2, 0.2, 0.2, 0.2], {"document_id": "doc_a", "version": 2}
        )
        qdrant_db.upsert(
            "doc_b_chunk_1", [0.3, 0.3, 0.3, 0.3], {"document_id": "doc_b", "version": 1}
        )
        assert qdrant_db.count() == 3

        # Act
        deleted_count = qdrant_db.delete_by_filter({"document_id": "doc_a"})

        # Assert
        assert deleted_count == 2
        assert qdrant_db.exists("doc_a_chunk_1") is False
        assert qdrant_db.exists("doc_a_chunk_2") is False
        assert qdrant_db.exists("doc_b_chunk_1") is True

    def test_search_with_score_threshold(self, qdrant_db: QdrantVectorDatabase):
        """Test similarity search with a minimum score threshold."""
        # Arrange
        qdrant_db.upsert("vec_1", [1.0, 0.0, 0.0, 0.0], {})
        qdrant_db.upsert("vec_2", [0.9, 0.1, 0.0, 0.0], {})  # High similarity
        qdrant_db.upsert("vec_3", [0.1, 0.9, 0.0, 0.0], {})  # Low similarity

        # Act
        query_vector = [1.0, 0.0, 0.0, 0.0]
        results_high_threshold = qdrant_db.search_with_score_threshold(
            query_vector, top_k=3, score_threshold=0.95
        )
        results_low_threshold = qdrant_db.search_with_score_threshold(
            query_vector, top_k=3, score_threshold=0.8
        )

        # Assert
        assert len(results_high_threshold) == 2
        assert {r.id for r in results_high_threshold} == {"vec_1", "vec_2"}

        assert len(results_low_threshold) == 2
        assert {r.id for r in results_low_threshold} == {"vec_1", "vec_2"}
