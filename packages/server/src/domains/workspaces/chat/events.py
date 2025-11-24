"""Socket.IO event handlers for chat and status domains."""

import uuid
from collections.abc import Mapping
from typing import TypedDict

from flask import current_app
from flask_socketio import SocketIO, emit, join_room

from src.infrastructure.database import get_db
from src.infrastructure.socket.socket_handler import SocketHandler
from shared.logger import create_logger

logger = create_logger(__name__)

class ChatMessageData(TypedDict, total=False):
    """TypedDict for chat message request data."""

    message: str
    session_id: str | int | None
    rag_type: str
    client_id: str


class CancelMessageData(TypedDict, total=False):
    """TypedDict for cancel message request data."""

    client_id: str


class ChatSocketHandler:
    """Socket.IO event handler for chat domain operations."""

    def __init__(self) -> None:
        """Initialize the chat socket handler."""
        # Track active request IDs per client
        self._active_requests: dict[str, str] = {}


    def handle_chat_message(self, data: Mapping[str, object]) -> None:
        """
        Handle streaming chat messages via Socket.IO.

        This is the chat domain's Socket.IO event handler that orchestrates
        the streaming chat workflow using ChatService.

        Expected data:
            {
                "message": "User's question",
                "session_id": "optional-session-id",
                "rag_type": "vector" (optional, defaults to vector),
                "client_id": "unique-client-id" (for cancellation tracking)
            }

        Emits:
            - chat_chunk: Streamed response chunks {"chunk": str}
            - chat_complete: Final response {"session_id": int, "full_response": str}
            - error: Error information {"error": str}
        """
        with current_app.app_context():
            # Import here to avoid circular dependency
            from src.context import AppContext

            db = None
            request_id = str(uuid.uuid4())

            try:
                # Get database session
                db = next(get_db())
                app_context = AppContext(db)

                user_message = str(data.get("message", ""))
                session_id_raw = data.get("session_id")
                if session_id_raw is not None:
                    try:
                        session_id = int(str(session_id_raw))
                    except (ValueError, TypeError):
                        session_id = None
                else:
                    session_id = None
                rag_type = str(data.get("rag_type", "vector"))
                client_id = str(data.get("client_id", request_id))  # Use client_id for tracking

                # Store request ID for cancellation
                self._active_requests[client_id] = request_id

                # Validate message (will raise EmptyMessageError if invalid)
                app_context.chat_service.validate_message(user_message)

                # Get user
                user = app_context.user_service.get_or_create_default_user()

                # Delegate to chat service for streaming
                for event in app_context.chat_service.stream_chat_response(
                    user_id=user.id,
                    message=user_message,
                    llm_provider=app_context.llm_provider,
                    session_id=session_id,
                    rag_type=rag_type,
                    request_id=request_id,
                ):
                    # Emit events based on event type
                    if event.event_type == "chunk":
                        emit("chat_chunk", {"chunk": event.data["chunk"]})
                        # Also emit the new chat.response_chunk event that client expects
                        emit("chat.response_chunk", {"chunk": event.data["chunk"], "message_id": request_id})
                    elif event.event_type == "complete":
                        emit("chat_complete", event.data)

            except Exception as e:
                emit("error", {"error": f"Error processing chat: {str(e)}"})

            finally:
                # Clean up active request tracking
                client_id = str(data.get("client_id", request_id))
                if client_id in self._active_requests:
                    del self._active_requests[client_id]

                if db is not None:
                    db.close()


    def handle_cancel_message(self, data: Mapping[str, object] | None = None) -> None:
        """
        Handle cancellation of streaming chat messages via Socket.IO.

        This handler allows clients to cancel an ongoing streaming response.

        Expected data:
            {
                "client_id": "unique-client-id" (same as used in chat_message)
            }

        Emits:
            - chat_cancelled: Confirmation that the stream was cancelled
        """
        with current_app.app_context():
            # Import here to avoid circular dependency
            from src.context import AppContext

            db = None
            try:
                # Get database session
                db = next(get_db())
                app_context = AppContext(db)

                # Look up the active request ID for this client
                client_id = str((data or {}).get("client_id", "")) if data else None
                request_id = self._active_requests.get(client_id) if client_id else None

                if request_id:
                    # Cancel the streaming request
                    app_context.chat_service.cancel_stream(request_id)
                    emit("chat_cancelled", {"status": "cancelled"})
                else:
                    # No active request to cancel (might have already completed)
                    emit("chat_cancelled", {"status": "no_active_request"})

            except Exception as e:
                emit("error", {"error": f"Error cancelling chat: {str(e)}"})

            finally:
                if db is not None:
                    db.close()

    def emit_chat_no_context_found(self, session_id: int, query: str) -> None:
        """Emit chat.no_context_found event when RAG finds no relevant context."""
        emit("chat.no_context_found", {"session_id": session_id, "query": query})

    def register_handlers(self, socketio: SocketIO) -> None:
        """Register Socket.IO event handlers for chat domain."""
        handler = SocketHandler(socketio)
        handler.register_event("chat_message", self.handle_chat_message)
        handler.register_event("cancel_message", self.handle_cancel_message)


def handle_connect() -> None:
    """Handle client connection."""
    emit("connected")


def handle_disconnect() -> None:
    """Handle client disconnection."""
    # Client handles disconnect event, no need to emit anything special
    pass


# Global instance for backwards compatibility
_chat_handler = ChatSocketHandler()


def handle_chat_message(data: Mapping[str, object]) -> None:
    """Legacy function for backwards compatibility."""
    _chat_handler.handle_chat_message(data)


def handle_cancel_message(data: Mapping[str, object] | None = None) -> None:
    """Legacy function for backwards compatibility."""
    _chat_handler.handle_cancel_message(data)


def emit_chat_no_context_found(session_id: int, query: str) -> None:
    """Legacy function for backwards compatibility."""
    _chat_handler.emit_chat_no_context_found(session_id, query)


def register_socket_handlers(socketio: SocketIO) -> None:
    """Register Socket.IO event handlers for chat domain."""
    _chat_handler.register_handlers(socketio)


# Status-related socket handlers (moved from status/socket_handlers.py)

class SubscribeStatusData(TypedDict):
    """TypedDict for subscribe status request data."""

    user_id: int


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
    from src.infrastructure.socket.socket_handler import SocketHandler
    handler = SocketHandler(socketio)
    handler.register_event("subscribe_status", handle_subscribe_status)
    logger.info("Registered status Socket.IO handlers")
