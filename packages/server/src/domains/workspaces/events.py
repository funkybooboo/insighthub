"""Workspace-specific event handlers and broadcasting functions."""

from flask_socketio import SocketIO

from src.infrastructure.events.events import broadcast_workspace_status
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def handle_workspace_status_update(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle workspace status update events.

    This is called when workspace operation status changes.
    """
    try:
        # Broadcast the status update via WebSocket
        broadcast_workspace_status(event_data, socketio)

        # Log the status change
        workspace_id = event_data.get("workspace_id")
        status = event_data.get("status")
        operation = event_data.get("operation", "unknown")
        logger.info(f"Workspace {workspace_id} {operation} status updated to: {status}")

    except Exception as e:
        logger.error(f"Failed to handle workspace status update: {e}")


def handle_workspace_operation_complete(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle workspace operation completion events.

    Called when a workspace operation (create/delete/update) finishes.
    """
    try:
        workspace_id = event_data.get("workspace_id")
        operation = event_data.get("operation", "unknown")
        status = event_data.get("status")

        if status == "ready":
            logger.info(f"Workspace {workspace_id} {operation} completed successfully")
        elif status == "failed":
            error = event_data.get("error", "Unknown error")
            logger.error(f"Workspace {workspace_id} {operation} failed: {error}")
        else:
            logger.info(f"Workspace {workspace_id} {operation} status: {status}")

        # Broadcast the completion event
        broadcast_workspace_status(event_data, socketio)

    except Exception as e:
        logger.error(f"Failed to handle workspace operation completion: {e}")


# Event handler mappings for automatic registration
WORKSPACE_EVENT_HANDLERS = {
    "workspace.status.updated": handle_workspace_status_update,
    "workspace.operation.complete": handle_workspace_operation_complete,
}
