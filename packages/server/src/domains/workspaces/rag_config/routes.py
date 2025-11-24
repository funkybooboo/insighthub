"""RAG Config routes for workspace-specific RAG configurations."""

from flask import Blueprint, Response, g, jsonify, request
from shared.models.workspace import RagConfig

from src.infrastructure.auth import get_current_user, require_auth

rag_config_bp = Blueprint("rag_config", __name__, url_prefix="/api/workspaces")


@rag_config_bp.route("/<workspace_id>/rag-config", methods=["GET"])
@require_auth
def get_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Get RAG configuration for a workspace.

    Returns:
        200: {
            "id": int,
            "workspace_id": int,
            "embedding_model": "string",
            "embedding_dim": int | null,
            "retriever_type": "string",
            "chunk_size": int,
            "chunk_overlap": int,
            "top_k": int,
            "rerank_enabled": bool,
            "rerank_model": "string" | null,
            "created_at": "string",
            "updated_at": "string"
        }
        403: {"error": "string"} - No access to workspace
        404: {"error": "string"} - Workspace not found or no config
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()

        # TODO: Validate workspace access
        # TODO: Get RAG config via service
        # config = g.app_context.rag_config_service.get_config(
        #     workspace_id=int(workspace_id),
        #     user_id=user.id
        # )

        # Mock response for now
        mock_config = {
            "id": 1,
            "workspace_id": int(workspace_id),
            "embedding_model": "nomic-embed-text",
            "embedding_dim": None,
            "retriever_type": "vector",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k": 8,
            "rerank_enabled": False,
            "rerank_model": None,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }

        return jsonify(mock_config), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid workspace ID: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to get RAG config: {str(e)}"}), 500


@rag_config_bp.route("/<workspace_id>/rag-config", methods=["POST"])
@require_auth
def create_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Create RAG configuration for a workspace.

    Note: RAG config is automatically created with workspace, so this
    endpoint returns the existing config or updates it with provided values.

    Request Body:
    {
        "embedding_model": "nomic-embed-text",
        "retriever_type": "vector",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "top_k": 8
    }
    """
    try:
        user_id = get_current_user().id
        data = request.get_json() or {}

        # TODO: Implement actual RAG config creation/update
        # For now, return mock response
        mock_config = {
            "id": 1,
            "workspace_id": int(workspace_id),
            "embedding_model": data.get("embedding_model", "nomic-embed-text"),
            "embedding_dim": data.get("embedding_dim"),
            "retriever_type": data.get("retriever_type", "vector"),
            "chunk_size": data.get("chunk_size", 1000),
            "chunk_overlap": data.get("chunk_overlap", 200),
            "top_k": data.get("top_k", 8),
            "rerank_enabled": data.get("rerank_enabled", False),
            "rerank_model": data.get("rerank_model"),
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }

        return jsonify(mock_config), 200

    except Exception as e:
        return jsonify({"error": f"Failed to create RAG config: {str(e)}"}), 500


@rag_config_bp.route("/<workspace_id>/rag-config", methods=["PATCH"])
@require_auth
def update_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Update RAG configuration for a workspace.

    Request Body (all fields optional):
    {
        "embedding_model": "nomic-embed-text",
        "retriever_type": "vector",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "top_k": 8,
        "rerank_enabled": false,
        "rerank_model": null
    }
    """
    try:
        user_id = get_current_user().id
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # TODO: Implement actual RAG config update
        # For now, return mock response
        mock_config = {
            "id": 1,
            "workspace_id": int(workspace_id),
            "embedding_model": data.get("embedding_model", "nomic-embed-text"),
            "embedding_dim": data.get("embedding_dim"),
            "retriever_type": data.get("retriever_type", "vector"),
            "chunk_size": data.get("chunk_size", 1000),
            "chunk_overlap": data.get("chunk_overlap", 200),
            "top_k": data.get("top_k", 8),
            "rerank_enabled": data.get("rerank_enabled", False),
            "rerank_model": data.get("rerank_model"),
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }

        return jsonify(mock_config), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update RAG config: {str(e)}"}), 500