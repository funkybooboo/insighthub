"""Socket.IO event handlers for status updates."""

import logging
from typing import TypedDict

from flask_socketio import SocketIO, emit, join_room

logger = logging.getLogger(__name__)


class SubscribeStatusData(TypedDict):
    """TypedDict for subscribe status request data."""

    user_id: int


class DocumentStatusData(TypedDict, total=False):
    """TypedDict for document status event data."""

    document_id: int
    user_id: int
    workspace_id: int | None
    status: str
    error: str | None
    message: str | None
    progress: int | None
    chunk_count: int | None
    filename: str
    timestamp: str


class WorkspaceStatusData(TypedDict, total=False):
    """TypedDict for workspace status event data."""

    workspace_id: int
    user_id: int
    status: str
    message: str | None
    error: str | None
    name: str
    timestamp: str


def handle_subscribe_status(data: SubscribeStatusData) -> None:
    """
    Handle client subscription to status updates.

    Clients join a room based on their user_id to receive real-time status updates.

    Expected data:
        {
            "user_id": int  # User ID to subscribe to status updates for
        }
    """
    user_id = data.get("user_id")
    if not user_id:
        emit("error", {"error": "user_id is required"})
        return

    room = f"user_{user_id}"
    join_room(room)
    logger.info(f"Client subscribed to status updates for user {user_id}")
    emit("subscribed", {"user_id": user_id, "room": room})


def broadcast_document_status(event_data: DocumentStatusData, socketio: SocketIO) -> None:
    """
    Broadcast document status update to clients.

    Called by RabbitMQ consumer when document status changes.

    Event data structure:
        {
            "document_id": int,
            "user_id": int,
            "workspace_id": int | None,
            "status": str,  # 'pending', 'processing', 'ready', 'failed'
            "error": str | None,
            "chunk_count": int | None,
            "filename": str,
            "metadata": dict
        }
    """
    user_id = event_data.get("user_id")
    if not user_id:
        logger.warning("document.status.updated event missing user_id")
        return

    room = f"user_{user_id}"
    socketio.emit("document_status", event_data, to=room, namespace="/")
    logger.debug(
        f"Broadcasted document status update to room {room}: document {event_data.get('document_id')}"
    )


def broadcast_workspace_status(event_data: WorkspaceStatusData, socketio: SocketIO) -> None:
    """
    Broadcast workspace status update to clients.

    Called by RabbitMQ consumer when workspace status changes.

    Event data structure:
        {
            "workspace_id": int,
            "user_id": int,
            "status": str,  # 'provisioning', 'ready', 'error'
            "message": str | None,
            "name": str,
            "metadata": dict
        }
    """
    user_id = event_data.get("user_id")
    if not user_id:
        logger.warning("workspace.status.updated event missing user_id")
        return

    room = f"user_{user_id}"
    socketio.emit("workspace_status", event_data, to=room, namespace="/")
    logger.debug(
        f"Broadcasted workspace status update to room {room}: workspace {event_data.get('workspace_id')}"
    )


def register_status_socket_handlers(socketio: SocketIO) -> None:
    """
    Register all status-related Socket.IO event handlers.

    Args:
        socketio: Flask-SocketIO instance
    """
    socketio.on_event("subscribe_status", handle_subscribe_status)
    logger.info("Registered status Socket.IO handlers")
