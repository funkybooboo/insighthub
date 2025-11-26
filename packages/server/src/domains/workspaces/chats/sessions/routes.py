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


def _validate_workspace_access(workspace_id: str, user_id: int) -> Response | None:
    """Validate that user has access to the workspace.

    Returns:
        Response JSON if validation fails, None if validation passes
    """
    workspace_service = g.app_context.workspace_service
    if not workspace_service.validate_workspace_access(int(workspace_id), user_id):
        return jsonify({"error": "Workspace not found"})
    return None


def _create_session_response(session, status_code: int = 200) -> tuple[Response, int]:
    """Create a standardized session response.

    Args:
        session: The session object to serialize
        status_code: HTTP status code to return

    Returns:
        Tuple of (jsonified response, status code)
    """
    response = SessionMapper.session_to_dto(session)
    return jsonify(response.to_dict()), status_code


@sessions_bp.route("", methods=["GET"])
@require_auth
def list_sessions(workspace_id: str) -> tuple[Response, int]:
    """List chats sessions for a workspace."""
    user = get_current_user()
    service = g.app_context.chat_session_service

    # Validate workspace access
    validation_error = _validate_workspace_access(workspace_id, user.id)
    if validation_error:
        return validation_error, 404

    # Parse pagination parameters
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 50))

    sessions, total = service.list_workspace_sessions(int(workspace_id), user.id, skip, limit)
    response = SessionListResponse(
        sessions=[SessionMapper.session_to_dto(s) for s in sessions],
        count=len(sessions),
        total=total,
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

    return _create_session_response(session, 201)


@sessions_bp.route("/<session_id>", methods=["GET"])
@require_auth
def get_session(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """Get a specific chats session."""
    user = get_current_user()
    service = g.app_context.chat_session_service

    # Validate workspace access
    validation_error = _validate_workspace_access(workspace_id, user.id)
    if validation_error:
        return validation_error, 404

    session = service.get_workspace_session(int(workspace_id), int(session_id), user.id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    return _create_session_response(session, 200)


@sessions_bp.route("/<session_id>", methods=["PATCH"])
@require_auth
def update_session(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """Update a chats session."""
    user = get_current_user()
    service = g.app_context.chat_session_service

    # Validate workspace access
    validation_error = _validate_workspace_access(workspace_id, user.id)
    if validation_error:
        return validation_error, 404

    # Check session ownership and workspace membership
    session = service.get_workspace_session(int(workspace_id), int(session_id), user.id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    data = request.get_json() or {}
    request_dto = UpdateSessionRequest(title=data.get("title"))

    session = service.update_session(int(session_id), title=request_dto.title)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    return _create_session_response(session, 200)


@sessions_bp.route("/<session_id>", methods=["DELETE"])
@require_auth
def delete_session(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """Delete a chats session."""
    user = get_current_user()
    service = g.app_context.chat_session_service

    # Validate workspace access
    validation_error = _validate_workspace_access(workspace_id, user.id)
    if validation_error:
        return validation_error, 404

    # Check session ownership and workspace membership
    session = service.get_workspace_session(int(workspace_id), int(session_id), user.id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    success = service.delete_session(int(session_id))
    if not success:
        return jsonify({"error": "Session not found"}), 404

    return jsonify({"message": "Session deleted successfully"}), 200
