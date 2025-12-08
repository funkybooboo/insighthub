"""Integration tests for the DefaultRagConfigService component."""

import pytest

from src.domains.default_rag_config.data_access import DefaultRagConfigDataAccess
from src.domains.default_rag_config.models import DefaultGraphRagConfig, DefaultRagConfig, DefaultVectorRagConfig
from src.domains.default_rag_config.repositories import DefaultRagConfigRepository
from src.domains.default_rag_config.service import DefaultRagConfigService
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.sql_database import SqlDatabase


@pytest.mark.integration
class TestDefaultRagConfigServiceIntegration:
    """Integration tests for the DefaultRagConfigService component."""

    @pytest.fixture(scope="function")
    def default_rag_config_repository(self, db_session: SqlDatabase) -> DefaultRagConfigRepository:
        """Fixture to create a DefaultRagConfigRepository."""
        return DefaultRagConfigRepository(db_session)

    @pytest.fixture(scope="function")
    def default_rag_config_data_access(
        self, default_rag_config_repository: DefaultRagConfigRepository, cache_instance: RedisCache
    ) -> DefaultRagConfigDataAccess:
        """Fixture to create a DefaultRagConfigDataAccess."""
        return DefaultRagConfigDataAccess(repository=default_rag_config_repository, cache=cache_instance)

    @pytest.fixture(scope="function")
    def default_rag_config_service(
        self, default_rag_config_data_access: DefaultRagConfigDataAccess
    ) -> DefaultRagConfigService:
        """Fixture to create a DefaultRagConfigService."""
        return DefaultRagConfigService(data_access=default_rag_config_data_access)

    def test_get_config_returns_none_when_not_set(
        self, default_rag_config_service: DefaultRagConfigService
    ):
        """Test that get_config returns None if no default config is in the database."""
        # Arrange
        # Ensure the table is clean for this test
        default_rag_config_service.data_access.repository.db.execute(
            "TRUNCATE default_rag_configs RESTART IDENTITY CASCADE;"
        )
        default_rag_config_service.data_access._invalidate_cache()

        # Act
        config = default_rag_config_service.get_config()

        # Assert
        assert config is None

    def test_create_or_update_config_initial_vector(
        self, default_rag_config_service: DefaultRagConfigService
    ):
        """Test initial creation of a vector RAG config."""
        # Arrange
        default_rag_config_service.data_access.repository.db.execute(
            "TRUNCATE default_rag_configs RESTART IDENTITY CASCADE;"
        )
        default_rag_config_service.data_access._invalidate_cache()

        # Act
        config = default_rag_config_service.create_or_update_config(
            rag_type="vector",
            vector_config={"embedding_algorithm": "test-embedder", "chunk_size": 100},
        )

        # Assert
        assert config is not None
        assert config.id == 1
        assert config.rag_type == "vector"
        assert config.vector_config.embedding_algorithm == "test-embedder"
        assert config.vector_config.chunk_size == 100
        assert config.graph_config.entity_extraction_algorithm == "spacy"  # Default graph config

    def test_create_or_update_config_initial_graph(
        self, default_rag_config_service: DefaultRagConfigService
    ):
        """Test initial creation of a graph RAG config."""
        # Arrange
        default_rag_config_service.data_access.repository.db.execute(
            "TRUNCATE default_rag_configs RESTART IDENTITY CASCADE;"
        )
        default_rag_config_service.data_access._invalidate_cache()

        # Act
        config = default_rag_config_service.create_or_update_config(
            rag_type="graph",
            graph_config={"entity_extraction_algorithm": "test-entity-extractor"},
        )

        # Assert
        assert config is not None
        assert config.id == 1
        assert config.rag_type == "graph"
        assert config.graph_config.entity_extraction_algorithm == "test-entity-extractor"
        assert config.vector_config.embedding_algorithm == "ollama"  # Default vector config

    def test_create_or_update_config_update_vector(
        self, default_rag_config_service: DefaultRagConfigService
    ):
        """Test updating an existing vector RAG config."""
        # Arrange - create initial config
        default_rag_config_service.create_or_update_config(
            rag_type="vector",
            vector_config={"embedding_algorithm": "initial-embedder", "chunk_size": 50},
        )

        # Act - update some fields
        config = default_rag_config_service.create_or_update_config(
            rag_type="vector",
            vector_config={"chunk_size": 200, "rerank_algorithm": "test-reranker"},
        )

        # Assert
        assert config is not None
        assert config.rag_type == "vector"
        assert config.vector_config.embedding_algorithm == "initial-embedder"  # Should be preserved
        assert config.vector_config.chunk_size == 200
        assert config.vector_config.rerank_algorithm == "test-reranker"

    def test_create_or_update_config_update_graph(
        self, default_rag_config_service: DefaultRagConfigService
    ):
        """Test updating an existing graph RAG config."""
        # Arrange - create initial config
        default_rag_config_service.create_or_update_config(
            rag_type="graph",
            graph_config={"entity_extraction_algorithm": "initial-extractor", "max_traversal_depth": 1},
        )

        # Act - update some fields
        config = default_rag_config_service.create_or_update_config(
            rag_type="graph",
            graph_config={"max_traversal_depth": 3, "clustering_algorithm": "test-clusterer"},
        )

        # Assert
        assert config is not None
        assert config.rag_type == "graph"
        assert config.graph_config.entity_extraction_algorithm == "initial-extractor"  # Should be preserved
        assert config.graph_config.max_traversal_depth == 3
        assert config.graph_config.clustering_algorithm == "test-clusterer"

    def test_create_or_update_config_switch_rag_type(
        self, default_rag_config_service: DefaultRagConfigService
    ):
        """Test updating existing config to switch RAG type."""
        # Arrange - start with vector config
        initial_config = default_rag_config_service.create_or_update_config(
            rag_type="vector",
            vector_config={"embedding_algorithm": "original-embedder"},
        )
        assert initial_config.rag_type == "vector"

        # Act - switch to graph config, providing graph-specific updates
        updated_config = default_rag_config_service.create_or_update_config(
            rag_type="graph",
            graph_config={"entity_extraction_algorithm": "new-extractor"},
        )

        # Assert
        assert updated_config is not None
        assert updated_config.rag_type == "graph"
        assert updated_config.graph_config.entity_extraction_algorithm == "new-extractor"
        # Old vector config details should still be present but not active
        assert updated_config.vector_config.embedding_algorithm == "original-embedder"
