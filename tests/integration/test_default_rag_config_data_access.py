"""Integration tests for the DefaultRagConfigDataAccess component."""

import pytest

from src.domains.default_rag_config.data_access import DefaultRagConfigDataAccess
from src.domains.default_rag_config.models import (
    DefaultGraphRagConfig,
    DefaultRagConfig,
    DefaultVectorRagConfig,
)
from src.domains.default_rag_config.repositories import DefaultRagConfigRepository
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.sql_database import SqlDatabase


@pytest.mark.integration
class TestDefaultRagConfigDataAccessIntegration:
    """Integration tests for the DefaultRagConfigDataAccess component."""

    @pytest.fixture(scope="function")
    def default_rag_config_repository(self, db_session: SqlDatabase) -> DefaultRagConfigRepository:
        """Fixture to create a DefaultRagConfigRepository."""
        return DefaultRagConfigRepository(db_session)

    @pytest.fixture(scope="function")
    def data_access_with_cache(
        self,
        default_rag_config_repository: DefaultRagConfigRepository,
        cache_instance: RedisCache,
    ) -> DefaultRagConfigDataAccess:
        """Fixture for DefaultRagConfigDataAccess with a Redis cache."""
        return DefaultRagConfigDataAccess(
            repository=default_rag_config_repository, cache=cache_instance
        )

    def test_get_default_rag_config_returns_none_when_not_set(
        self, data_access_with_cache: DefaultRagConfigDataAccess
    ):
        """Test that get() returns None if no default config is in the database."""
        # Arrange
        # Ensure the table is clean for this test
        data_access_with_cache.repository.db.execute(
            "TRUNCATE default_rag_configs RESTART IDENTITY CASCADE;"
        )
        data_access_with_cache._invalidate_cache()

        # Act
        config = data_access_with_cache.get()

        # Assert
        assert config is None

    def test_update_and_get_default_rag_config(
        self, data_access_with_cache: DefaultRagConfigDataAccess
    ):
        """Test that updating and then getting the default RAG config works correctly."""
        # Arrange
        new_config = DefaultRagConfig(
            id=1,
            rag_type="vector",
            vector_config=DefaultVectorRagConfig(
                embedding_algorithm="test_embedder",
                chunking_algorithm="test_chunker",
                rerank_algorithm="test_reranker",
                chunk_size=512,
                chunk_overlap=50,
                top_k=5,
            ),
            graph_config=DefaultGraphRagConfig(
                entity_extraction_algorithm="test_entity_extractor",
                relationship_extraction_algorithm="test_relationship_extractor",
                clustering_algorithm="test_clusterer",
            ),
        )

        # Act: Update the config
        updated_config = data_access_with_cache.update(new_config)

        # Assert: The returned config from update should match the input
        assert updated_config.rag_type == "vector"
        assert updated_config.vector_config.chunk_size == 512
        assert updated_config.graph_config.clustering_algorithm == "test_clusterer"

        # Act: Get the config
        retrieved_config = data_access_with_cache.get()

        # Assert: The retrieved config should match what was saved
        assert retrieved_config is not None
        assert retrieved_config.id == updated_config.id
        assert retrieved_config.rag_type == "vector"
        assert retrieved_config.vector_config.embedding_algorithm == "test_embedder"
        assert retrieved_config.vector_config.chunk_size == 512
        assert retrieved_config.graph_config.entity_extraction_algorithm == "test_entity_extractor"
