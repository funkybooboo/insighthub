"""Unit tests for RAG config repository."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from shared.models.workspace import RagConfig
from shared.repositories import SqlRagConfigRepository


class TestSqlRagConfigRepository:
    """Test SqlRagConfigRepository."""

    @pytest.fixture
    def mock_db(self):
        """Mock database connection."""
        return MagicMock()

    @pytest.fixture
    def mock_connection(self):
        """Mock database connection."""
        return MagicMock()

    @pytest.fixture
    def mock_cursor(self):
        """Mock database cursor."""
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_db):
        """Create repository instance."""
        return SqlRagConfigRepository(mock_db)

    def test_get_by_workspace_id_found(self, repository, mock_db, mock_connection, mock_cursor):
        """Test getting RAG config when it exists."""
        # Setup
        workspace_id = 123
        expected_config = RagConfig(
            id=1,
            workspace_id=workspace_id,
            embedding_model="nomic-embed-text",
            embedding_dim=768,
            retriever_type="vector",
            chunk_size=1000,
            chunk_overlap=200,
            top_k=8,
            rerank_enabled=False,
            rerank_model=None,
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        mock_db.get_connection.return_value.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (
            1, workspace_id, "nomic-embed-text", 768, "vector",
            1000, 200, 8, False, None,
            datetime(2025, 1, 1, 12, 0, 0), datetime(2025, 1, 1, 12, 0, 0)
        )

        # Execute
        result = repository.get_by_workspace_id(workspace_id)

        # Assert
        assert result is not None
        assert result.id == expected_config.id
        assert result.workspace_id == expected_config.workspace_id
        assert result.embedding_model == expected_config.embedding_model
        assert result.chunk_size == expected_config.chunk_size

        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        assert "SELECT" in args[0]
        assert workspace_id in args[1]

    def test_get_by_workspace_id_not_found(self, repository, mock_db, mock_connection, mock_cursor):
        """Test getting RAG config when it doesn't exist."""
        # Setup
        workspace_id = 123
        mock_db.get_connection.return_value.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        # Execute
        result = repository.get_by_workspace_id(workspace_id)

        # Assert
        assert result is None
        mock_cursor.execute.assert_called_once()

    def test_create_success(self, repository, mock_db, mock_connection, mock_cursor):
        """Test creating RAG config successfully."""
        # Setup
        workspace_id = 123
        config_data = {
            "embedding_model": "custom-model",
            "chunk_size": 1500,
            "top_k": 10
        }

        mock_db.get_connection.return_value.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (
            1, workspace_id, "custom-model", None, "vector",
            1500, 200, 10, False, None,
            datetime(2025, 1, 1, 12, 0, 0), datetime(2025, 1, 1, 12, 0, 0)
        )

        # Execute
        result = repository.create(workspace_id, **config_data)

        # Assert
        assert result is not None
        assert result.workspace_id == workspace_id
        assert result.embedding_model == "custom-model"
        assert result.chunk_size == 1500
        assert result.top_k == 10

        mock_connection.commit.assert_called_once()
        mock_cursor.execute.assert_called_once()

    def test_create_failure(self, repository, mock_db, mock_connection, mock_cursor):
        """Test creating RAG config when database returns no row."""
        # Setup
        workspace_id = 123
        mock_db.get_connection.return_value.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        # Execute & Assert
        with pytest.raises(RuntimeError, match="Failed to create RAG config"):
            repository.create(workspace_id)

    def test_update_with_data(self, repository, mock_db, mock_connection, mock_cursor):
        """Test updating RAG config with data."""
        # Setup
        workspace_id = 123
        update_data = {"chunk_size": 1200, "top_k": 12}

        mock_db.get_connection.return_value.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (
            1, workspace_id, "nomic-embed-text", None, "vector",
            1200, 200, 12, False, None,
            datetime(2025, 1, 1, 12, 0, 0), datetime(2025, 1, 1, 12, 0, 0)
        )

        # Execute
        result = repository.update(workspace_id, **update_data)

        # Assert
        assert result is not None
        assert result.chunk_size == 1200
        assert result.top_k == 12

        mock_connection.commit.assert_called_once()

    def test_update_no_data(self, repository, mock_db, mock_connection, mock_cursor):
        """Test updating RAG config with no data returns current config."""
        # Setup
        workspace_id = 123
        current_config = RagConfig(
            id=1, workspace_id=workspace_id, embedding_model="nomic-embed-text",
            embedding_dim=None, retriever_type="vector", chunk_size=1000,
            chunk_overlap=200, top_k=8, rerank_enabled=False, rerank_model=None,
            created_at=datetime(2025, 1, 1, 12, 0, 0), updated_at=datetime(2025, 1, 1, 12, 0, 0)
        )

        # Mock get_by_workspace_id to return current config
        with patch.object(repository, 'get_by_workspace_id', return_value=current_config):
            # Execute
            result = repository.update(workspace_id)

            # Assert
            assert result == current_config
            # Should not have executed any database updates
            mock_connection.commit.assert_not_called()

    def test_update_not_found(self, repository, mock_db, mock_connection, mock_cursor):
        """Test updating RAG config when it doesn't exist."""
        # Setup
        workspace_id = 123
        mock_db.get_connection.return_value.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        # Execute
        result = repository.update(workspace_id, chunk_size=1200)

        # Assert
        assert result is None
        mock_connection.commit.assert_not_called()

    def test_delete_success(self, repository, mock_db, mock_connection, mock_cursor):
        """Test deleting RAG config successfully."""
        # Setup
        workspace_id = 123
        mock_db.get_connection.return_value.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        # Execute
        result = repository.delete(workspace_id)

        # Assert
        assert result is True
        mock_connection.commit.assert_called_once()

    def test_delete_not_found(self, repository, mock_db, mock_connection, mock_cursor):
        """Test deleting RAG config when it doesn't exist."""
        # Setup
        workspace_id = 123
        mock_db.get_connection.return_value.__enter__.return_value = mock_connection
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        # Execute
        result = repository.delete(workspace_id)

        # Assert
        assert result is False
        mock_connection.commit.assert_not_called()