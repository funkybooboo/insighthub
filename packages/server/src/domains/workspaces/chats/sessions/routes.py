"""Chat session routes."""

from flask import Blueprint, Response, g, jsonify, request

from src.infrastructure.auth import get_current_user, require_auth
from src.infrastructure.logger import create_logger

from .dtos import CreateSessionRequest, SessionListResponse, UpdateSessionRequest
from .mappers import SessionMapper

logger = create_logger(__name__)

sessions_bp = Blueprint(
    "chat_sessions", __name__, url_prefix="/api/workspaces/<workspace_id>/chats/sessions"
)


@sessions_bp.route("", methods=["GET"])
@require_auth
def list_sessions(workspace_id: str) -> tuple[Response, int]:
    """List chats sessions for a workspace."""
    user = get_current_user()
    service = g.app_context.chat_session_service

    sessions = service.list_workspace_sessions(int(workspace_id), user.id)
    response = SessionListResponse(
        sessions=[SessionMapper.session_to_dto(s) for s in sessions],
        count=len(sessions),
        total=len(sessions),  # TODO: Add pagination
    )

    return jsonify(response.to_dict()), 200


@sessions_bp.route("", methods=["POST"])
@require_auth
def create_session(workspace_id: str) -> tuple[Response, int]:
    """Create a new chats session."""
    user = get_current_user()
    service = g.app_context.chat_session_service

    data = request.get_json() or {}
    request_dto = CreateSessionRequest(
        title=data.get("title"),
        workspace_id=int(workspace_id),
        rag_type=data.get("rag_type", "vector"),
    )

    session = service.create_session(
        user_id=user.id,
        title=request_dto.title,
        workspace_id=request_dto.workspace_id,
        rag_type=request_dto.rag_type,
    )

    response = SessionMapper.session_to_dto(session)
    return jsonify(response.to_dict()), 201


@sessions_bp.route("/<session_id>", methods=["GET"])
@require_auth
def get_session(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """Get a specific chats session."""
    user = get_current_user()
    service = g.app_context.chat_session_service

    session = service.get_user_session(int(session_id), user.id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    response = SessionMapper.session_to_dto(session)
    return jsonify(response.to_dict()), 200


@sessions_bp.route("/<session_id>", methods=["PATCH"])
@require_auth
def update_session(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """Update a chats session."""
    user = get_current_user()
    service = g.app_context.chat_session_service

    # Check ownership
    if not service.validate_session_access(int(session_id), user.id):
        return jsonify({"error": "Session not found"}), 404

    data = request.get_json() or {}
    request_dto = UpdateSessionRequest(title=data.get("title"))

    session = service.update_session(int(session_id), title=request_dto.title)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    response = SessionMapper.session_to_dto(session)
    return jsonify(response.to_dict()), 200


@sessions_bp.route("/<session_id>", methods=["DELETE"])
@require_auth
def delete_session(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """Delete a chats session."""
    user = get_current_user()
    service = g.app_context.chat_session_service

    # Check ownership
    if not service.validate_session_access(int(session_id), user.id):
        return jsonify({"error": "Session not found"}), 404

    success = service.delete_session(int(session_id))
    if not success:
        return jsonify({"error": "Session not found"}), 404

    return jsonify({"message": "Session deleted successfully"}), 200
