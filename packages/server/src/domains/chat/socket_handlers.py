"""Socket.IO event handlers for chat domain."""

from typing import Any

from flask import current_app
from flask_socketio import emit
from src.context import AppContext
from src.infrastructure.database import get_db


def handle_chat_message(data: dict[str, Any]) -> None:
    """
    Handle streaming chat messages via Socket.IO.

    This is the chat domain's Socket.IO event handler that orchestrates
    the streaming chat workflow using ChatService.

    Expected data:
        {
            "message": "User's question",
            "session_id": "optional-session-id",
            "rag_type": "vector" (optional, defaults to vector)
        }

    Emits:
        - chat_chunk: Streamed response chunks {"chunk": str}
        - chat_complete: Final response {"session_id": int, "full_response": str}
        - error: Error information {"error": str}
    """
    with current_app.app_context():
        db = None
        try:
            # Get database session
            db = next(get_db())
            app_context = AppContext(db)

            user_message = data.get("message", "")
            session_id = data.get("session_id")
            rag_type = data.get("rag_type", "vector")

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
            ):
                # Emit events based on event type
                if event.event_type == "chunk":
                    emit("chat_chunk", {"chunk": event.data["chunk"]})
                elif event.event_type == "complete":
                    emit("chat_complete", event.data)

        except Exception as e:
            emit("error", {"error": f"Error processing chat: {str(e)}"})

        finally:
            if db is not None:
                db.close()
