"""Integration tests for API endpoints."""

import json
import os
from collections.abc import Generator
from io import BytesIO
from typing import Any

import pytest
from flask import Flask
from flask.testing import FlaskClient
from shared.storage import BlobStorage
from shared.storage.s3_blob_storage import S3BlobStorage
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer

from src.api import create_app


@pytest.fixture(scope="function")
def test_blob_storage(minio_container: MinioContainer) -> BlobStorage:
    """Create blob storage instance using MinIO testcontainer."""
    minio_config = minio_container.get_config()
    endpoint = minio_config["endpoint"]
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"http://{endpoint}"

    # Create blob storage with explicit config (cleaner than env vars)
    return S3BlobStorage(
        endpoint=endpoint,
        access_key=minio_config["access_key"],
        secret_key=minio_config["secret_key"],
        bucket_name="test-bucket",
        secure=False,
    )


@pytest.fixture(scope="function")
def app(
    postgres_container: PostgresContainer, test_blob_storage: BlobStorage
) -> Generator[Flask, None, None]:
    """
    Create Flask app for testing with database and MinIO storage.

    This fixture uses testcontainers to spin up real PostgreSQL and MinIO
    instances for integration testing.
    """
    # Set up database URL from testcontainer
    os.environ["DATABASE_URL"] = postgres_container.get_connection_url()

    # Create app
    app = create_app()
    app.config["TESTING"] = True

    # Override blob storage in app context to use test blob storage
    # This is cleaner than modifying environment variables at runtime
    from flask import g

    from src.context import AppContext
    from src.infrastructure.database import get_db

    @app.before_request
    def setup_test_context() -> None:
        """Set up test context with explicit blob storage."""
        g.db = next(get_db())
        g.app_context = AppContext(g.db, blob_storage=test_blob_storage)

    # Replace the before_request handler
    app.before_request_funcs[None] = [setup_test_context]

    yield app

    # Clean up environment variable
    os.environ.pop("DATABASE_URL", None)


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture(scope="function")
def test_user(app: Flask) -> Generator[Any, None, None]:
    """Create a test user for authentication."""
    from shared.models import User

    from src.infrastructure.database import get_db

    db = next(get_db())
    password_hash = User.hash_password("test_password")

    row = db.fetchone(
        """
        INSERT INTO users (username, email, password_hash, full_name)
        VALUES (%(username)s, %(email)s, %(password_hash)s, %(full_name)s)
        RETURNING *
        """,
        {
            "username": "test_user",
            "email": "test@example.com",
            "password_hash": password_hash,
            "full_name": "Test User",
        },
    )
    assert row is not None
    user = User(**row)

    yield user

    # Cleanup
    db.execute("DELETE FROM users WHERE id = %(id)s", {"id": user.id})


@pytest.fixture(scope="function")
def test_token(test_user: Any) -> str:
    """Create a JWT token for the test user."""
    from src.infrastructure.auth import create_access_token

    return create_access_token(test_user.id)


@pytest.fixture(scope="function")
def auth_headers(test_token: str) -> dict[str, str]:
    """Create authentication headers with Bearer token."""
    return {"Authorization": f"Bearer {test_token}"}


def test_heartbeat(client: FlaskClient) -> None:
    """Test heartbeat endpoint."""
    response = client.get("/heartbeat")

    assert response.status_code == 200


def test_health(client: FlaskClient) -> None:
    """Test health endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"


def test_upload_document(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test uploading a document."""
    # Create test file
    file_content = b"This is a test document"
    file_data = {"file": (BytesIO(file_content), "test.txt", "text/plain")}

    response = client.post(
        "/api/documents/upload",
        data=file_data,
        content_type="multipart/form-data",
        headers=auth_headers,
    )

    if response.status_code != 201:
        print(f"Error response: {response.data.decode()}")

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["message"] == "Document uploaded successfully"
    assert "document" in data
    assert data["document"]["filename"] == "test.txt"


