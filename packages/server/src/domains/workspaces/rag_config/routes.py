"""RAG Config routes for workspace-specific RAG configurations."""

from flask import Blueprint, Response, g, jsonify, request

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

        # Get RAG config via service
        config = g.app_context.rag_config_service.get_rag_config(
            workspace_id=int(workspace_id), user_id=user.id
        )

        if not config:
            return jsonify({"error": "RAG configuration not found"}), 404

        return (
            jsonify(
                {
                    "id": config.id,
                    "workspace_id": config.workspace_id,
                    "embedding_model": config.embedding_model,
                    "embedding_dim": config.embedding_dim,
                    "retriever_type": config.retriever_type,
                    "chunk_size": config.chunk_size,
                    "chunk_overlap": config.chunk_overlap,
                    "top_k": config.top_k,
                    "rerank_enabled": config.rerank_enabled,
                    "rerank_model": config.rerank_model,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": f"Invalid workspace ID: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to get RAG config: {str(e)}"}), 500


@rag_config_bp.route("/<workspace_id>/rag-config", methods=["POST"])
@require_auth
def create_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Create RAG configuration for a workspace.

    Request Body:
    {
        "embedding_model": "nomic-embed-text",
        "retriever_type": "vector",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "top_k": 8
    }

    Returns:
        201: {
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
        400: {"error": "string"} - Invalid request data
        403: {"error": "string"} - No access to workspace
        409: {"error": "string"} - Config already exists
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()
        data = request.get_json() or {}

        # Validate required fields
        required_fields = [
            "embedding_model",
            "retriever_type",
            "chunk_size",
            "chunk_overlap",
            "top_k",
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create RAG config via service
        config = g.app_context.rag_config_service.create_rag_config(
            workspace_id=int(workspace_id), user_id=user.id, **data
        )

        return (
            jsonify(
                {
                    "id": config.id,
                    "workspace_id": config.workspace_id,
                    "embedding_model": config.embedding_model,
                    "embedding_dim": config.embedding_dim,
                    "retriever_type": config.retriever_type,
                    "chunk_size": config.chunk_size,
                    "chunk_overlap": config.chunk_overlap,
                    "top_k": config.top_k,
                    "rerank_enabled": config.rerank_enabled,
                    "rerank_model": config.rerank_model,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat(),
                }
            ),
            201,
        )

    except ValueError as e:
        if "already exists" in str(e):
            return jsonify({"error": str(e)}), 409
        return jsonify({"error": str(e)}), 400
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
        400: {"error": "string"} - Invalid request data
        403: {"error": "string"} - No access to workspace
        404: {"error": "string"} - Config not found
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Update RAG config via service
        config = g.app_context.rag_config_service.update_rag_config(
            workspace_id=int(workspace_id), user_id=user.id, **data
        )

        if not config:
            return jsonify({"error": "RAG configuration not found"}), 404

        return (
            jsonify(
                {
                    "id": config.id,
                    "workspace_id": config.workspace_id,
                    "embedding_model": config.embedding_model,
                    "embedding_dim": config.embedding_dim,
                    "retriever_type": config.retriever_type,
                    "chunk_size": config.chunk_size,
                    "chunk_overlap": config.chunk_overlap,
                    "top_k": config.top_k,
                    "rerank_enabled": config.rerank_enabled,
                    "rerank_model": config.rerank_model,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update RAG config: {str(e)}"}), 500
