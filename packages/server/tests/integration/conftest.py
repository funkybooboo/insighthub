import json
import os
from collections.abc import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from shared.database.sql import PostgresSqlDatabase
from shared.repositories import (
    SqlChatMessageRepository,
    SqlChatSessionRepository,
    SqlDocumentRepository,
    SqlUserRepository,
)

try:
    from testcontainers.postgres import PostgresContainer

    POSTGRES_AVAILABLE = True
except Exception:
    POSTGRES_AVAILABLE = False


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    """Provide a PostgreSQL test container for integration tests."""
    if not POSTGRES_AVAILABLE:
        pytest.skip("testcontainers PostgreSQL not available; skipping integration tests")
    # Use PostgreSQL with pgvector extension pre-installed
    with PostgresContainer("ankane/pgvector:latest") as container:
        url = container.get_connection_url().replace("postgresql+psycopg2://", "postgresql://")
        os.environ["DATABASE_URL"] = url
        yield url
        del os.environ["DATABASE_URL"]


@pytest.fixture(scope="function")
def app(postgres_url: str) -> Generator[Flask, None, None]:
    """Create a Flask app with test configuration using real database."""
    import importlib

    import psycopg2

    import src.config

    # Set testing environment BEFORE importing app
    os.environ["TESTING"] = "true"
    os.environ["FLASK_DEBUG"] = "false"
    os.environ["RATE_LIMIT_ENABLED"] = "false"
    os.environ["DATABASE_URL"] = postgres_url
    os.environ["RABBITMQ_URL"] = ""  # Disable RabbitMQ for tests

    # Reload config module to pick up new environment variables
    importlib.reload(src.config)

    from src.api import create_app
    from src.infrastructure.database import init_db

    # Initialize database with migrations
    init_db(postgres_url)

    # Create the app
    test_app = create_app()
    test_app.config["TESTING"] = True

    yield test_app

    # Clean up database after test
    conn = psycopg2.connect(postgres_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public;
                """
            )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    """Provide a test client for the Flask app."""
    return app.test_client()


@pytest.fixture(scope="function")
def auth_token(client: FlaskClient) -> str:
    """Create a test users and return a valid JWT token."""
    # Create a test users
    signup_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPass123!",
        "full_name": "Test User",
    }

    signup_response = client.post(
        "/api/auth/signup", data=json.dumps(signup_data), content_type="application/json"
    )
    assert signup_response.status_code == 201

    # Login to get token
    login_data = {"username": "testuser", "password": "TestPass123!"}
    login_response = client.post(
        "/api/auth/login", data=json.dumps(login_data), content_type="application/json"
    )
    assert login_response.status_code == 200
    login_result = json.loads(login_response.data)

    return str(login_result["access_token"])


@pytest.fixture(scope="function")
def test_workspace(client: FlaskClient, auth_token: str) -> dict[str, str]:
    """Create a test workspace for the authenticated users."""
    workspace_data = {
        "name": "Test Workspace",
        "description": "Workspace for integration testing",
    }

    response = client.post(
        "/api/workspaces",
        data=json.dumps(workspace_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 201
    workspace = json.loads(response.data)

    return dict(workspace)


@pytest.fixture(scope="function")
def db(postgres_url: str) -> Generator[PostgresSqlDatabase, None, None]:
    """Create a database connection for integration tests."""
    from shared.database.sql import PostgresSqlDatabase

    from src.infrastructure.database import init_db

    # Initialize database with migrations
    init_db(postgres_url)

    database = PostgresSqlDatabase(postgres_url)
    try:
        yield database
    finally:
        database.close()


@pytest.fixture(scope="function")
def user_repository(db: PostgresSqlDatabase) -> SqlUserRepository:
    """Create a users repository for integration tests."""
    from shared.repositories import SqlUserRepository

    return SqlUserRepository(db)


@pytest.fixture(scope="function")
def document_repository(db: PostgresSqlDatabase) -> SqlDocumentRepository:
    """Create a document repository for integration tests."""
    from shared.repositories import SqlDocumentRepository

    return SqlDocumentRepository(db)


@pytest.fixture(scope="function")
def chat_session_repository(db: PostgresSqlDatabase) -> SqlChatSessionRepository:
    """Create a chats session repository for integration tests."""
    from shared.repositories import SqlChatSessionRepository

    return SqlChatSessionRepository(db)


@pytest.fixture(scope="function")
def chat_message_repository(db: PostgresSqlDatabase) -> SqlChatMessageRepository:
    """Create a chats message repository for integration tests."""
    from shared.repositories import SqlChatMessageRepository

    return SqlChatMessageRepository(db)
