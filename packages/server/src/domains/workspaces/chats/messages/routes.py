"""Chat message routes."""

from flask import Blueprint, Response, g, jsonify, request

from src.infrastructure.auth import get_current_user, require_auth
from src.infrastructure.logger import create_logger

from .dtos import CreateMessageRequest, MessageListResponse, MessageResponse
from .mappers import MessageMapper

logger = create_logger(__name__)

messages_bp = Blueprint("chat_messages", __name__, url_prefix="/api/workspaces/<workspace_id>/chats/sessions/<session_id>/messages")


@messages_bp.route("", methods=["GET"])
@require_auth
def list_messages(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """List messages for a chats session."""
    user = get_current_user()
    service = g.app_context.chat_message_service

    # TODO: Validate session access
    messages = service.get_session_messages(int(session_id))
    response = MessageListResponse(
        messages=[MessageMapper.message_to_dto(msg) for msg in messages],
        count=len(messages),
        total=len(messages),  # TODO: Add pagination
    )

    return jsonify(response.to_dict()), 200


@messages_bp.route("", methods=["POST"])
@require_auth
def create_message(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """Create a new message in a chats session."""
    user = get_current_user()
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

    # TODO: Launch ChatQueryWorker (if role is 'users')
    # Worker should:
    # 1. Get workspace RAG configuration
    # 2. Execute QueryWorkflow to retrieve relevant context
    # 3. Generate LLM response with context
    # 4. Stream response to client via WebSocket
    # 5. Save assistant message to database
    #
    # Example implementation:
    #    if request_dto.role == "users":
    #        from src.workers import get_chat_query_worker
    #        query_worker = get_chat_query_worker()
    #        query_worker.process_query(
    #            session_id=int(session_id),
    #            workspace_id=int(workspace_id),
    #            query_text=request_dto.content,
    #            user_id=user.id
    #        )

    response = MessageMapper.message_to_dto(message)
    return jsonify(response.to_dict()), 201


@messages_bp.route("/<message_id>", methods=["GET"])
@require_auth
def get_message(workspace_id: str, session_id: str, message_id: str) -> tuple[Response, int]:
    """Get a specific message."""
    user = get_current_user()
    service = g.app_context.chat_message_service

    message = service.get_message(int(message_id))
    if not message or message.session_id != int(session_id):
        return jsonify({"error": "Message not found"}), 404

    response = MessageMapper.message_to_dto(message)
    return jsonify(response.to_dict()), 200


@messages_bp.route("/<message_id>", methods=["DELETE"])
@require_auth
def delete_message(workspace_id: str, session_id: str, message_id: str) -> tuple[Response, int]:
    """Delete a message."""
    user = get_current_user()
    service = g.app_context.chat_message_service

    # TODO: Validate session access
    success = service.delete_message(int(message_id))
    if not success:
        return jsonify({"error": "Message not found"}), 404

    return jsonify({"message": "Message deleted successfully"}), 200