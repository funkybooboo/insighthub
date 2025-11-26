"""WebSocket handler for real-time communication."""

from src.infrastructure.logger import create_logger
from typing import Any, Callable, Dict

from flask_socketio import SocketIO, emit, join_room, leave_room

logger = create_logger(__name__)


class SocketHandler:
    """Handles WebSocket connections and events."""

    def __init__(self, socketio: SocketIO):
        """Initialize socket handler."""
        self.socketio = socketio
        self.register_handlers()

    def register_handlers(self) -> None:
        """Register all socket event handlers."""

        @self.socketio.on("connect")
        def handle_connect() -> None:
            """Handle client connection."""
            logger.info("Client connected")
            emit("connected", {"message": "Connected to server"})

        @self.socketio.on("disconnect")
        def handle_disconnect() -> None:
            """Handle client disconnection."""
            logger.info("Client disconnected")

        @self.socketio.on("join")
        def handle_join(data: Dict[str, Any]) -> None:
            """Join a room (e.g., for specific chats sessions)."""
            room = data.get("room")
            if room:
                join_room(room)
                logger.info(f"Client joined room: {room}")
                emit("joined", {"room": room})

        @self.socketio.on("leave")
        def handle_leave(data: Dict[str, Any]) -> None:
            """Leave a room."""
            room = data.get("room")
            if room:
                leave_room(room)
                logger.info(f"Client left room: {room}")
                emit("left", {"room": room})

    def emit_to_room(self, room: str, event: str, data: Any) -> None:
        """
        Emit event to all clients in a room.

        Args:
            room: Room identifier
            event: Event name
            data: Data to send
        """
        self.socketio.emit(event, data, room=room)

    def emit_to_all(self, event: str, data: Any) -> None:
        """
        Emit event to all connected clients.

        Args:
            event: Event name
            data: Data to send
        """
        self.socketio.emit(event, data, broadcast=True)
