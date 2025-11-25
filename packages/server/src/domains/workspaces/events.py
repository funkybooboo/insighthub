"""Workspace processing event handlers."""

from flask_socketio import SocketIO
from shared.logger import create_logger

logger = create_logger(__name__)


def handle_workspace_provision_status(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle workspace.provision_status event from provisioner worker.

    Updates workspace status in database and broadcasts via WebSocket.
    """
    try:
        workspace_id = event_data.get("workspace_id")
        user_id = event_data.get("user_id")
        status = event_data.get("status", "provisioning")
        message = event_data.get("message", "")

        if not workspace_id:
            logger.error("Missing workspace_id in provision status event")
            return

        logger.info(f"Workspace provision status: {workspace_id}, status: {status}")

        # Update workspace status in database
        try:
            # Get workspace service from app context
            from flask import g

            if hasattr(g, "app_context") and hasattr(g.app_context, "workspace_service"):
                workspace_service = g.app_context.workspace_service
                # Update workspace status
                workspace_service.update_workspace_status(
                    workspace_id=int(workspace_id), status=status, status_message=message
                )
                logger.debug(f"Updated workspace {workspace_id} status to {status}")
            else:
                logger.warning("Workspace service not available in app context")
        except Exception as db_error:
            logger.error(f"Failed to update workspace status in database: {db_error}")

        # Broadcast workspace status update via WebSocket
        status_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": status,
            "message": message,
            "timestamp": event_data.get("timestamp"),
        }

        # Emit workspace status event
        socketio.emit("workspace_status", status_data, namespace="/")
        logger.debug(f"Broadcasted workspace status update: {status_data}")

    except Exception as e:
        logger.error(f"Error handling workspace.provision_status event: {e}")


def handle_workspace_deletion_status(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle workspace.deletion_status event from deletion worker.

    Updates workspace status and broadcasts via WebSocket.
    """
    try:
        workspace_id = event_data.get("workspace_id")
        user_id = event_data.get("user_id")
        status = event_data.get("status", "deleting")
        message = event_data.get("message", "")

        if not workspace_id:
            logger.error("Missing workspace_id in deletion status event")
            return

        logger.info(f"Workspace deletion status: {workspace_id}, status: {status}")

        # Update workspace status in database
        try:
            # Get workspace service from app context
            from flask import g

            if hasattr(g, "app_context") and hasattr(g.app_context, "workspace_service"):
                workspace_service = g.app_context.workspace_service
                if status == "deleted":
                    # Actually delete the workspace when deletion is complete
                    workspace_service._repo.delete(int(workspace_id))
                    logger.info(f"Workspace {workspace_id} fully deleted")
                else:
                    # Update status for in-progress deletion
                    workspace_service._repo.update(
                        int(workspace_id), status=status, status_message=message
                    )
                    logger.debug(f"Updated workspace {workspace_id} deletion status to {status}")
            else:
                logger.warning("Workspace service not available in app context")
        except Exception as db_error:
            logger.error(f"Failed to update workspace deletion status in database: {db_error}")

        # Broadcast workspace status update via WebSocket
        status_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": status,
            "message": message,
            "timestamp": event_data.get("timestamp"),
        }

        # Emit workspace status event
        socketio.emit("workspace_status", status_data, namespace="/")
        logger.debug(f"Broadcasted workspace deletion status update: {status_data}")

    except Exception as e:
        logger.error(f"Error handling workspace.deletion_status event: {e}")
