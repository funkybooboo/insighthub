"""Socket.IO event handlers for chat domain."""

import uuid
from typing import TYPE_CHECKING, Any

from flask import current_app
from flask_socketio import emit

from src.infrastructure.database import get_db

if TYPE_CHECKING:
    from src.context import AppContext

# Track active request IDs per client
_active_requests: dict[str, str] = {}


def handle_chat_message(data: dict[str, Any]) -> None:
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

            user_message = data.get("message", "")
            session_id = data.get("session_id")
            rag_type = data.get("rag_type", "vector")
            client_id = data.get("client_id", request_id)  # Use client_id for tracking

            # Store request ID for cancellation
            _active_requests[client_id] = request_id

            # Validate message (will raise EmptyMessageError if invalid)
            app_context.chat_service.validate_message(user_message)

            # Get user
            user = app_context.user_service.get_or_create_default_user()

            # Delegate to chat service for streaming
            for event in app_context.chat_service.stream_chat_response(
                user_id=user.id,
                message=user_message,
                llm_provider=app_context.llm_provider,
                session_id=int(session_id) if session_id else None,
                rag_type=rag_type,
                request_id=request_id,
            ):
                # Emit events based on event type
                if event.event_type == "chunk":
                    emit("chat_chunk", {"chunk": event.data["chunk"]})
                elif event.event_type == "complete":
                    emit("chat_complete", event.data)

        except Exception as e:
            emit("error", {"error": f"Error processing chat: {str(e)}"})

        finally:
            # Clean up active request tracking
            client_id = data.get("client_id", request_id)
            if client_id in _active_requests:
                del _active_requests[client_id]

            if db is not None:
                db.close()


def handle_cancel_message(data: dict[str, Any] | None = None) -> None:
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
            client_id = (data or {}).get("client_id")
            request_id = _active_requests.get(client_id) if client_id else None

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


def register_socket_handlers(socketio: Any) -> None:
    """Register Socket.IO event handlers for chat domain."""
    socketio.on_event("chat_message", handle_chat_message)
    socketio.on_event("cancel_chat", handle_cancel_chat)
