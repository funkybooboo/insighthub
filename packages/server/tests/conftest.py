"""Shared test fixtures and configuration."""

from unittest.mock import Mock

import pytest
from flask import Flask
from flask.testing import FlaskClient


@pytest.fixture
def app():
    """Create a minimal test app for basic testing."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"

    # Add a simple test route
    @app.route("/test")
    def test_route():
        return {"status": "ok"}

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_token() -> str:
    """Mock authentication token for testing."""
    return "mock-jwt-token"


@pytest.fixture
def test_user():
    """Mock test user for testing."""
    return {"id": 1, "username": "testuser", "email": "test@example.com", "full_name": "Test User"}


@pytest.fixture
def test_workspace():
    """Mock test workspace for testing."""
    return {
        "id": 1,
        "name": "Test Workspace",
        "description": "Workspace for testing",
        "owner_id": 1,
        "rag_config": {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
        },
    }


@pytest.fixture
def mock_service():
    """Mock service for testing."""
    return Mock()


@pytest.fixture
def mock_workspace_service():
    """Mock workspace service for testing."""
    return Mock()


@pytest.fixture
def mock_app_context():
    """Mock app context for testing."""
    return Mock()


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return Mock(id=1, username="testuser", email="test@example.com", full_name="Test User")


@pytest.fixture
def auth_headers(auth_token: str):
    """Authentication headers for testing."""
    return {"Authorization": f"Bearer {auth_token}"}
