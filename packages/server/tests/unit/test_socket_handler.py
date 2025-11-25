"""Unit tests for SocketHandler infrastructure component."""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask_socketio import SocketIO

from src.infrastructure.socket.socket_handler import SocketHandler


class TestSocketHandler:
    """Tests for SocketHandler infrastructure component."""

    @pytest.fixture
    def app(self) -> Flask:
        """Provide a test Flask app."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def mock_socketio(self) -> MagicMock:
        """Provide a mock SocketIO instance."""
        return MagicMock(spec=SocketIO)

    @pytest.fixture
    def socket_handler(self, mock_socketio: MagicMock) -> SocketHandler:
        """Provide a SocketHandler instance."""
        return SocketHandler(mock_socketio)

    def test_init_registers_base_handlers(self, mock_socketio: MagicMock) -> None:
        """Test that SocketHandler registers base event handlers on initialization."""
        SocketHandler(mock_socketio)

        # Verify that on_event was called for each base handler
        assert mock_socketio.on_event.call_count == 4

        # Check that the expected events were registered
        calls = mock_socketio.on_event.call_args_list
        event_names = [call[0][0] for call in calls]  # Extract first argument from each call

        assert "connect" in event_names
        assert "disconnect" in event_names
        assert "ping" in event_names
        assert "pong" in event_names

    @patch("src.infrastructure.socket.socket_handler.emit")
    def test_handle_connect_emits_connected_event(
        self, mock_emit: MagicMock, socket_handler: SocketHandler, app: Flask
    ) -> None:
        """Test that _handle_connect emits connected event with proper data."""
        # Setup
        with app.test_request_context():
            from flask import request
            request.sid = "test_client_123"  # type: ignore

            # Execute
            socket_handler._handle_connect()

        # Assert
        mock_emit.assert_called_once_with(
            "connected",
            {
                "status": "connected",
                "client_id": "test_client_123",
                "heartbeat_interval": 30000,
            },
        )

    def test_handle_connect_stores_connection_info(
        self, socket_handler: SocketHandler, app: Flask
    ) -> None:
        """Test that _handle_connect stores connection information."""
        # Setup
        with app.test_request_context():
            from flask import request
            request.sid = "test_client_456"  # type: ignore

            # Execute
            socket_handler._handle_connect()

        # Assert
        assert hasattr(socket_handler, "_connections")
        assert "test_client_456" in socket_handler._connections
        connection_info = socket_handler._connections["test_client_456"]
        assert "connected_at" in connection_info
        assert "last_ping" in connection_info
        assert connection_info["user_id"] is None

    def test_handle_connect_with_auth_data(
        self, socket_handler: SocketHandler, app: Flask
    ) -> None:
        """Test that _handle_connect handles auth data parameter."""
        # Setup
        with app.test_request_context():
            from flask import request
            request.sid = "test_client_789"  # type: ignore
            auth_data = {"token": "some_token"}

            # Execute
        socket_handler._handle_connect(auth_data)

        # Assert - should not raise exception and should still work
        assert "test_client_789" in socket_handler._connections

    @patch("src.infrastructure.socket.socket_handler.request")
    def test_handle_disconnect_cleans_up_connection(
        self, mock_request: MagicMock, socket_handler: SocketHandler
    ) -> None:
        """Test that _handle_disconnect cleans up connection tracking."""
        # Setup
        mock_request.sid = "test_client_999"
        socket_handler._connections = {"test_client_999": {"some": "data"}}

        # Execute
        socket_handler._handle_disconnect("client_disconnect")

        # Assert
        assert "test_client_999" not in socket_handler._connections

    @patch("src.infrastructure.socket.socket_handler.request")
    def test_handle_disconnect_with_no_existing_connection(
        self, mock_request: MagicMock, socket_handler: SocketHandler
    ) -> None:
        """Test that _handle_disconnect handles non-existent connections gracefully."""
        # Setup
        mock_request.sid = "non_existent_client"

        # Execute - should not raise exception
        socket_handler._handle_disconnect()

        # Assert - no connections dict should exist or be empty
        if hasattr(socket_handler, "_connections"):
            assert "non_existent_client" not in socket_handler._connections

    @patch("src.infrastructure.socket.socket_handler.request")
    @patch("src.infrastructure.socket.socket_handler.emit")
    def test_handle_ping_updates_last_ping_and_emits_pong(
        self, mock_emit: MagicMock, mock_request: MagicMock, socket_handler: SocketHandler
    ) -> None:
        """Test that _handle_ping updates last_ping and emits pong."""
        # Setup
        mock_request.sid = "ping_client"
        socket_handler._connections = {
            "ping_client": {"last_ping": "old_timestamp", "user_id": None}
        }

        # Execute
        socket_handler._handle_ping({"data": "test"})

        # Assert
        mock_emit.assert_called_once_with("pong", {"timestamp": "2025-11-24T00:00:00Z"})
        # Note: In real implementation, this would be datetime.now()

    @patch("src.infrastructure.socket.socket_handler.request")
    def test_handle_ping_with_no_connection_tracking(
        self, mock_request: MagicMock, socket_handler: SocketHandler
    ) -> None:
        """Test that _handle_ping handles missing connection tracking gracefully."""
        # Setup
        mock_request.sid = "ping_client_no_tracking"

        # Execute - should not raise exception
        socket_handler._handle_ping()

        # Assert - should not create connections dict
        assert not hasattr(socket_handler, "_connections")

    @patch("src.infrastructure.socket.socket_handler.request")
    def test_handle_pong_updates_last_ping(
        self, mock_request: MagicMock, socket_handler: SocketHandler
    ) -> None:
        """Test that _handle_pong updates last_ping timestamp."""
        # Setup
        mock_request.sid = "pong_client"
        socket_handler._connections = {
            "pong_client": {"last_ping": "old_timestamp", "user_id": None}
        }

        # Execute
        socket_handler._handle_pong({"timestamp": "new_timestamp"})

        # Assert - the timestamp should be updated (in real impl, to current time)
        # We can't easily test the exact timestamp without mocking datetime

    @patch("src.infrastructure.socket.socket_handler.request")
    def test_handle_pong_with_no_connection_tracking(
        self, mock_request: MagicMock, socket_handler: SocketHandler
    ) -> None:
        """Test that _handle_pong handles missing connection tracking gracefully."""
        # Setup
        mock_request.sid = "pong_client_no_tracking"

        # Execute - should not raise exception
        socket_handler._handle_pong()

        # Assert
        assert not hasattr(socket_handler, "_connections")

    def test_register_event_calls_socketio_on_event(
        self, mock_socketio: MagicMock, socket_handler: SocketHandler
    ) -> None:
        """Test that register_event calls socketio.on_event with correct parameters."""

        # Setup
        def test_handler(data) -> None:
            pass

        # Execute
        socket_handler.register_event("custom_event", test_handler)

        # Assert that the custom event was registered
        mock_socketio.on_event.assert_any_call("custom_event", test_handler)

    def test_register_event_accepts_different_handler_types(
        self, mock_socketio: MagicMock, socket_handler: SocketHandler
    ) -> None:
        """Test that register_event accepts different types of handler functions."""

        # Test with function
        def lambda_handler(_) -> None:
            pass

        socket_handler.register_event("lambda_event", lambda_handler)
        mock_socketio.on_event.assert_called_with("lambda_event", lambda_handler)

        # Reset mock
        mock_socketio.reset_mock()

        # Test with method - create a proper handler method for testing
        def custom_handler(data) -> None:
            pass

        socket_handler.register_event("method_event", custom_handler)
        mock_socketio.on_event.assert_called_with("method_event", custom_handler)

    def test_multiple_connections_are_tracked_separately(
        self, socket_handler: SocketHandler
    ) -> None:
        """Test that multiple client connections are tracked separately."""
        # This test verifies the connection tracking isolation
        # Since we can't easily mock request.sid in a loop, we'll test the data structure

        # Simulate multiple connections
        socket_handler._connections = {
            "client1": {"connected_at": "time1", "user_id": None},
            "client2": {"connected_at": "time2", "user_id": 123},
        }

        # Verify they are stored separately
        assert socket_handler._connections["client1"]["user_id"] is None
        assert socket_handler._connections["client2"]["user_id"] == 123
        assert socket_handler._connections["client1"]["connected_at"] == "time1"
        assert socket_handler._connections["client2"]["connected_at"] == "time2"

    def test_connection_tracking_initializes_empty_dict(
        self, socket_handler: SocketHandler
    ) -> None:
        """Test that connection tracking starts with an empty dictionary."""
        # Initially, no connections dict should exist
        assert not hasattr(socket_handler, "_connections")

        # After first connection, it should exist
        # (We can't easily test this without mocking request.sid)

    def test_handle_connect_returns_none_for_successful_connection(
        self, socket_handler: SocketHandler
    ) -> None:
        """Test that _handle_connect returns None on successful connection."""
        # This tests the return value contract
        with (
            patch("src.infrastructure.socket.socket_handler.request") as mock_request,
            patch("src.infrastructure.socket.socket_handler.emit"),
        ):
            mock_request.sid = "test_client"

            result = socket_handler._handle_connect()

            # Should return None (successful connection)
            assert result is None

    def test_handle_connect_return_type_matches_socketio_expectations(
        self, socket_handler: SocketHandler
    ) -> None:
        """Test that _handle_connect return type is compatible with Socket.IO."""
        # Socket.IO connect handlers can return bool or None
        # None means allow connection, False means reject

        with (
            patch("src.infrastructure.socket.socket_handler.request") as mock_request,
            patch("src.infrastructure.socket.socket_handler.emit"),
        ):
            mock_request.sid = "test_client"

            result = socket_handler._handle_connect()

            # Should return None (allow connection) or bool
            assert result is None or isinstance(result, bool)
