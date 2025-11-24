"""Workspace-scoped chat routes."""

from flask import Blueprint, Response, g, jsonify, request
from shared.exceptions import ValidationError

from src.infrastructure.auth import get_current_user, require_auth

chat_bp = Blueprint("chat", __name__, url_prefix="/api/workspaces")


@chat_bp.route("/<workspace_id>/chat/sessions", methods=["POST"])
@require_auth
def create_chat_session(workspace_id: str) -> tuple[Response, int]:
    """
    Create a new chat session for a workspace.

    Request Body:
        {
            "title": "Optional session title"
        }

    Returns:
        201: {
            "session_id": int,
            "title": "string"
        }
        400: {"error": "string"} - Invalid request
        403: {"error": "string"} - No access to workspace
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()
        data = request.get_json() or {}
        title = data.get("title")

        # Validate title if provided
        if title and (len(title.strip()) == 0 or len(title) > 200):
            return jsonify({"error": "Title must be 1-200 characters"}), 400

        # TODO: Validate workspace access
        # TODO: Create chat session via service
        # session = g.app_context.chat_service.create_session(
        #     workspace_id=int(workspace_id),
        #     user_id=user.id,
        #     title=title.strip() if title else None
        # )

        # Mock response for now
        return jsonify({
            "session_id": 1,
            "title": title or "New Chat"
        }), 201

    except ValueError as e:
        return jsonify({"error": f"Invalid workspace ID: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create chat session: {str(e)}"}), 500


@chat_bp.route("/<workspace_id>/chat/sessions", methods=["GET"])
@require_auth
def list_chat_sessions(workspace_id: str) -> tuple[Response, int]:
    """
    List all chat sessions for a workspace.

    Query Parameters:
        - limit: int (default: 50, max: 100)
        - offset: int (default: 0)

    Returns:
        200: [
            {
                "session_id": int,
                "title": "string",
                "created_at": "string",
                "updated_at": "string",
                "message_count": int
            }
        ]
        403: {"error": "string"} - No access to workspace
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()

        # Parse query parameters
        limit = min(int(request.args.get("limit", 50)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)

        # TODO: Validate workspace access
        # TODO: Get sessions via service
        # sessions = g.app_context.chat_service.list_workspace_sessions(
        #     workspace_id=int(workspace_id),
        #     user_id=user.id,
        #     limit=limit,
        #     offset=offset
        # )

        # Mock response for now
        return jsonify([
            {
                "session_id": 1,
                "title": "Sample Chat Session",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "message_count": 0
            }
        ]), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid workspace ID: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to list chat sessions: {str(e)}"}), 500


@chat_bp.route("/<workspace_id>/chat/sessions/<session_id>", methods=["DELETE"])
@require_auth
def delete_chat_session(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """
    Delete a chat session from a workspace.

    Returns:
        200: {"message": "Chat session deleted successfully"}
        403: {"error": "string"} - No access to workspace/session
        404: {"error": "string"} - Session not found
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()

        # TODO: Validate workspace and session access
        # TODO: Delete session via service
        # g.app_context.chat_service.delete_session(
        #     session_id=int(session_id),
        #     workspace_id=int(workspace_id),
        #     user_id=user.id
        # )

        return jsonify({"message": "Chat session deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to delete chat session: {str(e)}"}), 500


@chat_bp.route("/<workspace_id>/chat/sessions/<session_id>/messages", methods=["POST"])
@require_auth
def send_chat_message(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """
    Send a chat message to a workspace session.

    Request Body:
        {
            "content": "User message",
            "message_type": "user",  // "user" or "system"
            "ignore_rag": false     // Skip RAG processing
        }

    Returns:
        200: {"message_id": "string"}
        400: {"error": "string"} - Invalid request
        403: {"error": "string"} - No access to workspace/session
        404: {"error": "string"} - Session not found
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        content = data.get("content", "").strip()
        if not content:
            return jsonify({"error": "Message content cannot be empty"}), 400

        if len(content) > 10000:  # Reasonable limit
            return jsonify({"error": "Message content too long (max 10000 characters)"}), 400

        message_type = data.get("message_type", "user")
        if message_type not in ["user", "system"]:
            return jsonify({"error": "message_type must be 'user' or 'system'"}), 400

        ignore_rag = bool(data.get("ignore_rag", False))

        # TODO: Validate workspace and session access
        # TODO: Send message via service with RAG processing
        # message_id = g.app_context.chat_service.send_message(
        #     workspace_id=int(workspace_id),
        #     session_id=int(session_id),
        #     user_id=user.id,
        #     content=content,
        #     message_type=message_type,
        #     ignore_rag=ignore_rag
        # )

        # Mock response for now
        return jsonify({"message_id": f"msg-{session_id}-123"}), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to send message: {str(e)}"}), 500


@chat_bp.route("/<workspace_id>/chat/sessions/<session_id>/cancel", methods=["POST"])
@require_auth
def cancel_chat_message(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """
    Cancel a streaming chat message.

    Request Body:
        {
            "message_id": "optional-message-id"
        }

    Returns:
        200: {"message": "Message cancelled successfully"}
        400: {"error": "string"} - Invalid request
        403: {"error": "string"} - No access to workspace/session
        404: {"error": "string"} - No active message to cancel
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()
        data = request.get_json() or {}
        message_id = data.get("message_id")

        # TODO: Validate workspace and session access
        # TODO: Cancel message via service
        # g.app_context.chat_service.cancel_message(
        #     workspace_id=int(workspace_id),
        #     session_id=int(session_id),
        #     user_id=user.id,
        #     message_id=message_id
        # )

        return jsonify({"message": "Message cancelled successfully"}), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to cancel message: {str(e)}"}), 500
