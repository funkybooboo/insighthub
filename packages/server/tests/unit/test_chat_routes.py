"""Unit tests for chat routes."""

import json
import pytest
from unittest.mock import Mock, patch
from flask import Flask

from shared.models import ChatSession
from src.domains.workspaces.chat.routes import chat_bp


@pytest.fixture
def app() -> Flask:
    """Create a test Flask app."""
    app = Flask(__name__)
    app.register_blueprint(chat_bp)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app: Flask):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def mock_chat_service():
    """Mock chat service."""
    return Mock()


@pytest.fixture
def mock_workspace_service():
    """Mock workspace service."""
    return Mock()


@pytest.fixture
def mock_app_context(mock_chat_service, mock_workspace_service):
    """Mock app context."""
    mock_context = Mock()
    mock_context.chat_service = mock_chat_service
    mock_context.workspace_service = mock_workspace_service
    return mock_context


class TestSendChatMessage:
    """Test cases for sending chat messages."""

    def test_send_message_success(
        self, client: Flask, mock_app_context: Mock, mock_chat_service: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test successful message sending."""
        # Setup mocks
        mock_workspace_service.validate_workspace_access.return_value = True
        mock_chat_service.send_message.return_value = "msg-123"

        message_data = {
            "content": "Hello, how are you?",
            "message_type": "user",
            "ignore_rag": False
        }

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/workspaces/1/chat/sessions/1/messages",
                data=json.dumps(message_data),
                content_type="application/json"
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["message_id"] == "msg-123"

    def test_send_message_missing_content(self, client: Flask) -> None:
        """Test sending message with missing content."""
        message_data = {"message_type": "user"}

        response = client.post(
            "/api/workspaces/1/chat/sessions/1/messages",
            data=json.dumps(message_data),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "content" in data["error"].lower()

    def test_send_message_empty_content(self, client: Flask) -> None:
        """Test sending message with empty content."""
        message_data = {"content": "", "message_type": "user"}

        response = client.post(
            "/api/workspaces/1/chat/sessions/1/messages",
            data=json.dumps(message_data),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "content" in data["error"].lower()

    def test_send_message_too_long(self, client: Flask) -> None:
        """Test sending message that is too long."""
        long_content = "a" * 10001  # Over 10,000 character limit
        message_data = {"content": long_content, "message_type": "user"}

        response = client.post(
            "/api/workspaces/1/chat/sessions/1/messages",
            data=json.dumps(message_data),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "long" in data["error"].lower()

    def test_send_message_invalid_message_type(self, client: Flask) -> None:
        """Test sending message with invalid message type."""
        message_data = {"content": "Hello", "message_type": "invalid"}

        response = client.post(
            "/api/workspaces/1/chat/sessions/1/messages",
            data=json.dumps(message_data),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "message_type" in data["error"].lower()

    def test_send_message_no_workspace_access(
        self, client: Flask, mock_app_context: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test sending message without workspace access."""
        mock_workspace_service.validate_workspace_access.return_value = False

        message_data = {"content": "Hello", "message_type": "user"}

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/workspaces/1/chat/sessions/1/messages",
                data=json.dumps(message_data),
                content_type="application/json"
            )

            assert response.status_code == 403
            data = json.loads(response.data)
            assert "access" in data["error"].lower()


class TestCancelChatMessage:
    """Test cases for cancelling chat messages."""

    def test_cancel_message_success(
        self, client: Flask, mock_app_context: Mock, mock_chat_service: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test successful message cancellation."""
        mock_workspace_service.validate_workspace_access.return_value = True

        cancel_data = {"message_id": "msg-123"}

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/workspaces/1/chat/sessions/1/cancel",
                data=json.dumps(cancel_data),
                content_type="application/json"
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "cancelled" in data["message"].lower()

    def test_cancel_message_no_workspace_access(
        self, client: Flask, mock_app_context: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test cancelling message without workspace access."""
        mock_workspace_service.validate_workspace_access.return_value = False

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/workspaces/1/chat/sessions/1/cancel",
                content_type="application/json"
            )

            assert response.status_code == 403
            data = json.loads(response.data)
            assert "access" in data["error"].lower()


