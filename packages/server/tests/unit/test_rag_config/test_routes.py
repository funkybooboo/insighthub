"""Unit tests for RAG config routes."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from shared.models.workspace import RagConfig


class TestRagConfigRoutes:
    """Test RAG config API routes."""

    @pytest.fixture
    def mock_service(self):
        """Mock RAG config service."""
        return MagicMock()

    @pytest.fixture
    def mock_workspace_service(self):
        """Mock workspace service."""
        return MagicMock()

    @pytest.fixture
    def app_context(self, mock_service, mock_workspace_service):
        """Mock app context."""
        context = MagicMock()
        context.rag_config_service = mock_service
        context.workspace_service = mock_workspace_service
        return context

    @pytest.fixture
    def client(self, app, app_context):
        """Test client with mocked context."""
        with app.test_client() as client, app.app_context():
            # Mock the g.app_context
            import flask

            flask.g.app_context = app_context
            yield client

    def test_get_rag_config_success(self, client, mock_service, mock_workspace_service):
        """Test GET /api/workspaces/{id}/rag-config successful."""
        # Setup
        workspace_id = "123"
        config = RagConfig(
            id=1,
            workspace_id=123,
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

        mock_service.get_rag_config.return_value = config

        # Mock authentication
        with patch("src.infrastructure.auth.get_current_user") as mock_user:
            mock_user.return_value = MagicMock(id=456)

            # Execute
            response = client.get(f"/api/workspaces/{workspace_id}/rag-config")

            # Assert
            assert response.status_code == 200
            data = response.get_json()
            assert data["id"] == 1
            assert data["workspace_id"] == 123
            assert data["embedding_model"] == "nomic-embed-text"
            assert data["chunk_size"] == 1000
            assert "created_at" in data
            assert "updated_at" in data

            mock_service.get_rag_config.assert_called_once_with(123, 456)

    def test_get_rag_config_not_found(self, client, mock_service):
        """Test GET /api/workspaces/{id}/rag-config when config doesn't exist."""
        # Setup
        workspace_id = "123"
        mock_service.get_rag_config.return_value = None

        # Mock authentication
        with patch("src.infrastructure.auth.get_current_user") as mock_user:
            mock_user.return_value = MagicMock(id=456)

            # Execute
            response = client.get(f"/api/workspaces/{workspace_id}/rag-config")

            # Assert
            assert response.status_code == 404
            data = response.get_json()
            assert "error" in data
            assert "not found" in data["error"].lower()

    def test_get_rag_config_invalid_workspace_id(self, client):
        """Test GET /api/workspaces/{id}/rag-config with invalid workspace ID."""
        # Mock authentication
        with patch("src.infrastructure.auth.get_current_user") as mock_user:
            mock_user.return_value = MagicMock(id=456)

            # Execute
            response = client.get("/api/workspaces/invalid/rag-config")

            # Assert
            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data
            assert "Invalid workspace ID" in data["error"]

    def test_create_rag_config_success(self, client, mock_service, mock_workspace_service):
        """Test POST /api/workspaces/{id}/rag-config successful."""
        # Setup
        workspace_id = "123"
        request_data = {"embedding_model": "custom-model", "chunk_size": 1500, "top_k": 10}
        created_config = RagConfig(
            id=1,
            workspace_id=123,
            embedding_model="custom-model",
            embedding_dim=None,
            retriever_type="vector",
            chunk_size=1500,
            chunk_overlap=200,
            top_k=10,
            rerank_enabled=False,
            rerank_model=None,
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        mock_service.create_rag_config.return_value = created_config

        # Mock authentication
        with patch("src.infrastructure.auth.get_current_user") as mock_user:
            mock_user.return_value = MagicMock(id=456)

            # Execute
            response = client.post(f"/api/workspaces/{workspace_id}/rag-config", json=request_data)

            # Assert
            assert response.status_code == 201
            data = response.get_json()
            assert data["id"] == 1
            assert data["embedding_model"] == "custom-model"
            assert data["chunk_size"] == 1500
            assert data["top_k"] == 10

            mock_service.create_rag_config.assert_called_once_with(
                123, 456, embedding_model="custom-model", chunk_size=1500, top_k=10
            )

    def test_create_rag_config_missing_required_fields(self, client):
        """Test POST /api/workspaces/{id}/rag-config with missing required fields."""
        # Setup
        workspace_id = "123"
        request_data = {}  # Missing required fields

        # Mock authentication
        with patch("src.infrastructure.auth.get_current_user") as mock_user:
            mock_user.return_value = MagicMock(id=456)

            # Execute
            response = client.post(f"/api/workspaces/{workspace_id}/rag-config", json=request_data)

            # Assert
            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data
            assert "Missing required field" in data["error"]

    def test_create_rag_config_already_exists(self, client, mock_service):
        """Test POST /api/workspaces/{id}/rag-config when config already exists."""
        # Setup
        workspace_id = "123"
        request_data = {"embedding_model": "nomic-embed-text", "chunk_size": 1000}

        mock_service.create_rag_config.side_effect = ValueError(
            "RAG configuration already exists for this workspace"
        )

        # Mock authentication
        with patch("src.infrastructure.auth.get_current_user") as mock_user:
            mock_user.return_value = MagicMock(id=456)

            # Execute
            response = client.post(f"/api/workspaces/{workspace_id}/rag-config", json=request_data)

            # Assert
            assert response.status_code == 409
            data = response.get_json()
            assert "error" in data
            assert "already exists" in data["error"]

    def test_update_rag_config_success(self, client, mock_service, mock_workspace_service):
        """Test PATCH /api/workspaces/{id}/rag-config successful."""
        # Setup
        workspace_id = "123"
        request_data = {"chunk_size": 1200, "top_k": 12}
        updated_config = RagConfig(
            id=1,
            workspace_id=123,
            embedding_model="nomic-embed-text",
            embedding_dim=None,
            retriever_type="vector",
            chunk_size=1200,
            chunk_overlap=200,
            top_k=12,
            rerank_enabled=False,
            rerank_model=None,
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        mock_service.update_rag_config.return_value = updated_config

        # Mock authentication
        with patch("src.infrastructure.auth.get_current_user") as mock_user:
            mock_user.return_value = MagicMock(id=456)

            # Execute
            response = client.patch(f"/api/workspaces/{workspace_id}/rag-config", json=request_data)

            # Assert
            assert response.status_code == 200
            data = response.get_json()
            assert data["chunk_size"] == 1200
            assert data["top_k"] == 12

            mock_service.update_rag_config.assert_called_once_with(
                123, 456, chunk_size=1200, top_k=12
            )

    def test_update_rag_config_validation_error(self, client, mock_service):
        """Test PATCH /api/workspaces/{id}/rag-config with validation error."""
        # Setup
        workspace_id = "123"
        request_data = {"chunk_size": 50}  # Too small

        mock_service.update_rag_config.side_effect = ValueError(
            "chunk_size must be between 100 and 5000"
        )

        # Mock authentication
        with patch("src.infrastructure.auth.get_current_user") as mock_user:
            mock_user.return_value = MagicMock(id=456)

            # Execute
            response = client.patch(f"/api/workspaces/{workspace_id}/rag-config", json=request_data)

            # Assert
            assert response.status_code == 400
            data = response.get_json()
            assert "error" in data
            assert "chunk_size must be between" in data["error"]

    def test_update_rag_config_not_found(self, client, mock_service):
        """Test PATCH /api/workspaces/{id}/rag-config when config doesn't exist."""
        # Setup
        workspace_id = "123"
        request_data = {"chunk_size": 1200}

        mock_service.update_rag_config.return_value = None

        # Mock authentication
        with patch("src.infrastructure.auth.get_current_user") as mock_user:
            mock_user.return_value = MagicMock(id=456)

            # Execute
            response = client.patch(f"/api/workspaces/{workspace_id}/rag-config", json=request_data)

            # Assert
            assert response.status_code == 404
            data = response.get_json()
            assert "error" in data
            assert "not found" in data["error"]

    def test_unauthenticated_request(self, client):
        """Test that unauthenticated requests are rejected."""
        # Execute without authentication
        response = client.get("/api/workspaces/123/rag-config")

        # Assert
        assert response.status_code == 401
