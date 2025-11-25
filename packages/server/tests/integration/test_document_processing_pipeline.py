"""Integration tests for document processing pipeline."""

import json

import pytest
from flask.testing import FlaskClient


def test_document_upload_async_processing(client: FlaskClient, auth_token: str):
    """Test that document upload initiates async processing."""
    # Create test file content
    test_content = b"This is a test document for processing."
    test_filename = "test.txt"

    # Upload document
    response = client.post(
        "/api/workspaces/1/documents/upload",
        data={"file": (test_content, test_filename)},
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 201
    data = json.loads(response.data)

    # Should return document info
    assert "document" in data
    assert data["document"]["filename"] == test_filename
    assert data["document"]["processing_status"] == "pending"  # Should be pending, not ready


def test_document_status_update(client: FlaskClient, auth_token: str):
    """Test that document status can be updated via API."""
    # First create a document
    test_content = b"Test content"
    response = client.post(
        "/api/workspaces/1/documents/upload",
        data={"file": (test_content, "test.txt")},
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 201
    doc_data = json.loads(response.data)
    doc_id = doc_data["document"]["id"]

    # Update status to processing
    status_data = {"status": "processing", "chunk_count": 5}

    response = client.patch(
        f"/api/workspaces/1/documents/{doc_id}/status",
        data=json.dumps(status_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "Status updated successfully"


def test_document_status_update_invalid_status(client: FlaskClient, auth_token: str):
    """Test that invalid status values are rejected."""
    # Create a document first
    test_content = b"Test content"
    response = client.post(
        "/api/workspaces/1/documents/upload",
        data={"file": (test_content, "test.txt")},
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    doc_data = json.loads(response.data)
    doc_id = doc_data["document"]["id"]

    # Try to update with invalid status
    status_data = {"status": "invalid_status"}

    response = client.patch(
        f"/api/workspaces/1/documents/{doc_id}/status",
        data=json.dumps(status_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_document_status_update_wrong_workspace(client: FlaskClient, auth_token: str):
    """Test that status updates validate workspace ownership."""
    # Create document in workspace 1
    test_content = b"Test content"
    response = client.post(
        "/api/workspaces/1/documents/upload",
        data={"file": (test_content, "test.txt")},
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    doc_data = json.loads(response.data)
    doc_id = doc_data["document"]["id"]

    # Try to update status via workspace 2 (should fail)
    status_data = {"status": "ready"}

    response = client.patch(
        f"/api/workspaces/2/documents/{doc_id}/status",
        data=json.dumps(status_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 404


def test_wikipedia_fetch_async_processing(client: FlaskClient, auth_token: str):
    """Test that Wikipedia fetch initiates async processing."""
    fetch_data = {"query": "Machine Learning", "language": "en"}

    response = client.post(
        "/api/workspaces/1/documents/fetch-wikipedia",
        data=json.dumps(fetch_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 200
    data = json.loads(response.data)

    # Should return document info
    assert "document" in data
    assert "message" in data
    assert "Wikipedia_Machine_Learning_pending.md" in data["document"]["filename"]


def test_wikipedia_fetch_invalid_query(client: FlaskClient, auth_token: str):
    """Test Wikipedia fetch with invalid query."""
    fetch_data = {"query": ""}  # Empty query

    response = client.post(
        "/api/workspaces/1/documents/fetch-wikipedia",
        data=json.dumps(fetch_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_wikipedia_fetch_unsupported_language(client: FlaskClient, auth_token: str):
    """Test Wikipedia fetch with unsupported language."""
    fetch_data = {"query": "Test", "language": "invalid"}

    response = client.post(
        "/api/workspaces/1/documents/fetch-wikipedia",
        data=json.dumps(fetch_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_document_listing_includes_processing_status(client: FlaskClient, auth_token: str):
    """Test that document listing includes processing status."""
    # Upload a document
    test_content = b"Test document"
    response = client.post(
        "/api/workspaces/1/documents/upload",
        data={"file": (test_content, "status_test.txt")},
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response.status_code == 201

    # List documents
    response = client.get(
        "/api/workspaces/1/documents", headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)

    # Find our uploaded document
    uploaded_doc = None
    for doc in data:
        if doc["filename"] == "status_test.txt":
            uploaded_doc = doc
            break

    assert uploaded_doc is not None
    assert "processing_status" in uploaded_doc
    assert uploaded_doc["processing_status"] == "pending"


def test_document_duplicate_handling(client: FlaskClient, auth_token: str):
    """Test that duplicate documents are handled correctly."""
    test_content = b"Duplicate content"
    filename = "duplicate.txt"

    # Upload first time
    response1 = client.post(
        "/api/workspaces/1/documents/upload",
        data={"file": (test_content, filename)},
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response1.status_code == 201
    data1 = json.loads(response1.data)
    assert data1["is_duplicate"] is False

    # Upload second time (should be detected as duplicate)
    response2 = client.post(
        "/api/workspaces/1/documents/upload",
        data={"file": (test_content, filename)},
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert response2.status_code == 201
    data2 = json.loads(response2.data)
    assert data2["is_duplicate"] is True
    assert data2["document"]["id"] == data1["document"]["id"]  # Same document


@pytest.mark.parametrize(
    "status,should_succeed",
    [
        ("parsing", True),
        ("chunking", True),
        ("embedding", True),
        ("indexing", True),
        ("ready", True),
        ("failed", True),
        ("invalid", False),
    ],
)
def test_document_status_validation(
    client: FlaskClient, auth_token: str, status: str, should_succeed: bool
):
    """Test that document status updates validate status values."""
    # Create a document
    test_content = b"Status test"
    response = client.post(
        "/api/workspaces/1/documents/upload",
        data={"file": (test_content, "status_test.txt")},
        content_type="multipart/form-data",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    doc_data = json.loads(response.data)
    doc_id = doc_data["document"]["id"]

    # Try to update status
    status_data = {"status": status}

    response = client.patch(
        f"/api/workspaces/1/documents/{doc_id}/status",
        data=json.dumps(status_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    if should_succeed:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