def test_upload_invalid_file_type(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test uploading an invalid file type."""
    file_data = {"file": (BytesIO(b"content"), "test.exe", "application/x-executable")}

    response = client.post(
        "/api/documents/upload",
        data=file_data,
        content_type="multipart/form-data",
        headers=auth_headers,
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_upload_no_file(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test uploading without a file."""
    response = client.post(
        "/api/documents/upload", data={}, content_type="multipart/form-data", headers=auth_headers
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_list_documents(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test listing documents."""
    response = client.get("/api/documents", headers=auth_headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "documents" in data
    assert "count" in data
    assert isinstance(data["documents"], list)


def test_delete_document(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test deleting a document."""
    # First, upload a document
    file_data = {"file": (BytesIO(b"test content"), "test.txt", "text/plain")}
    upload_response = client.post(
        "/api/documents/upload",
        data=file_data,
        content_type="multipart/form-data",
        headers=auth_headers,
    )
    upload_data = json.loads(upload_response.data)
    doc_id = upload_data["document"]["id"]

    # Delete the document
    response = client.delete(f"/api/documents/{doc_id}", headers=auth_headers)

    if response.status_code != 200:
        print(f"Delete error response: {response.data.decode()}")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Document deleted successfully"


def test_delete_nonexistent_document(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test deleting a nonexistent document."""
    response = client.delete("/api/documents/99999", headers=auth_headers)

    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data


def test_chat_endpoint(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test chat endpoint."""
    chat_data = {"message": "What is RAG?", "rag_type": "vector"}

    response = client.post(
        "/api/chat",
        data=json.dumps(chat_data),
        content_type="application/json",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "answer" in data
    assert "context" in data
    assert "session_id" in data


def test_chat_no_message(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test chat endpoint without a message."""
    response = client.post(
        "/api/chat", data=json.dumps({}), content_type="application/json", headers=auth_headers
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_chat_with_session(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test chat endpoint with existing session."""
    # First message to create session
    chat_data1 = {"message": "Hello"}
    response1 = client.post(
        "/api/chat",
        data=json.dumps(chat_data1),
        content_type="application/json",
        headers=auth_headers,
    )
    data1 = json.loads(response1.data)
    session_id = data1["session_id"]

    # Second message with session ID
    chat_data2 = {"message": "Follow up question", "session_id": session_id}
    response2 = client.post(
        "/api/chat",
        data=json.dumps(chat_data2),
        content_type="application/json",
        headers=auth_headers,
    )

    assert response2.status_code == 200
    data2 = json.loads(response2.data)
    assert data2["session_id"] == session_id


def test_list_sessions(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test listing chat sessions."""
    response = client.get("/api/sessions", headers=auth_headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "sessions" in data
    assert "count" in data
    assert isinstance(data["sessions"], list)


def test_get_session_messages(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test getting messages for a session."""
    # Create a session with a message
    chat_data = {"message": "Test message"}
    chat_response = client.post(
        "/api/chat",
        data=json.dumps(chat_data),
        content_type="application/json",
        headers=auth_headers,
    )
    chat_data_response = json.loads(chat_response.data)
    session_id = chat_data_response["session_id"]

    # Get messages for the session
    response = client.get(f"/api/sessions/{session_id}/messages", headers=auth_headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "messages" in data
    assert "count" in data
    assert len(data["messages"]) >= 2  # User message + assistant response


def test_upload_duplicate_document(client: FlaskClient, auth_headers: dict[str, str]) -> None:
    """Test uploading the same document twice (deduplication)."""
    file_content = b"Duplicate content"

    # Upload first time
    file_data1 = {"file": (BytesIO(file_content), "test1.txt", "text/plain")}
    response1 = client.post(
        "/api/documents/upload",
        data=file_data1,
        content_type="multipart/form-data",
        headers=auth_headers,
    )
    json.loads(response1.data)

    # Upload second time with same content
    file_data2 = {"file": (BytesIO(file_content), "test2.txt", "text/plain")}
    response2 = client.post(
        "/api/documents/upload",
        data=file_data2,
        content_type="multipart/form-data",
        headers=auth_headers,
    )
    json.loads(response2.data)

    # Both should succeed (or second should indicate duplicate)
    assert response1.status_code == 201
    assert response2.status_code in [200, 201]
