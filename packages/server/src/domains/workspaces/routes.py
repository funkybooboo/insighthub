"""Workspace API endpoints for InsightHub."""

from typing import TypedDict

from flask import Blueprint, Response, g, jsonify, request
from shared.models import User
from shared.models.workspace import Workspace

from src.domains.workspaces.service import WorkspaceService
from src.infrastructure.auth import get_current_user, require_auth

workspace_bp = Blueprint("workspaces", __name__, url_prefix="/api/workspaces")


def get_workspace_service() -> WorkspaceService:
    """Get workspace service from app context."""
    return g.app_context.workspace_service


class WorkspaceDict(TypedDict, total=False):
    """TypedDict for workspace response."""

    id: int
    name: str
    description: str | None
    user_id: int
    is_active: bool
    status: str
    status_message: str | None
    created_at: str
    updated_at: str
    document_count: int
    session_count: int
    rag_config: dict


def workspace_to_dict(workspace: Workspace, include_rag_config: bool = False) -> WorkspaceDict:
    """Convert workspace model to dict for JSON response."""
    result = {
        "id": workspace.id,
        "name": workspace.name,
        "description": workspace.description,
        "user_id": workspace.user_id,
        "is_active": workspace.is_active,
        "status": workspace.status,
        "status_message": workspace.status_message,
        "created_at": workspace.created_at.isoformat(),
        "updated_at": workspace.updated_at.isoformat(),
    }

    if include_rag_config:
        service = get_workspace_service()
        rag_config = service._repo.get_rag_config(workspace.id)
        if rag_config:
            result["rag_config"] = {
                "id": rag_config.id,
                "embedding_model": rag_config.embedding_model,
                "embedding_dim": rag_config.embedding_dim,
                "retriever_type": rag_config.retriever_type,
                "chunk_size": rag_config.chunk_size,
                "chunk_overlap": rag_config.chunk_overlap,
                "top_k": rag_config.top_k,
                "rerank_enabled": rag_config.rerank_enabled,
                "rerank_model": rag_config.rerank_model,
            }

    return result


