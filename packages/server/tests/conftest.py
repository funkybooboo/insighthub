"""Shared test fixtures and configuration."""

import os
import pytest
import tempfile
from typing import Generator

from src import create_app
from src.infrastructure.database import init_db


@pytest.fixture(scope="session")
def test_db():
    """Create a temporary test database."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Override database URL for testing
    original_db_url = os.environ.get("DATABASE_URL")
    test_db_url = f"postgresql://test:test@localhost:5432/test_insighthub"

    os.environ["DATABASE_URL"] = test_db_url

    try:
        # Initialize test database
        init_db(test_db_url)

        yield test_db_url

    finally:
        # Restore original database URL
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url
        else:
            os.environ.pop("DATABASE_URL", None)

        # Clean up temporary file
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def app(test_db):
    """Create and configure a test app instance."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE_URL'] = test_db

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """Create a test user and return authentication token."""
    # Register a test user
    register_response = client.post('/api/auth/signup', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    assert register_response.status_code == 201

    register_data = register_response.get_json()
    token = register_data['access_token']

    return token


@pytest.fixture
def test_workspace(client, auth_token):
    """Create a test workspace and return its data."""
    workspace_data = {
        'name': 'Test Workspace',
        'description': 'Workspace for testing',
        'rag_config': {
            'embedding_model': 'nomic-embed-text',
            'retriever_type': 'vector',
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'top_k': 8
        }
    }

    response = client.post(
        '/api/workspaces',
        json=workspace_data,
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 201

    return response.get_json()