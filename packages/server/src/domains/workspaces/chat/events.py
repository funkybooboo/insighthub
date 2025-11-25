"""Socket.IO event handlers for chat and status domains."""

import uuid
from collections.abc import Mapping
from typing import TypedDict

from flask import current_app
from flask_socketio import SocketIO, emit, join_room

from src.infrastructure.database import get_db
from src.infrastructure.socket.socket_handler import SocketHandler
from shared.logger import create_logger
from .dtos import StreamEvent

logger = create_logger(__name__)

class ChatMessageData(TypedDict, total=False):
    """TypedDict for chat message request data."""

    message: str
    session_id: str | int | None
    workspace_id: str | int | None
    rag_type: str
    client_id: str
    token: str


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

                workspace_id_raw = data.get("workspace_id")
                if workspace_id_raw is not None:
                    try:
                        workspace_id = int(str(workspace_id_raw))
                    except (ValueError, TypeError):
                        workspace_id = None
                else:
                    workspace_id = None

                rag_type = str(data.get("rag_type", "vector"))
                client_id = str(data.get("client_id", request_id))  # Use client_id for tracking

                # Store request ID for cancellation
                self._active_requests[client_id] = request_id

                # Validate message (will raise EmptyMessageError if invalid)
                app_context.chat_service.validate_message(user_message)

                # Authenticate user from JWT token in message data
                token_raw = data.get("token")
                if not token_raw:
                    emit("error", {"error": "Authentication token required"})
                    return

                try:
                    from src.infrastructure.auth.jwt_utils import decode_access_token
                    token = str(token_raw)
                    payload = decode_access_token(token)
                    user_id = payload.get("user_id")

                    if not user_id:
                        raise ValueError("Invalid token payload")

                    user = app_context.user_service.get_user_by_id(int(user_id))
                    if not user:
                        raise ValueError("User not found")

                except Exception as e:
                    emit("error", {"error": f"Authentication failed: {str(e)}"})
                    return

                # Validate workspace access if workspace_id is provided
                if workspace_id is not None:
                    workspace_service = app_context.workspace_service
                    if not workspace_service.validate_workspace_access(workspace_id, user.id):
                        emit("error", {"error": "No access to workspace"})
                        return

                # Check if RAG context is available before streaming
                has_rag_context = False
                if rag_type == "vector" and app_context.rag_system:
                    try:
                        rag_results = app_context.rag_system.query(user_message, workspace_id=workspace_id, top_k=8)
                        meaningful_context = [result for result in rag_results if result.score > 0.1]
                        has_rag_context = len(meaningful_context) > 0
                    except Exception:
                        has_rag_context = False

                # Use async chat processing architecture
                # Publish message to RabbitMQ and expect worker responses via WebSocket
                logger.info(f"Starting async chat processing for user {user.id}")

                # Send message via chat service (this publishes to RabbitMQ for worker processing)
                message_id = app_context.chat_service.send_message(
                    workspace_id=workspace_id,
                    session_id=session_id,
                    user_id=user.id,
                    content=user_message,
                    message_type="user",
                    ignore_rag=rag_type != "vector"
                )

                # Emit initial acknowledgment with message_id for tracking
                emit("chat.response_started", {
                    "message_id": message_id,
                    "session_id": session_id,
                    "request_id": request_id
                })

                # Note: The actual streaming responses will come from the chat worker
                # via the event handlers below (handle_chat_response_chunk, etc.)
                # If no worker responds within a timeout, we could implement a fallback

            except ValueError as e:
                # Invalid input data
                emit("error", {"error": f"Invalid input: {str(e)}"})
            except PermissionError as e:
                # Authentication/authorization issues
                emit("error", {"error": f"Access denied: {str(e)}"})
            except ConnectionError as e:
                # Database or external service connection issues
                emit("error", {"error": f"Service unavailable: {str(e)}"})
            except TimeoutError as e:
                # Operation timed out
                emit("error", {"error": f"Request timed out: {str(e)}"})
            except Exception as e:
                # Catch-all for unexpected errors
                print(f"Unexpected error in chat processing: {e}")
                emit("error", {"error": "An unexpected error occurred"})

            finally:
                # Clean up active request tracking
                client_id = str(data.get("client_id", request_id))
                if client_id in self._active_requests:
                    del self._active_requests[client_id]

                if db is not None:
                    db.close()


    def handle_chat_response_chunk(self, data: Mapping[str, object]) -> None:
        """
        Handle chat.response_chunk events from the chat worker.

        Expected data:
            {
                "session_id": int,
                "message_id": str,
                "request_id": str,
                "chunk": str
            }
        """
        session_id = data.get("session_id")
        message_id = data.get("message_id")
        request_id = data.get("request_id")
        chunk = data.get("chunk", "")

        # Emit to the client
        emit("chat.response_chunk", {
            "chunk": chunk,
            "message_id": message_id,
            "session_id": session_id,
            "request_id": request_id
        })

    def handle_chat_response_complete(self, data: Mapping[str, object]) -> None:
        """
        Handle chat.response_complete events from the chat worker.

        Expected data:
            {
                "session_id": int,
                "message_id": str,
                "request_id": str,
                "full_response": str
            }
        """
        session_id = data.get("session_id")
        message_id = data.get("message_id")
        request_id = data.get("request_id")
        full_response = data.get("full_response", "")

        # Emit to the client
        emit("chat.response_complete", {
            "session_id": session_id,
            "full_response": full_response,
            "message_id": message_id,
            "request_id": request_id
        })

    def handle_chat_no_context_found(self, data: Mapping[str, object]) -> None:
        """
        Handle chat.no_context_found events from the chat worker.

        Expected data:
            {
                "session_id": int,
                "message_id": str,
                "request_id": str,
                "query": str
            }
        """
        session_id = data.get("session_id")
        message_id = data.get("message_id")
        request_id = data.get("request_id")
        query = data.get("query", "")

        # Emit to the client
        emit("chat.no_context_found", {
            "session_id": session_id,
            "query": query,
            "message_id": message_id,
            "request_id": request_id
        })

    def handle_chat_error(self, data: Mapping[str, object]) -> None:
        """
        Handle chat.error events from the chat worker.

        Expected data:
            {
                "session_id": int,
                "message_id": str,
                "request_id": str,
                "error": str
            }
        """
        session_id = data.get("session_id")
        message_id = data.get("message_id")
        request_id = data.get("request_id")
        error = data.get("error", "Unknown error")

        # Emit to the client
        emit("chat.error", {
            "session_id": session_id,
            "error": error,
            "message_id": message_id,
            "request_id": request_id
        })

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

        # Register async chat event handlers (from chat worker)
        handler.register_event("chat_response_chunk", self.handle_chat_response_chunk)
        handler.register_event("chat_response_complete", self.handle_chat_response_complete)
        handler.register_event("chat_no_context_found", self.handle_chat_no_context_found)
        handler.register_event("chat_error", self.handle_chat_error)


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
