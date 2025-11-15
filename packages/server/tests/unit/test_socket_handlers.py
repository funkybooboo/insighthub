"""Unit tests for Socket.IO handlers."""

from unittest.mock import Mock, patch

import pytest
from flask import Flask
from flask_socketio import SocketIO

from src.infrastructure.socket.socket_handler import SocketHandler


@pytest.fixture
def app() -> Flask:
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def socketio(app: Flask) -> SocketIO:
    """Create a test SocketIO instance."""
    return SocketIO(app)


@pytest.fixture
def socket_handler(socketio: SocketIO) -> SocketHandler:
    """Create a SocketHandler instance."""
    return SocketHandler(socketio)


class TestSocketHandler:
    """Tests for SocketHandler."""

    def test_initialization(self, socket_handler: SocketHandler, socketio: SocketIO) -> None:
        """Test socket handler initialization."""
        assert socket_handler.socketio == socketio

    def test_register_base_handlers_called(self, socketio: SocketIO) -> None:
        """Test that base handlers are registered on initialization."""
        with patch.object(SocketHandler, "_register_base_handlers") as mock_register:
            SocketHandler(socketio)
            mock_register.assert_called_once()

    def test_register_event(self, socket_handler: SocketHandler) -> None:
        """Test registering a custom event handler."""
        mock_handler = Mock()

        socket_handler.register_event("test_event", mock_handler)

    def test_handle_connect(self, socket_handler: SocketHandler) -> None:
        """Test handling client connection."""
        with patch("src.infrastructure.socket.socket_handler.emit") as mock_emit:
            socket_handler._handle_connect()
            mock_emit.assert_called_once_with("connected", {"status": "connected"})

    def test_handle_connect_with_auth(self, socket_handler: SocketHandler) -> None:
        """Test handling client connection with authentication."""
        with patch("src.infrastructure.socket.socket_handler.emit") as mock_emit:
            auth_data = {"token": "test-token"}
            socket_handler._handle_connect(auth_data)
            mock_emit.assert_called_once()

    def test_handle_disconnect(self, socket_handler: SocketHandler) -> None:
        """Test handling client disconnection."""
        socket_handler._handle_disconnect()

    def test_handle_disconnect_with_reason(self, socket_handler: SocketHandler) -> None:
        """Test handling client disconnection with reason."""
        socket_handler._handle_disconnect("Client closed connection")


