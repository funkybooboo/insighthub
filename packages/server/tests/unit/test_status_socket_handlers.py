"""Unit tests for status Socket.IO handlers."""

from unittest.mock import Mock, patch

import pytest

from src.domains.status.socket_handlers import (
    broadcast_document_status,
    broadcast_workspace_status,
    handle_subscribe_status,
    register_status_socket_handlers,
)


class TestStatusSocketHandlers:
    """Tests for status Socket.IO handlers."""

    @patch("src.domains.status.socket_handlers.join_room")
    @patch("src.domains.status.socket_handlers.emit")
    def test_handle_subscribe_status_success(self, mock_emit, mock_join_room):
        """Test successful subscription to status updates."""
        data = {"user_id": 123}

        handle_subscribe_status(data)

        # Verify client joined room
        mock_join_room.assert_called_once_with("user_123")

        # Verify subscription confirmation was emitted
        mock_emit.assert_called_once_with("subscribed", {"user_id": 123, "room": "user_123"})

    @patch("src.domains.status.socket_handlers.join_room")
    @patch("src.domains.status.socket_handlers.emit")
    def test_handle_subscribe_status_missing_user_id(self, mock_emit, mock_join_room):
        """Test subscription with missing user_id."""
        data = {}

        handle_subscribe_status(data)

        # Verify room was not joined
        mock_join_room.assert_not_called()

        # Verify error was emitted
        mock_emit.assert_called_once_with("error", {"error": "user_id is required"})

    def test_broadcast_document_status_success(self):
        """Test broadcasting document status update."""
        mock_socketio = Mock()

        event_data = {
            "document_id": 123,
            "user_id": 456,
            "workspace_id": 789,
            "status": "processing",
            "error": None,
            "chunk_count": None,
            "filename": "test.pdf",
            "metadata": {"progress": 0.5},
        }

        broadcast_document_status(event_data, mock_socketio)

        # Verify emit was called with correct parameters
        mock_socketio.emit.assert_called_once_with(
            "document_status", event_data, to="user_456", namespace="/"
        )

    def test_broadcast_document_status_missing_user_id(self):
        """Test broadcasting document status without user_id."""
        mock_socketio = Mock()

        event_data = {
            "document_id": 123,
            "status": "processing",
        }

        broadcast_document_status(event_data, mock_socketio)

        # Verify emit was not called
        mock_socketio.emit.assert_not_called()

    def test_broadcast_workspace_status_success(self):
        """Test broadcasting workspace status update."""
        mock_socketio = Mock()

        event_data = {
            "workspace_id": 789,
            "user_id": 456,
            "status": "ready",
            "message": "Workspace is ready",
            "name": "My Workspace",
            "metadata": {},
        }

        broadcast_workspace_status(event_data, mock_socketio)

        # Verify emit was called with correct parameters
        mock_socketio.emit.assert_called_once_with(
            "workspace_status", event_data, to="user_456", namespace="/"
        )

    def test_broadcast_workspace_status_missing_user_id(self):
        """Test broadcasting workspace status without user_id."""
        mock_socketio = Mock()

        event_data = {
            "workspace_id": 789,
            "status": "ready",
        }

        broadcast_workspace_status(event_data, mock_socketio)

        # Verify emit was not called
        mock_socketio.emit.assert_not_called()

    def test_register_status_socket_handlers(self):
        """Test registering status socket handlers."""
        mock_socketio = Mock()

        register_status_socket_handlers(mock_socketio)

        # Verify on_event was called
        mock_socketio.on_event.assert_called_once_with("subscribe_status", handle_subscribe_status)
