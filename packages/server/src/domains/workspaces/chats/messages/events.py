"""Chat message events and Socket.IO handlers."""

import uuid
from collections.abc import Mapping
from typing import TypedDict

from flask import current_app
from flask_socketio import emit

from src.infrastructure.logger import create_logger

from .exceptions import EmptyMessageError, LlmProviderError

logger = create_logger(__name__)


class ChatMessageData(TypedDict, total=False):
    """TypedDict for chats message request data."""

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
    """Socket.IO event handler for chats message operations."""

    def __init__(self) -> None:
        """Initialize the chats socket handler."""
        # Track active request IDs per client
        self._active_requests: dict[str, str] = {}

    def handle_chat_message(self, data: Mapping[str, object]) -> None:
        """
        Handle streaming chats messages via Socket.IO.

        This is the chats domain's Socket.IO event handler that orchestrates
        the streaming chats workflow using ChatService.

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
            from src.infrastructure.context import AppContext

            db = None
            request_id = str(uuid.uuid4())

            try:
                # Get database session
                db = next(self._get_db())
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
                if not user_message.strip():
                    raise EmptyMessageError()

                # Authenticate users from JWT token in message data
                token_raw = data.get("token")
                if not token_raw:
                    emit("error", {"error": "Authentication token required"})
                    return

                try:
                    from src.infrastructure.auth.token import decode_access_token

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
                if rag_type == "vector" and app_context.rag_system:
                    try:
                        rag_results = app_context.rag_system.query(
                            user_message, workspace_id=workspace_id, top_k=8
                        )
                        [result for result in rag_results if result.score > 0.1]
                    except Exception:
                        pass

                # Use async chats processing architecture
                logger.info(f"Starting async chats processing for users {user.id}")

                # Send message via chats service
                message_id = app_context.chat_service.send_message(
                    workspace_id=workspace_id,
                    session_id=session_id,
                    user_id=user.id,
                    content=user_message,
                    message_type="users",
                    ignore_rag=rag_type != "vector",
                )

                # Emit initial acknowledgment with message_id for tracking
                emit(
                    "chats.response_started",
                    {"message_id": message_id, "session_id": session_id, "request_id": request_id},
                )

                # Note: The actual streaming responses will come from the chats worker
                # via the event handlers below (handle_chat_response_chunk, etc.)
                # If no worker responds within a timeout, we could implement a fallback

            except EmptyMessageError:
                emit("error", {"error": "Message cannot be empty"})
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
            except LlmProviderError as e:
                emit("error", {"error": str(e)})
            except Exception as e:
                # Catch-all for unexpected errors
                print(f"Unexpected error in chats processing: {e}")
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
        Handle chats.response_chunk events from the chats worker.

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
        emit(
            "chats.response_chunk",
            {
                "chunk": chunk,
                "message_id": message_id,
                "session_id": session_id,
                "request_id": request_id,
            },
        )

    def handle_chat_response_complete(self, data: Mapping[str, object]) -> None:
        """
        Handle chats.response_complete events from the chats worker.

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
        emit(
            "chats.response_complete",
            {
                "session_id": session_id,
                "full_response": full_response,
                "message_id": message_id,
                "request_id": request_id,
            },
        )

    def handle_chat_no_context_found(self, data: Mapping[str, object]) -> None:
        """
        Handle chats.no_context_found events from the chats worker.

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
        emit(
            "chats.no_context_found",
            {
                "session_id": session_id,
                "query": query,
                "message_id": message_id,
                "request_id": request_id,
            },
        )

    def handle_chat_error(self, data: Mapping[str, object]) -> None:
        """
        Handle chats.error events from the chats worker.

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
        emit(
            "chats.error",
            {
                "session_id": session_id,
                "error": error,
                "message_id": message_id,
                "request_id": request_id,
            },
        )

    def handle_cancel_message(self, data: Mapping[str, object] | None = None) -> None:
        """
        Handle cancellation of streaming chats messages via Socket.IO.

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
            from src.infrastructure.context import AppContext

            db = None
            try:
                # Get database session
                db = next(self._get_db())
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
                emit("error", {"error": f"Error cancelling chats: {str(e)}"})

            finally:
                if db is not None:
                    db.close()

    def _get_db(self):
        """Get database session."""
        from src.infrastructure.database import get_db
        return get_db()


# Global instance for backwards compatibility
_chat_handler = ChatSocketHandler()


def handle_chat_message(data: Mapping[str, object]) -> None:
    """Legacy function for backwards compatibility."""
    _chat_handler.handle_chat_message(data)


def handle_cancel_message(data: Mapping[str, object] | None = None) -> None:
    """Legacy function for backwards compatibility."""
    _chat_handler.handle_cancel_message(data)


def handle_chat_response_chunk(data: Mapping[str, object]) -> None:
    """Legacy function for backwards compatibility."""
    _chat_handler.handle_chat_response_chunk(data)


def handle_chat_response_complete(data: Mapping[str, object]) -> None:
    """Legacy function for backwards compatibility."""
    _chat_handler.handle_chat_response_complete(data)


def handle_chat_no_context_found(data: Mapping[str, object]) -> None:
    """Legacy function for backwards compatibility."""
    _chat_handler.handle_chat_no_context_found(data)


def handle_chat_error(data: Mapping[str, object]) -> None:
    """Legacy function for backwards compatibility."""
    _chat_handler.handle_chat_error(data)