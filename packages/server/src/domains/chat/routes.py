"""Chat routes."""

from flask import Blueprint, Response, g, jsonify, request

from src.infrastructure.auth import get_current_user, require_auth
from packages.shared.python.src.shared.errors import ValidationError

chat_bp = Blueprint("chat", __name__, url_prefix="/api")


@chat_bp.route("/chat", methods=["POST"])
@require_auth
def chat() -> tuple[Response, int]:
    """
    Handle chat messages and return responses from the RAG system.

    Expected JSON payload:
        {
            "message": "User's question",
            "session_id": "optional-session-id",
            "rag_type": "vector" (optional, defaults to vector)
        }

    Returns:
        JSON response with answer and relevant context

    Raises:
        EmptyMessageError: If message is empty
    """

    data = request.get_json()

    if not data or "message" not in data:
        raise ValidationError("No message provided")

    user_message = data["message"]
    session_id = data.get("session_id")
    rag_type = data.get("rag_type", "vector")

    # Get authenticated user
    user = get_current_user()

    # Get document count for response
    documents = g.app_context.document_service.list_user_documents(user.id)

    # Use service method that handles the full workflow and returns DTO
    response_dto = g.app_context.chat_service.process_chat_message_with_llm(
        user_id=user.id,
        message=user_message,
        llm_provider=g.app_context.llm_provider,
        session_id=int(session_id) if session_id else None,
        rag_type=rag_type,
        documents_count=len(documents),
    )

    return jsonify(response_dto.to_dict()), 200


@chat_bp.route("/sessions", methods=["GET"])
@require_auth
def list_sessions() -> tuple[Response, int]:
    """
    List all chat sessions for the current user.

    Returns:
        JSON response with list of chat sessions
    """
    user = get_current_user()

    # Use service method that returns DTO
    response_dto = g.app_context.chat_service.list_user_sessions_as_dto(user.id)

    return jsonify(response_dto.to_dict()), 200


@chat_bp.route("/sessions/<int:session_id>/messages", methods=["GET"])
@require_auth
def get_session_messages(session_id: int) -> tuple[Response, int]:
    """
    Get all messages for a specific chat session.

    Args:
        session_id: The chat session ID

    Returns:
        JSON response with list of messages
    """
    # Use service method that returns DTO
    response_dto = g.app_context.chat_service.list_session_messages_as_dto(session_id)

    return jsonify(response_dto.to_dict()), 200
