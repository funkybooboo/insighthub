"""Unit tests for RAG config service."""

from unittest.mock import MagicMock

import pytest
from shared.models.workspace import RagConfig

from src.domains.workspaces.rag_config.service import RagConfigService


class TestRagConfigService:
    """Test RagConfigService."""

    @pytest.fixture
    def mock_repository(self):
        """Mock repository."""
        return MagicMock()

    @pytest.fixture
    def mock_workspace_service(self):
        """Mock workspace service."""
        return MagicMock()

    @pytest.fixture
    def service(self, mock_repository, mock_workspace_service):
        """Create service instance."""
        return RagConfigService(mock_repository, mock_workspace_service)

    def test_get_rag_config_success(self, service, mock_repository, mock_workspace_service):
        """Test getting RAG config successfully."""
        # Setup
        workspace_id = 123
        user_id = 456
        expected_config = RagConfig(
            id=1,
            workspace_id=workspace_id,
            embedding_model="nomic-embed-text",
            embedding_dim=None,
            retriever_type="vector",
            chunk_size=1000,
            chunk_overlap=200,
            top_k=8,
            rerank_enabled=False,
            rerank_model=None,
            created_at=None,
            updated_at=None,
        )

        mock_workspace_service.validate_workspace_access.return_value = True
        mock_repository.get_by_workspace_id.return_value = expected_config

        # Execute
        result = service.get_rag_config(workspace_id, user_id)

        # Assert
        assert result == expected_config
        mock_workspace_service.validate_workspace_access.assert_called_once_with(
            workspace_id, user_id
        )
        mock_repository.get_by_workspace_id.assert_called_once_with(workspace_id)

    def test_get_rag_config_no_access(self, service, mock_workspace_service):
        """Test getting RAG config when user has no access."""
        # Setup
        workspace_id = 123
        user_id = 456
        mock_workspace_service.validate_workspace_access.return_value = False

        # Execute
        result = service.get_rag_config(workspace_id, user_id)

        # Assert
        assert result is None
        mock_workspace_service.validate_workspace_access.assert_called_once_with(
            workspace_id, user_id
        )

    def test_create_rag_config_success(self, service, mock_repository, mock_workspace_service):
        """Test creating RAG config successfully."""
        # Setup
        workspace_id = 123
        user_id = 456
        config_data = {"embedding_model": "custom-model", "chunk_size": 1500}
        expected_config = RagConfig(
            id=1,
            workspace_id=workspace_id,
            embedding_model="custom-model",
            embedding_dim=None,
            retriever_type="vector",
            chunk_size=1500,
            chunk_overlap=200,
            top_k=8,
            rerank_enabled=False,
            rerank_model=None,
            created_at=None,
            updated_at=None,
        )

        mock_workspace_service.validate_workspace_access.return_value = True
        mock_repository.get_by_workspace_id.return_value = None  # Doesn't exist yet
        mock_repository.create.return_value = expected_config

        # Execute
        result = service.create_rag_config(workspace_id, user_id, **config_data)

        # Assert
        assert result == expected_config
        mock_workspace_service.validate_workspace_access.assert_called_once_with(
            workspace_id, user_id
        )
        mock_repository.get_by_workspace_id.assert_called_once_with(workspace_id)
        mock_repository.create.assert_called_once_with(workspace_id, **config_data)

    def test_create_rag_config_already_exists(
        self, service, mock_repository, mock_workspace_service
    ):
        """Test creating RAG config when it already exists."""
        # Setup
        workspace_id = 123
        user_id = 456
        existing_config = RagConfig(
            id=1,
            workspace_id=workspace_id,
            embedding_model="existing-model",
            embedding_dim=None,
            retriever_type="vector",
            chunk_size=1000,
            chunk_overlap=200,
            top_k=8,
            rerank_enabled=False,
            rerank_model=None,
            created_at=None,
            updated_at=None,
        )

        mock_workspace_service.validate_workspace_access.return_value = True
        mock_repository.get_by_workspace_id.return_value = existing_config

        # Execute & Assert
        with pytest.raises(ValueError, match="already exists"):
            service.create_rag_config(workspace_id, user_id)

    def test_create_rag_config_no_access(self, service, mock_workspace_service):
        """Test creating RAG config when user has no access."""
        # Setup
        workspace_id = 123
        user_id = 456
        mock_workspace_service.validate_workspace_access.return_value = False

        # Execute & Assert
        with pytest.raises(ValueError):
            service.create_rag_config(workspace_id, user_id)

    def test_update_rag_config_success(self, service, mock_repository, mock_workspace_service):
        """Test updating RAG config successfully."""
        # Setup
        workspace_id = 123
        user_id = 456
        update_data = {"chunk_size": 1200, "top_k": 10}
        updated_config = RagConfig(
            id=1,
            workspace_id=workspace_id,
            embedding_model="nomic-embed-text",
            embedding_dim=None,
            retriever_type="vector",
            chunk_size=1200,
            chunk_overlap=200,
            top_k=10,
            rerank_enabled=False,
            rerank_model=None,
            created_at=None,
            updated_at=None,
        )

        mock_workspace_service.validate_workspace_access.return_value = True
        mock_repository.update.return_value = updated_config

        # Execute
        result = service.update_rag_config(workspace_id, user_id, **update_data)

        # Assert
        assert result == updated_config
        mock_workspace_service.validate_workspace_access.assert_called_once_with(
            workspace_id, user_id
        )
        mock_repository.update.assert_called_once_with(workspace_id, **update_data)

    def test_update_rag_config_validation_error(self, service, mock_workspace_service):
        """Test updating RAG config with invalid data."""
        # Setup
        workspace_id = 123
        user_id = 456
        invalid_data = {"retriever_type": "invalid_type"}

        mock_workspace_service.validate_workspace_access.return_value = True

        # Execute & Assert
        with pytest.raises(ValueError, match="retriever_type must be one of"):
            service.update_rag_config(workspace_id, user_id, **invalid_data)

    def test_update_rag_config_chunk_size_too_small(self, service, mock_workspace_service):
        """Test updating RAG config with chunk_size too small."""
        # Setup
        workspace_id = 123
        user_id = 456
        invalid_data = {"chunk_size": 50}

        mock_workspace_service.validate_workspace_access.return_value = True

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_size must be between 100 and 5000"):
            service.update_rag_config(workspace_id, user_id, **invalid_data)

    def test_update_rag_config_chunk_size_too_large(self, service, mock_workspace_service):
        """Test updating RAG config with chunk_size too large."""
        # Setup
        workspace_id = 123
        user_id = 456
        invalid_data = {"chunk_size": 6000}

        mock_workspace_service.validate_workspace_access.return_value = True

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_size must be between 100 and 5000"):
            service.update_rag_config(workspace_id, user_id, **invalid_data)

    def test_update_rag_config_chunk_overlap_negative(self, service, mock_workspace_service):
        """Test updating RAG config with negative chunk_overlap."""
        # Setup
        workspace_id = 123
        user_id = 456
        invalid_data = {"chunk_overlap": -10}

        mock_workspace_service.validate_workspace_access.return_value = True

        # Execute & Assert
        with pytest.raises(ValueError, match="chunk_overlap must be between 0 and 1000"):
            service.update_rag_config(workspace_id, user_id, **invalid_data)

    def test_update_rag_config_top_k_too_small(self, service, mock_workspace_service):
        """Test updating RAG config with top_k too small."""
        # Setup
        workspace_id = 123
        user_id = 456
        invalid_data = {"top_k": 0}

        mock_workspace_service.validate_workspace_access.return_value = True

        # Execute & Assert
        with pytest.raises(ValueError, match="top_k must be between 1 and 50"):
            service.update_rag_config(workspace_id, user_id, **invalid_data)

    def test_update_rag_config_top_k_too_large(self, service, mock_workspace_service):
        """Test updating RAG config with top_k too large."""
        # Setup
        workspace_id = 123
        user_id = 456
        invalid_data = {"top_k": 100}

        mock_workspace_service.validate_workspace_access.return_value = True

        # Execute & Assert
        with pytest.raises(ValueError, match="top_k must be between 1 and 50"):
            service.update_rag_config(workspace_id, user_id, **invalid_data)

    def test_update_rag_config_no_access(self, service, mock_workspace_service):
        """Test updating RAG config when user has no access."""
        # Setup
        workspace_id = 123
        user_id = 456
        mock_workspace_service.validate_workspace_access.return_value = False

        # Execute
        result = service.update_rag_config(workspace_id, user_id, chunk_size=1200)

        # Assert
        assert result is None
        mock_workspace_service.validate_workspace_access.assert_called_once_with(
            workspace_id, user_id
        )

    def test_delete_rag_config_success(self, service, mock_repository, mock_workspace_service):
        """Test deleting RAG config successfully."""
        # Setup
        workspace_id = 123
        user_id = 456

        mock_workspace_service.validate_workspace_access.return_value = True
        mock_repository.delete.return_value = True

        # Execute
        result = service.delete_rag_config(workspace_id, user_id)

        # Assert
        assert result is True
        mock_workspace_service.validate_workspace_access.assert_called_once_with(
            workspace_id, user_id
        )
        mock_repository.delete.assert_called_once_with(workspace_id)

    def test_delete_rag_config_no_access(self, service, mock_workspace_service):
        """Test deleting RAG config when user has no access."""
        # Setup
        workspace_id = 123
        user_id = 456
        mock_workspace_service.validate_workspace_access.return_value = False

        # Execute
        result = service.delete_rag_config(workspace_id, user_id)

        # Assert
        assert result is False
        mock_workspace_service.validate_workspace_access.assert_called_once_with(
            workspace_id, user_id
        )
