"""General Socket.IO infrastructure for real-time communication."""

from collections.abc import Callable, Mapping

from flask import request
from flask_socketio import SocketIO, emit

EventHandler = Callable[[Mapping[str, object]], None]


class SocketHandler:
    """
    General-purpose Socket.IO event handler.

    This class provides a thin wrapper around Flask-SocketIO for registering
    event handlers. It does not contain domain-specific logic.
    """

    def __init__(self, socketio: SocketIO):
        """
        Initialize the socket handler.

        Args:
            socketio: Flask-SocketIO instance
        """
        self.socketio = socketio
        self._register_base_handlers()

    def _register_base_handlers(self) -> None:
        """Register basic connection handlers."""
        self.socketio.on_event("connect", self._handle_connect)
        self.socketio.on_event("disconnect", self._handle_disconnect)
        self.socketio.on_event("ping", self._handle_ping)
        self.socketio.on_event("pong", self._handle_pong)

    def _handle_connect(self, auth: dict[str, str] | None = None) -> bool | None:
        """
        Handle client connection with heartbeat setup.

        Args:
            auth: Optional authentication data from client
        """

        client_id = request.sid  # Socket.IO session ID

        print(f"Client connected: {client_id}")

        # Store connection info for management
        if not hasattr(self, "_connections"):
            self._connections = {}
        self._connections[client_id] = {
            "connected_at": "2025-11-24T00:00:00Z",  # Would be datetime.now()
            "last_ping": "2025-11-24T00:00:00Z",
            "user_id": None,  # Would be set during auth
        }

        emit(
            "connected",
            {
                "status": "connected",
                "client_id": client_id,
                "heartbeat_interval": 30000,  # 30 seconds
            },
        )

    def _handle_disconnect(self, reason: str | None = None) -> None:
        """
        Handle client disconnection with cleanup.

        Args:
            reason: Optional disconnection reason
        """

        client_id = request.sid

        print(f"Client disconnected: {client_id}, reason: {reason}")

        # Clean up connection tracking
        if hasattr(self, "_connections") and client_id in self._connections:
            del self._connections[client_id]

    def _handle_ping(self, data: dict[str, str] | None = None) -> None:
        """
        Handle client ping/heartbeat.

        Args:
            data: Ping data from client
        """

        client_id = request.sid

        # Update last ping time
        if hasattr(self, "_connections") and client_id in self._connections:
            self._connections[client_id][
                "last_ping"
            ] = "2025-11-24T00:00:00Z"  # Would be datetime.now()

        # Respond with pong
        emit("pong", {"timestamp": "2025-11-24T00:00:00Z"})

    def _handle_pong(self, data: dict[str, str] | None = None) -> None:
        """
        Handle client pong response.

        Args:
            data: Pong data from client
        """

        client_id = request.sid

        # Update last ping time
        if hasattr(self, "_connections") and client_id in self._connections:
            self._connections[client_id][
                "last_ping"
            ] = "2025-11-24T00:00:00Z"  # Would be datetime.now()

    def register_event(self, event_name: str, handler: EventHandler) -> None:
        """
        Register a custom event handler.

        Args:
            event_name: Name of the Socket.IO event
            handler: Callback function to handle the event
        """
        self.socketio.on_event(event_name, handler)