@workspace_bp.route("", methods=["POST"])
@require_auth
def create_workspace() -> tuple[Response, int]:
    """
    Create a new workspace with RAG configuration.

    Request Body:
    {
        "name": "My Research Workspace",
        "description": "For academic papers on AI",
        "rag_config": {
            "embedding_model": "nomic-embed-text",
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8
        }
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data or not data.get("name"):
            return jsonify({"error": "Workspace name is required"}), 400

        name = data["name"].strip()
        description = data.get("description", "").strip() or None
        rag_config = data.get("rag_config")

        if len(name) < 1 or len(name) > 100:
            return jsonify({"error": "Workspace name must be 1-100 characters"}), 400

        # Validate RAG config if provided
        if rag_config:
            valid_retriever_types = ["vector", "graph", "hybrid"]
            if rag_config.get("retriever_type") not in valid_retriever_types:
                return (
                    jsonify(
                        {
                            "error": f"retriever_type must be one of: {', '.join(valid_retriever_types)}"
                        }
                    ),
                    400,
                )

            chunk_size = rag_config.get("chunk_size", 1000)
            if not (100 <= chunk_size <= 5000):
                return jsonify({"error": "chunk_size must be between 100 and 5000"}), 400

            chunk_overlap = rag_config.get("chunk_overlap", 200)
            if not (0 <= chunk_overlap <= 1000):
                return jsonify({"error": "chunk_overlap must be between 0 and 1000"}), 400

            top_k = rag_config.get("top_k", 8)
            if not (1 <= top_k <= 50):
                return jsonify({"error": "top_k must be between 1 and 50"}), 400

        user: User = get_current_user()
        user_id = user.id

        service = get_workspace_service()
        workspace = service.create_workspace(
            name=name,
            user_id=user_id,
            description=description,
            rag_config=rag_config,
        )

        return jsonify(workspace_to_dict(workspace, include_rag_config=True)), 201

    except ValueError as e:
        # Invalid input validation
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except PermissionError as e:
        # Authorization issues
        return jsonify({"error": f"Access denied: {str(e)}"}), 403
    except Exception as e:
        # Catch-all for unexpected errors
        print(f"Unexpected error creating workspace: {e}")
        return jsonify({"error": "Failed to create workspace"}), 500


@workspace_bp.route("", methods=["GET"])
@require_auth
def list_workspaces() -> tuple[Response, int]:
    """
    List all workspaces for the authenticated user.

    Query Parameters:
    - include_inactive: boolean (default: false)
    """
    try:
        user: User = get_current_user()
        user_id = user.id
        include_inactive = request.args.get("include_inactive", "false").lower() == "true"

        service = get_workspace_service()
        workspaces = service.list_workspaces(user_id, include_inactive)

        # Get stats for each workspace
        result = []
        for ws in workspaces:
            ws_dict = workspace_to_dict(ws, include_rag_config=True)
            stats = service.get_workspace_stats(ws.id, user_id)
            if stats:
                ws_dict["document_count"] = stats.document_count
                ws_dict["session_count"] = stats.chat_session_count
            result.append(ws_dict)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Failed to list workspaces: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>", methods=["GET"])
@require_auth
def get_workspace(workspace_id: str) -> tuple[Response, int]:
    """
    Get a specific workspace by ID.
    """
    try:
        user: User = get_current_user()
        user_id = user.id

        service = get_workspace_service()
        workspace = service.get_workspace(workspace_id, user_id)

        if not workspace:
            return jsonify({"error": "Workspace not found"}), 404

        ws_dict = workspace_to_dict(workspace, include_rag_config=True)

        # Include stats
        stats = service.get_workspace_stats(workspace_id, user_id)
        if stats:
            ws_dict["document_count"] = stats.document_count
            ws_dict["session_count"] = stats.chat_session_count

        return jsonify(ws_dict), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get workspace: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>", methods=["PUT", "PATCH"])
@require_auth
def update_workspace(workspace_id: str) -> tuple[Response, int]:
    """
    Update a workspace.

    Request Body:
    {
        "name": "Updated Name",
        "description": "Updated description",
        "is_active": true
    }
    """
    try:
        data = request.get_json()
        user: User = get_current_user()
        user_id = user.id

        # Build update dict with only provided fields
        update_data = {}

        if "name" in data:
            name = data["name"].strip()
            if len(name) < 1 or len(name) > 100:
                return jsonify({"error": "Workspace name must be 1-100 characters"}), 400
            update_data["name"] = name

        if "description" in data:
            description = data["description"].strip() if data["description"] else None
            update_data["description"] = description

        if "is_active" in data:
            if not isinstance(data["is_active"], bool):
                return jsonify({"error": "is_active must be a boolean"}), 400
            update_data["is_active"] = data["is_active"]

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        service = get_workspace_service()
        workspace = service.update_workspace(workspace_id, user_id, **update_data)

        if not workspace:
            return jsonify({"error": "Workspace not found"}), 404

        return jsonify(workspace_to_dict(workspace)), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update workspace: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>", methods=["DELETE"])
@require_auth
def delete_workspace(workspace_id: str) -> tuple[Response, int]:
    """
    Delete a workspace and all its data (cascades to documents, chats, etc.).
    """
    try:
        user: User = get_current_user()
        user_id = user.id

        service = get_workspace_service()
        success = service.delete_workspace(workspace_id, user_id)

        if not success:
            return jsonify({"error": "Workspace not found"}), 404

        return jsonify({"message": "Workspace deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to delete workspace: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/stats", methods=["GET"])
@require_auth
def get_workspace_stats(workspace_id: str) -> tuple[Response, int]:
    """
    Get statistics for a workspace.
    """
    try:
        user: User = get_current_user()
        user_id = user.id

        service = get_workspace_service()
        stats = service.get_workspace_stats(workspace_id, user_id)

        if not stats:
            return jsonify({"error": "Workspace not found"}), 404

        return (
            jsonify(
                {
                    "workspace_id": stats.workspace_id,
                    "document_count": stats.document_count,
                    "total_document_size": stats.total_document_size,
                    "chunk_count": stats.chunk_count,
                    "chat_session_count": stats.chat_session_count,
                    "total_message_count": stats.total_message_count,
                    "last_activity": (
                        stats.last_activity.isoformat() if stats.last_activity else None
                    ),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Failed to get workspace stats: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/validate-access", methods=["GET"])
@require_auth
def validate_workspace_access(workspace_id: str) -> tuple[Response, int]:
    """
    Validate that the current user has access to a workspace.
    Useful for client-side permission checks.
    """
    try:
        user: User = get_current_user()
        user_id = user.id

        service = get_workspace_service()
        has_access = service.validate_workspace_access(workspace_id, user_id)

        return jsonify({"has_access": has_access, "workspace_id": workspace_id}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to validate access: {str(e)}"}), 500