class TestChatSocketHandlers:
    """Tests for chat socket handlers."""

    @patch("src.domains.chat.socket_handlers.get_db")
    @patch("src.domains.chat.socket_handlers.emit")
    @patch("src.domains.chat.socket_handlers.AppContext")
    def test_handle_chat_message_success(
        self, mock_context: Mock, mock_emit: Mock, mock_get_db: Mock, app: Flask
    ) -> None:
        """Test successful chat message handling."""
        from src.domains.chat.dtos import StreamEvent
        from src.domains.chat.socket_handlers import handle_chat_message

        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = Mock()
        mock_service.validate_message.return_value = None
        mock_service.stream_chat_response.return_value = [
            StreamEvent.chunk("Hello "),
            StreamEvent.chunk("world"),
            StreamEvent.complete(session_id=1, full_response="Hello world"),
        ]

        mock_user_service = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user_service.get_or_create_default_user.return_value = mock_user

        mock_context_instance = Mock()
        mock_context_instance.chat_service = mock_service
        mock_context_instance.user_service = mock_user_service
        mock_context_instance.llm_provider = Mock()
        mock_context.return_value = mock_context_instance

        with app.app_context():
            data = {"message": "Hello", "session_id": None, "rag_type": "vector"}
            handle_chat_message(data)

        assert mock_emit.call_count == 3
        mock_service.validate_message.assert_called_once_with("Hello")

    @patch("src.domains.chat.socket_handlers.get_db")
    @patch("src.domains.chat.socket_handlers.emit")
    @patch("src.domains.chat.socket_handlers.AppContext")
    def test_handle_chat_message_with_session_id(
        self, mock_context: Mock, mock_emit: Mock, mock_get_db: Mock, app: Flask
    ) -> None:
        """Test chat message handling with existing session."""
        from src.domains.chat.dtos import StreamEvent
        from src.domains.chat.socket_handlers import handle_chat_message

        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = Mock()
        mock_service.validate_message.return_value = None
        mock_service.stream_chat_response.return_value = [
            StreamEvent.complete(session_id=123, full_response="Response")
        ]

        mock_user_service = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user_service.get_or_create_default_user.return_value = mock_user

        mock_context_instance = Mock()
        mock_context_instance.chat_service = mock_service
        mock_context_instance.user_service = mock_user_service
        mock_context_instance.llm_provider = Mock()
        mock_context.return_value = mock_context_instance

        with app.app_context():
            data = {"message": "Hello", "session_id": "123", "rag_type": "vector"}
            handle_chat_message(data)

        mock_service.stream_chat_response.assert_called_once()
        call_kwargs = mock_service.stream_chat_response.call_args[1]
        assert call_kwargs["session_id"] == 123

    @patch("src.domains.chat.socket_handlers.get_db")
    @patch("src.domains.chat.socket_handlers.emit")
    @patch("src.domains.chat.socket_handlers.AppContext")
    def test_handle_chat_message_empty_message(
        self, mock_context: Mock, mock_emit: Mock, mock_get_db: Mock, app: Flask
    ) -> None:
        """Test handling empty chat message."""
        from src.domains.chat.exceptions import EmptyMessageError
        from src.domains.chat.socket_handlers import handle_chat_message

        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = Mock()
        mock_service.validate_message.side_effect = EmptyMessageError()

        mock_context_instance = Mock()
        mock_context_instance.chat_service = mock_service
        mock_context.return_value = mock_context_instance

        with app.app_context():
            data = {"message": "", "session_id": None}
            handle_chat_message(data)

        mock_emit.assert_called_once()
        call_args = mock_emit.call_args[0]
        assert call_args[0] == "error"

    @patch("src.domains.chat.socket_handlers.get_db")
    @patch("src.domains.chat.socket_handlers.emit")
    @patch("src.domains.chat.socket_handlers.AppContext")
    def test_handle_chat_message_error(
        self, mock_context: Mock, mock_emit: Mock, mock_get_db: Mock, app: Flask
    ) -> None:
        """Test handling errors during chat processing."""
        from src.domains.chat.socket_handlers import handle_chat_message

        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = Mock()
        mock_service.validate_message.side_effect = Exception("Database error")

        mock_context_instance = Mock()
        mock_context_instance.chat_service = mock_service
        mock_context.return_value = mock_context_instance

        with app.app_context():
            data = {"message": "Hello"}
            handle_chat_message(data)

        mock_emit.assert_called_once()
        call_args = mock_emit.call_args[0]
        assert call_args[0] == "error"
        assert "Database error" in call_args[1]["error"]

    @patch("src.domains.chat.socket_handlers.get_db")
    @patch("src.domains.chat.socket_handlers.emit")
    @patch("src.domains.chat.socket_handlers.AppContext")
    def test_handle_chat_message_closes_db(
        self, mock_context: Mock, mock_emit: Mock, mock_get_db: Mock, app: Flask
    ) -> None:
        """Test that database connection is properly closed."""
        from src.domains.chat.socket_handlers import handle_chat_message

        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = Mock()
        mock_service.validate_message.side_effect = Exception("Error")

        mock_context_instance = Mock()
        mock_context_instance.chat_service = mock_service
        mock_context.return_value = mock_context_instance

        with app.app_context():
            data = {"message": "Hello"}
            handle_chat_message(data)

        mock_db.close.assert_called_once()

    @patch("src.domains.chat.socket_handlers.get_db")
    @patch("src.domains.chat.socket_handlers.emit")
    @patch("src.domains.chat.socket_handlers.AppContext")
    def test_handle_chat_message_with_custom_rag_type(
        self, mock_context: Mock, mock_emit: Mock, mock_get_db: Mock, app: Flask
    ) -> None:
        """Test chat message handling with custom RAG type."""
        from src.domains.chat.dtos import StreamEvent
        from src.domains.chat.socket_handlers import handle_chat_message

        mock_db = Mock()
        mock_get_db.return_value = iter([mock_db])

        mock_service = Mock()
        mock_service.validate_message.return_value = None
        mock_service.stream_chat_response.return_value = [
            StreamEvent.complete(session_id=1, full_response="Response")
        ]

        mock_user_service = Mock()
        mock_user = Mock()
        mock_user.id = 1
        mock_user_service.get_or_create_default_user.return_value = mock_user

        mock_context_instance = Mock()
        mock_context_instance.chat_service = mock_service
        mock_context_instance.user_service = mock_user_service
        mock_context_instance.llm_provider = Mock()
        mock_context.return_value = mock_context_instance

        with app.app_context():
            data = {"message": "Hello", "rag_type": "graph"}
            handle_chat_message(data)

        call_kwargs = mock_service.stream_chat_response.call_args[1]
        assert call_kwargs["rag_type"] == "graph"
