"""Chat-specific event handlers and broadcasting functions."""

from flask_socketio import SocketIO

from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


def handle_chat_message_created(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle chat message creation events.

    Called when a new chat message is created.
    """
    try:
        message_id = event_data.get("message_id")
        session_id = event_data.get("session_id")
        role = event_data.get("role")

        logger.info(f"Chat message created: {message_id} in session {session_id} (role: {role})")

        # Broadcast to user's room
        user_id = event_data.get("user_id")
        if user_id:
            room = f"user_{user_id}"
            socketio.emit("chat.message.created", event_data, to=room, namespace="/")

    except Exception as e:
        logger.error(f"Failed to handle chat message creation: {e}")


def handle_chat_response_chunk(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle chat response streaming chunk events.

    Called for each chunk of streaming LLM response.
    """
    try:
        session_id = event_data.get("session_id")
        chunk = event_data.get("chunk", "")
        is_complete = event_data.get("is_complete", False)

        # Broadcast to user's room
        user_id = event_data.get("user_id")
        if user_id:
            room = f"user_{user_id}"
            socketio.emit("chat.response.chunk", event_data, to=room, namespace="/")

            if is_complete:
                logger.info(f"Chat response completed for session {session_id}")
            elif len(chunk) > 0:
                logger.debug(f"Chat response chunk sent for session {session_id}: {len(chunk)} chars")

    except Exception as e:
        logger.error(f"Failed to handle chat response chunk: {e}")


def handle_chat_response_complete(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle chat response completion events.

    Called when the full LLM response is ready.
    """
    try:
        session_id = event_data.get("session_id")
        total_tokens = event_data.get("total_tokens", 0)

        logger.info(f"Chat response completed for session {session_id} ({total_tokens} tokens)")

        # Broadcast to user's room
        user_id = event_data.get("user_id")
        if user_id:
            room = f"user_{user_id}"
            socketio.emit("chat.response.complete", event_data, to=room, namespace="/")

    except Exception as e:
        logger.error(f"Failed to handle chat response completion: {e}")


def handle_chat_error(event_data: dict, socketio: SocketIO) -> None:
    """
    Handle chat error events.

    Called when chat processing encounters an error.
    """
    try:
        session_id = event_data.get("session_id")
        error = event_data.get("error", "Unknown error")

        logger.error(f"Chat error in session {session_id}: {error}")

        # Broadcast to user's room
        user_id = event_data.get("user_id")
        if user_id:
            room = f"user_{user_id}"
            socketio.emit("chat.error", event_data, to=room, namespace="/")

    except Exception as e:
        logger.error(f"Failed to handle chat error: {e}")


# Event handler mappings for automatic registration
CHAT_EVENT_HANDLERS = {
    "chat.message.created": handle_chat_message_created,
    "chat.response.stream": handle_chat_response_chunk,
    "chat.response.complete": handle_chat_response_complete,
    "chat.error": handle_chat_error,
}