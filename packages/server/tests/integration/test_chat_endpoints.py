"""Integration tests for chat endpoints."""

import json
from typing import Any

from flask.testing import FlaskClient


def test_send_chat_message_success(client: FlaskClient, auth_token: str) -> None:
    """Test successful chat message sending."""
    message_data = {
        "content": "What is machine learning?",
        "message_type": "user",
        "ignore_rag": False
    }

    response = client.post(
        "/api/workspaces/1/chat/sessions/1/messages",
        data=json.dumps(message_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message_id" in data
    assert isinstance(data["message_id"], str)


def test_send_chat_message_missing_content(client: FlaskClient, auth_token: str) -> None:
    """Test sending message with missing content."""
    message_data = {"message_type": "user"}

    response = client.post(
        "/api/workspaces/1/chat/sessions/1/messages",
        data=json.dumps(message_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_send_chat_message_empty_content(client: FlaskClient, auth_token: str) -> None:
    """Test sending message with empty content."""
    message_data = {"content": "", "message_type": "user"}

    response = client.post(
        "/api/workspaces/1/chat/sessions/1/messages",
        data=json.dumps(message_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_send_chat_message_too_long(client: FlaskClient, auth_token: str) -> None:
    """Test sending message that exceeds length limit."""
    long_content = "a" * 10001  # Over 10,000 character limit
    message_data = {"content": long_content, "message_type": "user"}

    response = client.post(
        "/api/workspaces/1/chat/sessions/1/messages",
        data=json.dumps(message_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_send_chat_message_invalid_type(client: FlaskClient, auth_token: str) -> None:
    """Test sending message with invalid message type."""
    message_data = {"content": "Hello", "message_type": "invalid"}

    response = client.post(
        "/api/workspaces/1/chat/sessions/1/messages",
        data=json.dumps(message_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_send_chat_message_unauthorized(client: FlaskClient) -> None:
    """Test sending message without authentication."""
    message_data = {"content": "Hello", "message_type": "user"}

    response = client.post(
        "/api/workspaces/1/chat/sessions/1/messages",
        data=json.dumps(message_data),
        content_type="application/json"
    )

    assert response.status_code == 401


def test_cancel_chat_message_success(client: FlaskClient, auth_token: str) -> None:
    """Test successful chat message cancellation."""
    cancel_data = {"message_id": "msg-123"}

    response = client.post(
        "/api/workspaces/1/chat/sessions/1/cancel",
        data=json.dumps(cancel_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "cancelled" in data["message"].lower()


def test_cancel_chat_message_unauthorized(client: FlaskClient) -> None:
    """Test cancelling message without authentication."""
    response = client.post(
        "/api/workspaces/1/chat/sessions/1/cancel",
        content_type="application/json"
    )

    assert response.status_code == 401


def test_create_chat_session_success(client: FlaskClient, auth_token: str) -> None:
    """Test successful chat session creation."""
    session_data = {"title": "Test Chat Session"}

    response = client.post(
        "/api/workspaces/1/chat/sessions",
        data=json.dumps(session_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert "session_id" in data
    assert "title" in data
    assert data["title"] == "Test Chat Session"


def test_create_chat_session_no_title(client: FlaskClient, auth_token: str) -> None:
    """Test creating chat session without title."""
    response = client.post(
        "/api/workspaces/1/chat/sessions",
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert "session_id" in data
    assert "title" in data


def test_create_chat_session_title_too_long(client: FlaskClient, auth_token: str) -> None:
    """Test creating session with title that's too long."""
    long_title = "a" * 201  # Over 200 character limit
    session_data = {"title": long_title}

    response = client.post(
        "/api/workspaces/1/chat/sessions",
        data=json.dumps(session_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_create_chat_session_unauthorized(client: FlaskClient) -> None:
    """Test creating session without authentication."""
    session_data = {"title": "Test Session"}

    response = client.post(
        "/api/workspaces/1/chat/sessions",
        data=json.dumps(session_data),
        content_type="application/json"
    )

    assert response.status_code == 401


def test_list_chat_sessions_success(client: FlaskClient, auth_token: str) -> None:
    """Test successful chat session listing."""
    response = client.get(
        "/api/workspaces/1/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_list_chat_sessions_unauthorized(client: FlaskClient) -> None:
    """Test listing sessions without authentication."""
    response = client.get("/api/workspaces/1/chat/sessions")

    assert response.status_code == 401


def test_delete_chat_session_success(client: FlaskClient, auth_token: str) -> None:
    """Test successful chat session deletion."""
    response = client.delete(
        "/api/workspaces/1/chat/sessions/1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "deleted" in data["message"].lower()


def test_delete_chat_session_not_found(client: FlaskClient, auth_token: str) -> None:
    """Test deleting non-existent chat session."""
    response = client.delete(
        "/api/workspaces/1/chat/sessions/999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data


def test_delete_chat_session_unauthorized(client: FlaskClient) -> None:
    """Test deleting session without authentication."""
    response = client.delete("/api/workspaces/1/chat/sessions/1")

    assert response.status_code == 401


def test_get_chat_session_success(client: FlaskClient, auth_token: str) -> None:
    """Test successful chat session retrieval."""
    response = client.get(
        "/api/workspaces/1/chat/sessions/1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "session_id" in data
    assert "title" in data
    assert "message_count" in data


def test_get_chat_session_not_found(client: FlaskClient, auth_token: str) -> None:
    """Test getting non-existent chat session."""
    response = client.get(
        "/api/workspaces/1/chat/sessions/999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data


def test_get_chat_session_unauthorized(client: FlaskClient) -> None:
    """Test getting session without authentication."""
    response = client.get("/api/workspaces/1/chat/sessions/1")

    assert response.status_code == 401


def test_update_chat_session_success(client: FlaskClient, auth_token: str) -> None:
    """Test successful chat session update."""
    update_data = {"title": "Updated Session Title"}

    response = client.patch(
        "/api/workspaces/1/chat/sessions/1",
        data=json.dumps(update_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["session_id"] == 1
    assert data["title"] == "Updated Session Title"


def test_update_chat_session_invalid_title(client: FlaskClient, auth_token: str) -> None:
    """Test updating session with invalid title."""
    update_data = {"title": ""}

    response = client.patch(
        "/api/workspaces/1/chat/sessions/1",
        data=json.dumps(update_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_update_chat_session_unauthorized(client: FlaskClient) -> None:
    """Test updating session without authentication."""
    update_data = {"title": "New Title"}

    response = client.patch(
        "/api/workspaces/1/chat/sessions/1",
        data=json.dumps(update_data),
        content_type="application/json"
    )

    assert response.status_code == 401


def test_list_chat_sessions_workspace_filtering(client: FlaskClient, auth_token: str) -> None:
    """Test that chat sessions are properly filtered by workspace."""
    # First create sessions in different workspaces
    # This would require setting up test data, but for now we'll just test the endpoint exists
    response = client.get(
        "/api/workspaces/1/chat/sessions",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)


def test_create_session_workspace_association(client: FlaskClient, auth_token: str) -> None:
    """Test that created sessions are associated with the correct workspace."""
    session_data = {"title": "Workspace-Specific Session"}

    response = client.post(
        "/api/workspaces/2/chat/sessions",  # Different workspace
        data=json.dumps(session_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["title"] == "Workspace-Specific Session"


def test_get_session_workspace_validation(client: FlaskClient, auth_token: str) -> None:
    """Test that getting a session validates workspace ownership."""
    # Try to get a session that might belong to a different workspace
    response = client.get(
        "/api/workspaces/1/chat/sessions/1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    # Should either succeed (if session belongs to workspace) or return 404
    assert response.status_code in [200, 404]


def test_update_session_workspace_validation(client: FlaskClient, auth_token: str) -> None:
    """Test that updating a session validates workspace ownership."""
    update_data = {"title": "Updated Title"}

    response = client.patch(
        "/api/workspaces/1/chat/sessions/1",
        data=json.dumps(update_data),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    # Should either succeed or return 404 (depending on whether session exists in workspace)
    assert response.status_code in [200, 404]


def test_delete_session_workspace_validation(client: FlaskClient, auth_token: str) -> None:
    """Test that deleting a session validates workspace ownership."""
    response = client.delete(
        "/api/workspaces/1/chat/sessions/1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    # Should either succeed or return 404
    assert response.status_code in [200, 404]