class TestCreateChatSession:
    """Test cases for creating chat sessions."""

    def test_create_session_success(
        self, client: Flask, mock_app_context: Mock, mock_chat_service: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test successful session creation."""
        mock_workspace_service.validate_workspace_access.return_value = True

        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session.title = "Test Session"
        mock_chat_service.create_session.return_value = mock_session

        session_data = {"title": "Test Session"}

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/workspaces/1/chat/sessions",
                data=json.dumps(session_data),
                content_type="application/json"
            )

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data["session_id"] == 1
            assert data["title"] == "Test Session"
            # Verify workspace_id was passed to create_session
            mock_chat_service.create_session.assert_called_once()
            call_args = mock_chat_service.create_session.call_args
            assert call_args[1]["workspace_id"] == 1

    def test_create_session_title_too_long(self, client: Flask) -> None:
        """Test creating session with title that's too long."""
        long_title = "a" * 201  # Over 200 character limit
        session_data = {"title": long_title}

        response = client.post(
            "/api/workspaces/1/chat/sessions",
            data=json.dumps(session_data),
            content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "title" in data["error"].lower()


class TestListChatSessions:
    """Test cases for listing chat sessions."""

    def test_list_sessions_success(
        self, client: Flask, mock_app_context: Mock, mock_chat_service: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test successful session listing."""
        mock_workspace_service.validate_workspace_access.return_value = True

        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session.title = "Test Session"
        mock_session.created_at = Mock()
        mock_session.updated_at = Mock()
        mock_session.created_at.isoformat.return_value = "2025-01-01T00:00:00"
        mock_session.updated_at.isoformat.return_value = "2025-01-01T00:00:00"

        mock_chat_service.list_user_sessions.return_value = [mock_session]
        mock_chat_service.list_session_messages.return_value = []  # No messages

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.get("/api/workspaces/1/chat/sessions")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]["session_id"] == 1
            assert data[0]["title"] == "Test Session"
            assert data[0]["message_count"] == 0


class TestDeleteChatSession:
    """Test cases for deleting chat sessions."""

    def test_delete_session_success(
        self, client: Flask, mock_app_context: Mock, mock_chat_service: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test successful session deletion."""
        mock_workspace_service.validate_workspace_access.return_value = True
        mock_chat_service.delete_session.return_value = True

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.delete("/api/workspaces/1/chat/sessions/1")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "deleted" in data["message"].lower()

    def test_delete_session_not_found(
        self, client: Flask, mock_app_context: Mock, mock_chat_service: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test deleting non-existent session."""
        mock_workspace_service.validate_workspace_access.return_value = True
        mock_chat_service.delete_session.return_value = False

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.delete("/api/workspaces/1/chat/sessions/999")

            assert response.status_code == 404
            data = json.loads(response.data)
            assert "not found" in data["error"].lower()


class TestGetChatSession:
    """Test cases for getting individual chat sessions."""

    def test_get_session_success(
        self, client: Flask, mock_app_context: Mock, mock_chat_service: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test successful session retrieval."""
        mock_workspace_service.validate_workspace_access.return_value = True

        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session.title = "Test Session"
        mock_session.rag_type = "vector"
        mock_session.workspace_id = 1
        mock_session.created_at = Mock()
        mock_session.updated_at = Mock()
        mock_session.created_at.isoformat.return_value = "2025-01-01T00:00:00"
        mock_session.updated_at.isoformat.return_value = "2025-01-01T00:00:00"

        mock_chat_service.get_session_by_id.return_value = mock_session
        mock_chat_service.list_session_messages.return_value = []  # No messages

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.get("/api/workspaces/1/chat/sessions/1")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["session_id"] == 1
            assert data["title"] == "Test Session"
            assert data["message_count"] == 0

    def test_get_session_not_found(
        self, client: Flask, mock_app_context: Mock, mock_chat_service: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test getting non-existent session."""
        mock_workspace_service.validate_workspace_access.return_value = True
        mock_chat_service.get_session_by_id.return_value = None

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.get("/api/workspaces/1/chat/sessions/999")

            assert response.status_code == 404
            data = json.loads(response.data)
            assert "not found" in data["error"].lower()

    def test_get_session_wrong_workspace(
        self, client: Flask, mock_app_context: Mock, mock_chat_service: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test getting session that belongs to different workspace."""
        mock_workspace_service.validate_workspace_access.return_value = True

        mock_session = Mock(spec=ChatSession)
        mock_session.workspace_id = 2  # Different workspace

        mock_chat_service.get_session_by_id.return_value = mock_session

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.get("/api/workspaces/1/chat/sessions/1")

            assert response.status_code == 404
            data = json.loads(response.data)
            assert "not found" in data["error"].lower()


class TestUpdateChatSession:
    """Test cases for updating chat sessions."""

    def test_update_session_success(
        self, client: Flask, mock_app_context: Mock, mock_chat_service: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test successful session update."""
        mock_workspace_service.validate_workspace_access.return_value = True

        mock_session = Mock(spec=ChatSession)
        mock_session.id = 1
        mock_session.title = "Updated Title"
        mock_session.rag_type = "vector"
        mock_session.created_at = Mock()
        mock_session.updated_at = Mock()
        mock_session.created_at.isoformat.return_value = "2025-01-01T00:00:00"
        mock_session.updated_at.isoformat.return_value = "2025-01-01T00:00:00"

        mock_chat_service.get_session_by_id.return_value = mock_session
        mock_session.workspace_id = 1
        mock_chat_service.update_session.return_value = mock_session

        update_data = {"title": "Updated Title"}

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.patch(
                "/api/workspaces/1/chat/sessions/1",
                data=json.dumps(update_data),
                content_type="application/json"
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["session_id"] == 1
            assert data["title"] == "Updated Title"

    def test_update_session_empty_title(
        self, client: Flask, mock_app_context: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test updating session with empty title."""
        mock_workspace_service.validate_workspace_access.return_value = True

        update_data = {"title": ""}

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.patch(
                "/api/workspaces/1/chat/sessions/1",
                data=json.dumps(update_data),
                content_type="application/json"
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "empty" in data["error"].lower()

    def test_update_session_title_too_long(
        self, client: Flask, mock_app_context: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test updating session with title that's too long."""
        mock_workspace_service.validate_workspace_access.return_value = True

        long_title = "a" * 201
        update_data = {"title": long_title}

        with patch("src.domains.workspaces.chat.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.patch(
                "/api/workspaces/1/chat/sessions/1",
                data=json.dumps(update_data),
                content_type="application/json"
            )

            assert response.status_code == 400
            data = json.loads(response.data)
            assert "200" in data["error"]