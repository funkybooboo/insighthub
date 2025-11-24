"""Unit tests for DefaultRagConfigRepository."""

import pytest
from datetime import datetime
from unittest.mock import Mock

from shared.models.default_rag_config import DefaultRagConfig
from shared.repositories.default_rag_config import SqlDefaultRagConfigRepository


class TestSqlDefaultRagConfigRepository:
    """Tests for SQL Default RAG Config Repository."""

    @pytest.fixture
    def mock_db(self):
        """Mock database."""
        return Mock()

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository with mock database."""
        return SqlDefaultRagConfigRepository(mock_db)

    @pytest.fixture
    def sample_config(self):
        """Create a sample DefaultRagConfig."""
        return DefaultRagConfig(
            id=1,
            user_id=1,
            embedding_model="nomic-embed-text",
            embedding_dim=768,
            retriever_type="vector",
            chunk_size=1000,
            chunk_overlap=200,
            top_k=8,
            rerank_enabled=False,
            rerank_model=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def test_get_by_user_id_success(self, repository, mock_db, sample_config):
        """Test successful get by user ID."""
        mock_db.fetchone.return_value = {
            "id": 1,
            "user_id": 1,
            "embedding_model": "nomic-embed-text",
            "embedding_dim": 768,
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
            "rerank_enabled": False,
            "rerank_model": None,
            "created_at": sample_config.created_at,
            "updated_at": sample_config.updated_at,
        }

        result = repository.get_by_user_id(1)

        assert result is not None
        assert result.id == 1
        assert result.user_id == 1
        assert result.embedding_model == "nomic-embed-text"
        assert result.embedding_dim == 768
        assert result.retriever_type == "vector"
        assert result.chunk_size == 1000
        assert result.chunk_overlap == 200
        assert result.top_k == 8
        assert result.rerank_enabled is False
        assert result.rerank_model is None

        mock_db.fetchone.assert_called_once_with(
            """
            SELECT id, user_id, embedding_model, embedding_dim, retriever_type,
                   chunk_size, chunk_overlap, top_k, rerank_enabled, rerank_model,
                   created_at, updated_at
            FROM default_rag_configs
            WHERE user_id = %s
        """,
            {"user_id": 1}
        )

    def test_get_by_user_id_not_found(self, repository, mock_db):
        """Test get by user ID when not found."""
        mock_db.fetchone.return_value = None

        result = repository.get_by_user_id(999)

        assert result is None
        mock_db.fetchone.assert_called_once()

    def test_upsert_update_existing(self, repository, mock_db, sample_config):
        """Test upsert when updating existing config."""
        mock_db.fetchone.return_value = {
            "id": 1,
            "user_id": 1,
            "embedding_model": "updated-model",
            "embedding_dim": 512,
            "retriever_type": "vector",
            "chunk_size": 1500,
            "chunk_overlap": 300,
            "top_k": 10,
            "rerank_enabled": True,
            "rerank_model": "rerank-model",
            "created_at": sample_config.created_at,
            "updated_at": sample_config.updated_at,
        }

        result = repository.upsert(
            user_id=1,
            embedding_model="updated-model",
            embedding_dim=512,
            chunk_size=1500,
            chunk_overlap=300,
            top_k=10,
            rerank_enabled=True,
            rerank_model="rerank-model",
        )

        assert result is not None
        assert result.id == 1
        assert result.user_id == 1
        assert result.embedding_model == "updated-model"
        assert result.embedding_dim == 512
        assert result.chunk_size == 1500
        assert result.chunk_overlap == 300
        assert result.top_k == 10
        assert result.rerank_enabled is True
        assert result.rerank_model == "rerank-model"

        # Should call fetchone for update attempt
        assert mock_db.fetchone.call_count == 1

    def test_upsert_create_new(self, repository, mock_db, sample_config):
        """Test upsert when creating new config."""
        # First call returns None (no existing record)
        # Second call returns the created record
        mock_db.fetchone.side_effect = [
            None,  # Update attempt returns None
            {
                "id": 2,
                "user_id": 1,
                "embedding_model": "new-model",
                "embedding_dim": 384,
                "retriever_type": "graph",
                "chunk_size": 800,
                "chunk_overlap": 100,
                "top_k": 5,
                "rerank_enabled": False,
                "rerank_model": None,
                "created_at": sample_config.created_at,
                "updated_at": sample_config.updated_at,
            }
        ]

        result = repository.upsert(
            user_id=1,
            embedding_model="new-model",
            embedding_dim=384,
            retriever_type="graph",
            chunk_size=800,
            chunk_overlap=100,
            top_k=5,
        )

        assert result is not None
        assert result.id == 2
        assert result.user_id == 1
        assert result.embedding_model == "new-model"
        assert result.embedding_dim == 384
        assert result.retriever_type == "graph"
        assert result.chunk_size == 800
        assert result.chunk_overlap == 100
        assert result.top_k == 5
        assert result.rerank_enabled is False
        assert result.rerank_model is None

        # Should call fetchone twice: once for update attempt, once for insert result
        assert mock_db.fetchone.call_count == 2

    def test_upsert_with_defaults(self, repository, mock_db, sample_config):
        """Test upsert with default values."""
        mock_db.fetchone.return_value = {
            "id": 1,
            "user_id": 1,
            "embedding_model": "nomic-embed-text",  # Default
            "embedding_dim": None,  # Default
            "retriever_type": "vector",  # Default
            "chunk_size": 1000,  # Default
            "chunk_overlap": 200,  # Default
            "top_k": 8,  # Default
            "rerank_enabled": False,  # Default
            "rerank_model": None,  # Default
            "created_at": sample_config.created_at,
            "updated_at": sample_config.updated_at,
        }

        result = repository.upsert(user_id=1)  # No parameters provided

        assert result is not None
        assert result.embedding_model == "nomic-embed-text"
        assert result.embedding_dim is None
        assert result.retriever_type == "vector"
        assert result.chunk_size == 1000
        assert result.chunk_overlap == 200
        assert result.top_k == 8
        assert result.rerank_enabled is False
        assert result.rerank_model is None

    def test_delete_by_user_id_success(self, repository, mock_db):
        """Test successful delete by user ID."""
        mock_db.execute.return_value = 1  # Rows affected

        result = repository.delete_by_user_id(1)

        assert result is True
        mock_db.execute.assert_called_once_with(
            "DELETE FROM default_rag_configs WHERE user_id = %s",
            {"user_id": 1}
        )

    def test_delete_by_user_id_no_rows(self, repository, mock_db):
        """Test delete by user ID when no rows affected."""
        mock_db.execute.return_value = 0  # No rows affected

        result = repository.delete_by_user_id(999)

        assert result is True  # Method always returns True
        mock_db.execute.assert_called_once()


class TestDefaultRagConfigRepositoryInterface:
    """Tests for the repository interface contract."""

    def test_repository_interface_methods(self):
        """Test that the repository implements all required methods."""
        from shared.repositories.default_rag_config import DefaultRagConfigRepository

        # Check that all abstract methods are defined
        required_methods = [
            "get_by_user_id",
            "upsert",
            "delete_by_user_id",
        ]

        for method_name in required_methods:
            assert hasattr(DefaultRagConfigRepository, method_name), f"Missing method: {method_name}"

            # Check that methods are abstract
            method = getattr(DefaultRagConfigRepository, method_name)
            assert hasattr(method, '__isabstractmethod__'), f"Method {method_name} should be abstract"