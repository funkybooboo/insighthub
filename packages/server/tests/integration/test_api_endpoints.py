"""Integration tests for API endpoints."""

import json
import os
from io import BytesIO
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer

from src.app import create_app


@pytest.fixture(scope="function")
def app(
    postgres_container: PostgresContainer, minio_container: MinioContainer
) -> Generator[Flask, None, None]:
    """Create Flask app for testing with database and storage."""
    # Set up environment variables for the app
    os.environ["DATABASE_URL"] = postgres_container.get_connection_url()
    minio_config = minio_container.get_config()

    # Ensure endpoint has protocol
    endpoint = minio_config["endpoint"]
    if not endpoint.startswith(("http://", "https://")):
        endpoint = f"http://{endpoint}"

    os.environ["S3_ENDPOINT_URL"] = endpoint
    os.environ["S3_ACCESS_KEY"] = minio_config["access_key"]
    os.environ["S3_SECRET_KEY"] = minio_config["secret_key"]
    os.environ["S3_BUCKET_NAME"] = "test-bucket"

    app = create_app()
    app.config["TESTING"] = True

    yield app

    # Clean up environment variables
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("S3_ENDPOINT_URL", None)
    os.environ.pop("S3_ACCESS_KEY", None)
    os.environ.pop("S3_SECRET_KEY", None)
    os.environ.pop("S3_BUCKET_NAME", None)


@pytest.fixture(scope="function")
def client(app: Flask) -> FlaskClient:
    """Create Flask test client."""
    return app.test_client()


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


def test_upload_document(client: FlaskClient) -> None:
    """Test uploading a document."""
    # Create test file
    file_content = b"This is a test document"
    file_data = {
        "file": (BytesIO(file_content), "test.txt", "text/plain")
    }

    response = client.post(
        "/api/documents/upload",
        data=file_data,
        content_type="multipart/form-data"
    )

    if response.status_code != 201:
        print(f"Error response: {response.data.decode()}")

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["message"] == "Document uploaded successfully"
    assert "document" in data
    assert data["document"]["filename"] == "test.txt"


def test_upload_invalid_file_type(client: FlaskClient) -> None:
    """Test uploading an invalid file type."""
    file_data = {
        "file": (BytesIO(b"content"), "test.exe", "application/x-executable")
    }

    response = client.post(
        "/api/documents/upload",
        data=file_data,
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_upload_no_file(client: FlaskClient) -> None:
    """Test uploading without a file."""
    response = client.post(
        "/api/documents/upload",
        data={},
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_list_documents(client: FlaskClient) -> None:
    """Test listing documents."""
    response = client.get("/api/documents")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "documents" in data
    assert "count" in data
    assert isinstance(data["documents"], list)


def test_delete_document(client: FlaskClient) -> None:
    """Test deleting a document."""
    # First, upload a document
    file_data = {
        "file": (BytesIO(b"test content"), "test.txt", "text/plain")
    }
    upload_response = client.post(
        "/api/documents/upload",
        data=file_data,
        content_type="multipart/form-data"
    )
    upload_data = json.loads(upload_response.data)
    doc_id = upload_data["document"]["id"]

    # Delete the document
    response = client.delete(f"/api/documents/{doc_id}")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Document deleted successfully"


def test_delete_nonexistent_document(client: FlaskClient) -> None:
    """Test deleting a nonexistent document."""
    response = client.delete("/api/documents/99999")

    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data


def test_chat_endpoint(client: FlaskClient) -> None:
    """Test chat endpoint."""
    chat_data = {
        "message": "What is RAG?",
        "rag_type": "vector"
    }

    response = client.post(
        "/api/chat",
        data=json.dumps(chat_data),
        content_type="application/json"
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "answer" in data
    assert "context" in data
    assert "session_id" in data


def test_chat_no_message(client: FlaskClient) -> None:
    """Test chat endpoint without a message."""
    response = client.post(
        "/api/chat",
        data=json.dumps({}),
        content_type="application/json"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_chat_with_session(client: FlaskClient) -> None:
    """Test chat endpoint with existing session."""
    # First message to create session
    chat_data1 = {"message": "Hello"}
    response1 = client.post(
        "/api/chat",
        data=json.dumps(chat_data1),
        content_type="application/json"
    )
    data1 = json.loads(response1.data)
    session_id = data1["session_id"]

    # Second message with session ID
    chat_data2 = {"message": "Follow up question", "session_id": session_id}
    response2 = client.post(
        "/api/chat",
        data=json.dumps(chat_data2),
        content_type="application/json"
    )

    assert response2.status_code == 200
    data2 = json.loads(response2.data)
    assert data2["session_id"] == session_id


def test_list_sessions(client: FlaskClient) -> None:
    """Test listing chat sessions."""
    response = client.get("/api/sessions")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "sessions" in data
    assert "count" in data
    assert isinstance(data["sessions"], list)


def test_get_session_messages(client: FlaskClient) -> None:
    """Test getting messages for a session."""
    # Create a session with a message
    chat_data = {"message": "Test message"}
    chat_response = client.post(
        "/api/chat",
        data=json.dumps(chat_data),
        content_type="application/json"
    )
    chat_data_response = json.loads(chat_response.data)
    session_id = chat_data_response["session_id"]

    # Get messages for the session
    response = client.get(f"/api/sessions/{session_id}/messages")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "messages" in data
    assert "count" in data
    assert len(data["messages"]) >= 2  # User message + assistant response


def test_upload_duplicate_document(client: FlaskClient) -> None:
    """Test uploading the same document twice (deduplication)."""
    file_content = b"Duplicate content"

    # Upload first time
    file_data1 = {
        "file": (BytesIO(file_content), "test1.txt", "text/plain")
    }
    response1 = client.post(
        "/api/documents/upload",
        data=file_data1,
        content_type="multipart/form-data"
    )
    data1 = json.loads(response1.data)

    # Upload second time with same content
    file_data2 = {
        "file": (BytesIO(file_content), "test2.txt", "text/plain")
    }
    response2 = client.post(
        "/api/documents/upload",
        data=file_data2,
        content_type="multipart/form-data"
    )
    data2 = json.loads(response2.data)

    # Both should succeed (or second should indicate duplicate)
    assert response1.status_code == 201
    assert response2.status_code in [200, 201]
