"""Workspace API endpoints for InsightHub."""

from typing import Optional

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from domains.workspaces.service import WorkspaceService
from infrastructure.database import get_db_connection

workspace_bp = Blueprint("workspaces", __name__, url_prefix="/api/workspaces")


@workspace_bp.route("", methods=["POST"])
@jwt_required()
async def create_workspace():
    """
    Create a new workspace.

    Request Body:
    {
        "name": "My Research Workspace",
        "description": "For academic papers on AI"
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data or not data.get("name"):
            return jsonify({"error": "Workspace name is required"}), 400

        name = data["name"].strip()
        description = data.get("description", "").strip() or None

        if len(name) < 1 or len(name) > 100:
            return jsonify({"error": "Workspace name must be 1-100 characters"}), 400

        user_id = get_jwt_identity()

        async with get_db_connection() as db:
            service = WorkspaceService(db)
            workspace = await service.create_workspace(name, user_id, description)

            return (
                jsonify(
                    {
                        "id": workspace.id,
                        "name": workspace.name,
                        "description": workspace.description,
                        "user_id": workspace.user_id,
                        "is_active": workspace.is_active,
                        "created_at": workspace.created_at.isoformat(),
                        "updated_at": workspace.updated_at.isoformat(),
                    }
                ),
                201,
            )

    except Exception as e:
        return jsonify({"error": f"Failed to create workspace: {str(e)}"}), 500


@workspace_bp.route("", methods=["GET"])
@jwt_required()
async def list_workspaces():
    """
    List all workspaces for the authenticated user.

    Query Parameters:
    - include_inactive: boolean (default: false)
    """
    try:
        user_id = get_jwt_identity()
        include_inactive = request.args.get("include_inactive", "false").lower() == "true"

        async with get_db_connection() as db:
            service = WorkspaceService(db)
            workspaces = await service.list_workspaces(user_id, include_inactive)

            return (
                jsonify(
                    {
                        "workspaces": [
                            {
                                "id": ws.id,
                                "name": ws.name,
                                "description": ws.description,
                                "user_id": ws.user_id,
                                "is_active": ws.is_active,
                                "created_at": ws.created_at.isoformat(),
                                "updated_at": ws.updated_at.isoformat(),
                            }
                            for ws in workspaces
                        ]
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": f"Failed to list workspaces: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>", methods=["GET"])
@jwt_required()
async def get_workspace(workspace_id: str):
    """
    Get a specific workspace by ID.
    """
    try:
        user_id = get_jwt_identity()

        async with get_db_connection() as db:
            service = WorkspaceService(db)
            workspace = await service.get_workspace(workspace_id, user_id)

            if not workspace:
                return jsonify({"error": "Workspace not found"}), 404

            return (
                jsonify(
                    {
                        "id": workspace.id,
                        "name": workspace.name,
                        "description": workspace.description,
                        "user_id": workspace.user_id,
                        "is_active": workspace.is_active,
                        "created_at": workspace.created_at.isoformat(),
                        "updated_at": workspace.updated_at.isoformat(),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": f"Failed to get workspace: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>", methods=["PUT"])
@jwt_required()
async def update_workspace(workspace_id: str):
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
        user_id = get_jwt_identity()

        # Build update dict with only provided fields
        update_data = {}

        if "name" in data:
            name = data["name"].strip()
            if len(name) < 1 or len(name) > 100:
                return jsonify({"error": "Workspace name must be 1-100 characters"}), 400
            update_data["name"] = name

        if "description" in data:
            description = data["description"].strip() or None
            update_data["description"] = description

        if "is_active" in data:
            if not isinstance(data["is_active"], bool):
                return jsonify({"error": "is_active must be a boolean"}), 400
            update_data["is_active"] = data["is_active"]

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        async with get_db_connection() as db:
            service = WorkspaceService(db)
            workspace = await service.update_workspace(workspace_id, user_id, **update_data)

            if not workspace:
                return jsonify({"error": "Workspace not found"}), 404

            return (
                jsonify(
                    {
                        "id": workspace.id,
                        "name": workspace.name,
                        "description": workspace.description,
                        "user_id": workspace.user_id,
                        "is_active": workspace.is_active,
                        "created_at": workspace.created_at.isoformat(),
                        "updated_at": workspace.updated_at.isoformat(),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": f"Failed to update workspace: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>", methods=["DELETE"])
@jwt_required()
async def delete_workspace(workspace_id: str):
    """
    Delete a workspace and all its data (cascades to documents, chats, etc.).
    """
    try:
        user_id = get_jwt_identity()

        async with get_db_connection() as db:
            service = WorkspaceService(db)
            success = await service.delete_workspace(workspace_id, user_id)

            if not success:
                return jsonify({"error": "Workspace not found"}), 404

            return jsonify({"message": "Workspace deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to delete workspace: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/stats", methods=["GET"])
@jwt_required()
async def get_workspace_stats(workspace_id: str):
    """
    Get statistics for a workspace.
    """
    try:
        user_id = get_jwt_identity()

        async with get_db_connection() as db:
            service = WorkspaceService(db)
            stats = await service.get_workspace_stats(workspace_id, user_id)

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


@workspace_bp.route("/<workspace_id>/rag-config", methods=["GET"])
@jwt_required()
async def get_rag_config(workspace_id: str):
    """
    Get RAG configuration for a workspace.
    """
    try:
        user_id = get_jwt_identity()

        async with get_db_connection() as db:
            service = WorkspaceService(db)
            config = await service.get_rag_config(workspace_id, user_id)

            if not config:
                return jsonify({"error": "Workspace not found"}), 404

            return (
                jsonify(
                    {
                        "id": config.id,
                        "workspace_id": config.workspace_id,
                        "embedding_model": config.embedding_model,
                        "retriever_type": config.retriever_type,
                        "chunk_size": config.chunk_size,
                        "chunk_overlap": config.chunk_overlap,
                        "top_k": config.top_k,
                        "embedding_dim": config.embedding_dim,
                        "rerank_enabled": config.rerank_enabled,
                        "rerank_model": config.rerank_model,
                        "created_at": config.created_at.isoformat(),
                        "updated_at": config.updated_at.isoformat(),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": f"Failed to get RAG config: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/rag-config", methods=["PUT"])
@jwt_required()
async def update_rag_config(workspace_id: str):
    """
    Update RAG configuration for a workspace.

    Request Body:
    {
        "embedding_model": "nomic-embed-text",
        "retriever_type": "vector",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "top_k": 8,
        "embedding_dim": 768,
        "rerank_enabled": false,
        "rerank_model": null
    }
    """
    try:
        data = request.get_json()
        user_id = get_jwt_identity()

        # Validate RAG config fields
        allowed_fields = [
            "embedding_model",
            "retriever_type",
            "chunk_size",
            "chunk_overlap",
            "top_k",
            "embedding_dim",
            "rerank_enabled",
            "rerank_model",
        ]

        update_data = {}

        for field in allowed_fields:
            if field in data:
                if field in ["chunk_size", "chunk_overlap", "top_k", "embedding_dim"]:
                    if not isinstance(data[field], int) or data[field] < 0:
                        return jsonify({"error": f"{field} must be a non-negative integer"}), 400
                elif field == "rerank_enabled":
                    if not isinstance(data[field], bool):
                        return jsonify({"error": "rerank_enabled must be a boolean"}), 400
                elif field in ["embedding_model", "retriever_type", "rerank_model"]:
                    if not isinstance(data[field], str) or len(data[field].strip()) == 0:
                        return jsonify({"error": f"{field} must be a non-empty string"}), 400

                update_data[field] = data[field]

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        async with get_db_connection() as db:
            service = WorkspaceService(db)
            config = await service.update_rag_config(workspace_id, user_id, **update_data)

            if not config:
                return jsonify({"error": "Workspace not found"}), 404

            return (
                jsonify(
                    {
                        "id": config.id,
                        "workspace_id": config.workspace_id,
                        "embedding_model": config.embedding_model,
                        "retriever_type": config.retriever_type,
                        "chunk_size": config.chunk_size,
                        "chunk_overlap": config.chunk_overlap,
                        "top_k": config.top_k,
                        "embedding_dim": config.embedding_dim,
                        "rerank_enabled": config.rerank_enabled,
                        "rerank_model": config.rerank_model,
                        "created_at": config.created_at.isoformat(),
                        "updated_at": config.updated_at.isoformat(),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": f"Failed to update RAG config: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/validate-access", methods=["GET"])
@jwt_required()
async def validate_workspace_access(workspace_id: str):
    """
    Validate that the current user has access to a workspace.
    Useful for client-side permission checks.
    """
    try:
        user_id = get_jwt_identity()

        async with get_db_connection() as db:
            service = WorkspaceService(db)
            has_access = await service.validate_workspace_access(workspace_id, user_id)

            return jsonify({"has_access": has_access, "workspace_id": workspace_id}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to validate access: {str(e)}"}), 500
