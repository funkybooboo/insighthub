"""Document status broadcasting functions."""

from typing import Any, TypedDict

from flask_socketio import SocketIO, emit
from shared.logger import create_logger

logger = create_logger(__name__)


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


def broadcast_document_status(event_data: dict, socketio: SocketIO) -> None:
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


def emit_wikipedia_fetch_status(workspace_id: int, query: str, status: str, **kwargs: Any) -> None:
    """Emit wikipedia_fetch_status event during Wikipedia fetching."""
    data = {"workspace_id": workspace_id, "query": query, "status": status, **kwargs}
    emit("wikipedia_fetch_status", data)
