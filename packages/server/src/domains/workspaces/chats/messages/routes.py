"""Chat message routes."""

from flask import Blueprint, Response, g, jsonify, request

from src.infrastructure.auth import get_current_user, require_auth
from src.infrastructure.logger import create_logger

from .dtos import CreateMessageRequest, MessageListResponse
from .mappers import MessageMapper

logger = create_logger(__name__)

messages_bp = Blueprint(
    "chat_messages",
    __name__,
    url_prefix="/api/workspaces/<workspace_id>/chats/sessions/<session_id>/messages",
)


@messages_bp.route("", methods=["GET"])
@require_auth
def list_messages(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """List messages for a chats session."""
    user = get_current_user()
    service = g.app_context.chat_message_service

    # Parse pagination parameters
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 50))

    # Validate workspace and session access
    message_service = g.app_context.chat_message_service
    if not message_service.validate_workspace_and_session_access(
        int(workspace_id), int(session_id), user.id
    ):
        return jsonify({"error": "Access denied"}), 403

    messages, total = service.get_session_messages(int(session_id), skip, limit)
    response = MessageListResponse(
        messages=[MessageMapper.message_to_dto(msg) for msg in messages],
        count=len(messages),
        total=total,
    )

    return jsonify(response.to_dict()), 200


@messages_bp.route("", methods=["POST"])
@require_auth
def create_message(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """Create a new message in a chats session."""
    user = get_current_user()

    # Validate workspace and session access
    message_service = g.app_context.chat_message_service
    if not message_service.validate_workspace_and_session_access(
        int(workspace_id), int(session_id), user.id
    ):
        return jsonify({"error": "Access denied"}), 403

    service = g.app_context.chat_message_service

    data = request.get_json() or {}
    request_dto = CreateMessageRequest(
        content=data.get("content", ""),
        role=data.get("role", "users"),
    )

    message = service.create_message(
        session_id=int(session_id),
        role=request_dto.role,
        content=request_dto.content,
    )

    # Launch ChatQueryWorker for user messages (triggers RAG query and LLM response)
    if request_dto.role == "user":
        from src.workers import get_chat_query_worker

        query_worker = get_chat_query_worker()
        query_worker.process_query(
            session_id=int(session_id),
            workspace_id=int(workspace_id),
            query_text=request_dto.content,
            user_id=user.id,
        )

    response = MessageMapper.message_to_dto(message)
    return jsonify(response.to_dict()), 201


@messages_bp.route("/<message_id>", methods=["GET"])
@require_auth
def get_message(workspace_id: str, session_id: str, message_id: str) -> tuple[Response, int]:
    """Get a specific message."""
    user = get_current_user()

    # Validate workspace and session access
    message_service = g.app_context.chat_message_service
    if not message_service.validate_workspace_and_session_access(
        int(workspace_id), int(session_id), user.id
    ):
        return jsonify({"error": "Access denied"}), 403

    # Validate message access
    message_service = g.app_context.chat_message_service
    if not message_service.validate_message_access(int(message_id), int(session_id), user.id):
        return jsonify({"error": "Message not found"}), 404

    service = g.app_context.chat_message_service
    message = service.get_message(int(message_id))

    response = MessageMapper.message_to_dto(message)
    return jsonify(response.to_dict()), 200


@messages_bp.route("/<message_id>", methods=["DELETE"])
@require_auth
def delete_message(workspace_id: str, session_id: str, message_id: str) -> tuple[Response, int]:
    """Delete a message."""
    user = get_current_user()

    # Validate workspace and session access
    message_service = g.app_context.chat_message_service
    if not message_service.validate_workspace_and_session_access(
        int(workspace_id), int(session_id), user.id
    ):
        return jsonify({"error": "Access denied"}), 403

    # Validate message access
    message_service = g.app_context.chat_message_service
    if not message_service.validate_message_access(int(message_id), int(session_id), user.id):
        return jsonify({"error": "Message not found"}), 404

    service = g.app_context.chat_message_service
    success = service.delete_message(int(message_id))
    if not success:
        return jsonify({"error": "Message not found"}), 404

    return jsonify({"message": "Message deleted successfully"}), 200


@messages_bp.route("/cancel", methods=["POST"])
@require_auth
def cancel_message_streaming(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """Cancel message streaming for a chats session."""
    user = get_current_user()

    # Validate workspace and session access
    message_service = g.app_context.chat_message_service
    if not message_service.validate_workspace_and_session_access(
        int(workspace_id), int(session_id), user.id
    ):
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json() or {}
    message_id = data.get("message_id")

    # TODO: Implement actual cancellation logic
    # For now, just return success
    logger.info(f"Cancelling message streaming for session {session_id}, message {message_id}")

    return jsonify({"message": "Message streaming cancelled successfully"}), 200
