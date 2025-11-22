"""General Socket.IO infrastructure for real-time communication."""

from collections.abc import Callable, Mapping

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

    def _handle_connect(self, auth: dict[str, str] | None = None) -> None:
        """
        Handle client connection.

        Args:
            auth: Optional authentication data from client
        """
        print("Client connected")
        emit("connected", {"status": "connected"})

    def _handle_disconnect(self, reason: str | None = None) -> None:
        """
        Handle client disconnection.

        Args:
            reason: Optional disconnection reason
        """
        print("Client disconnected")

    def register_event(self, event_name: str, handler: EventHandler) -> None:
        """
        Register a custom event handler.

        Args:
            event_name: Name of the Socket.IO event
            handler: Callback function to handle the event
        """
        self.socketio.on_event(event_name, handler)
