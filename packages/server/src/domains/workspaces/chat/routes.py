"""Workspace-scoped chat routes."""

from flask import Blueprint, Response, g, jsonify, request

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

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Create chat session via service
        chat_service = g.app_context.chat_service
        session = chat_service.create_session(
            user_id=user.id,
            workspace_id=int(workspace_id),
            title=title.strip() if title else None,
            rag_type="vector",  # Default to vector RAG
        )

        return jsonify({"session_id": session.id, "title": session.title or "New Chat"}), 201

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

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Get sessions via service
        chat_service = g.app_context.chat_service
        sessions = chat_service.list_workspace_sessions(
            workspace_id=int(workspace_id), skip=offset, limit=limit
        )

        # Convert to response format
        result = []
        for session in sessions:
            message_count = chat_service.list_session_messages(session.id).__len__()
            result.append(
                {
                    "session_id": session.id,
                    "title": session.title or "Untitled Chat",
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "message_count": message_count,
                }
            )

        return jsonify(result), 200

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

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Delete session via service
        chat_service = g.app_context.chat_service
        success = chat_service.delete_session(int(session_id))

        if not success:
            return jsonify({"error": "Chat session not found"}), 404

        return jsonify({"message": "Chat session deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to delete chat session: {str(e)}"}), 500


@chat_bp.route("/<workspace_id>/chat/sessions/<session_id>", methods=["GET"])
@require_auth
def get_chat_session(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """
    Get a specific chat session from a workspace.

    Returns:
        200: {
            "session_id": int,
            "title": "string",
            "rag_type": "string",
            "created_at": "string",
            "updated_at": "string",
            "message_count": int
        }
        403: {"error": "string"} - No access to workspace/session
        404: {"error": "string"} - Session not found
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Get session via service
        chat_service = g.app_context.chat_service
        session = chat_service.get_session_by_id(int(session_id))

        if not session:
            return jsonify({"error": "Chat session not found"}), 404

        # Verify session belongs to workspace
        if session.workspace_id != int(workspace_id):
            return jsonify({"error": "Chat session not found in this workspace"}), 404

        # Get message count
        message_count = chat_service.list_session_messages(session.id).__len__()

        return (
            jsonify(
                {
                    "session_id": session.id,
                    "title": session.title or "Untitled Chat",
                    "rag_type": session.rag_type,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "message_count": message_count,
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to get chat session: {str(e)}"}), 500


@chat_bp.route("/<workspace_id>/chat/sessions/<session_id>", methods=["PATCH"])
@require_auth
def update_chat_session(workspace_id: str, session_id: str) -> tuple[Response, int]:
    """
    Update a chat session in a workspace.

    Request Body:
        {
            "title": "New session title"  // optional
        }

    Returns:
        200: {
            "session_id": int,
            "title": "string",
            "rag_type": "string",
            "created_at": "string",
            "updated_at": "string"
        }
        400: {"error": "string"} - Invalid request data
        403: {"error": "string"} - No access to workspace/session
        404: {"error": "string"} - Session not found
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()
        data = request.get_json() or {}

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Validate request data
        title = data.get("title")
        if title is not None:
            title = title.strip()
            if not title:
                return jsonify({"error": "Title cannot be empty"}), 400
            if len(title) > 200:
                return jsonify({"error": "Title must be 200 characters or less"}), 400

        # Get current session to verify ownership
        chat_service = g.app_context.chat_service
        session = chat_service.get_session_by_id(int(session_id))

        if not session:
            return jsonify({"error": "Chat session not found"}), 404

        # Verify session belongs to workspace
        if session.workspace_id != int(workspace_id):
            return jsonify({"error": "Chat session not found in this workspace"}), 404

        # Update session
        update_data = {}
        if title is not None:
            update_data["title"] = title

        if update_data:
            updated_session = chat_service.update_session(session.id, **update_data)
            if not updated_session:
                return jsonify({"error": "Failed to update chat session"}), 500
            session = updated_session

        return (
            jsonify(
                {
                    "session_id": session.id,
                    "title": session.title or "Untitled Chat",
                    "rag_type": session.rag_type,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update chat session: {str(e)}"}), 500


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

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Send message via service
        chat_service = g.app_context.chat_service
        message_id = chat_service.send_message(
            workspace_id=int(workspace_id),
            session_id=int(session_id),
            user_id=user.id,
            content=content,
            message_type=message_type,
            ignore_rag=ignore_rag,
        )

        return jsonify({"message_id": message_id}), 200

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

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Cancel message via service
        chat_service = g.app_context.chat_service
        chat_service.cancel_message(
            workspace_id=int(workspace_id),
            session_id=int(session_id),
            user_id=user.id,
            message_id=message_id,
        )

        return jsonify({"message": "Message cancelled successfully"}), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to cancel message: {str(e)}"}), 500
