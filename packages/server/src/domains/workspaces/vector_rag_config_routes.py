"""Vector RAG configuration routes for workspace-specific configurations."""

from flask import Blueprint, Response, g, jsonify, request

from src.infrastructure.auth import get_current_user, require_auth

vector_rag_config_bp = Blueprint("vector_rag_config", __name__, url_prefix="/api/workspaces")


@vector_rag_config_bp.route("/<workspace_id>/vector-rag-config", methods=["GET"])
@require_auth
def get_vector_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Get Vector RAG configuration for a workspace.

    Returns:
        200: {
            "id": int,
            "workspace_id": int,
            "embedding_algorithm": "string",
            "chunking_algorithm": "string",
            "chunk_size": int,
            "chunk_overlap": int,
            "top_k": int,
            "rerank_enabled": bool,
            "rerank_algorithm": "string" | null,
            "created_at": "string",
            "updated_at": "string"
        }
        403: {"error": "string"} - No access to workspace
        404: {"error": "string"} - Workspace not found or no config
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()

        # Get Vector RAG config via service
        config = g.app_context.vector_rag_config_service.get_vector_rag_config(
            workspace_id=int(workspace_id), user_id=user.id
        )

        if not config:
            return jsonify({"error": "Vector RAG configuration not found"}), 404

        return (
            jsonify(
                {
                    "id": config.id,
                    "workspace_id": config.workspace_id,
                    "embedding_algorithm": config.embedding_algorithm,
                    "chunking_algorithm": config.chunking_algorithm,
                    "chunk_size": config.chunk_size,
                    "chunk_overlap": config.chunk_overlap,
                    "top_k": config.top_k,
                    "rerank_enabled": config.rerank_enabled,
                    "rerank_algorithm": config.rerank_algorithm,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": f"Invalid workspace ID: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to get Vector RAG config: {str(e)}"}), 500


@vector_rag_config_bp.route("/<workspace_id>/vector-rag-config", methods=["POST"])
@require_auth
def create_vector_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Create Vector RAG configuration for a workspace.

    Request Body:
    {
        "embedding_algorithm": "nomic-embed-text",
        "chunking_algorithm": "sentence",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "top_k": 8,
        "rerank_enabled": false,
        "rerank_algorithm": null
    }

    Returns:
        201: {
            "id": int,
            "workspace_id": int,
            "embedding_algorithm": "string",
            "chunking_algorithm": "string",
            "chunk_size": int,
            "chunk_overlap": int,
            "top_k": int,
            "rerank_enabled": bool,
            "rerank_algorithm": "string" | null,
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

        # Create Vector RAG config via service
        config = g.app_context.vector_rag_config_service.create_vector_rag_config(
            workspace_id=int(workspace_id), user_id=user.id, **data
        )

        return (
            jsonify(
                {
                    "id": config.id,
                    "workspace_id": config.workspace_id,
                    "embedding_algorithm": config.embedding_algorithm,
                    "chunking_algorithm": config.chunking_algorithm,
                    "chunk_size": config.chunk_size,
                    "chunk_overlap": config.chunk_overlap,
                    "top_k": config.top_k,
                    "rerank_enabled": config.rerank_enabled,
                    "rerank_algorithm": config.rerank_algorithm,
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
        return jsonify({"error": f"Failed to create Vector RAG config: {str(e)}"}), 500


@vector_rag_config_bp.route("/<workspace_id>/vector-rag-config", methods=["PATCH"])
@require_auth
def update_vector_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Update Vector RAG configuration for a workspace.

    Request Body (all fields optional):
    {
        "embedding_algorithm": "nomic-embed-text",
        "chunking_algorithm": "sentence",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "top_k": 8,
        "rerank_enabled": false,
        "rerank_algorithm": null
    }

    Returns:
        200: {
            "id": int,
            "workspace_id": int,
            "embedding_algorithm": "string",
            "chunking_algorithm": "string",
            "chunk_size": int,
            "chunk_overlap": int,
            "top_k": int,
            "rerank_enabled": bool,
            "rerank_algorithm": "string" | null,
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

        # Update Vector RAG config via service
        config = g.app_context.vector_rag_config_service.update_vector_rag_config(
            workspace_id=int(workspace_id), user_id=user.id, **data
        )

        if not config:
            return jsonify({"error": "Vector RAG configuration not found"}), 404

        return (
            jsonify(
                {
                    "id": config.id,
                    "workspace_id": config.workspace_id,
                    "embedding_algorithm": config.embedding_algorithm,
                    "chunking_algorithm": config.chunking_algorithm,
                    "chunk_size": config.chunk_size,
                    "chunk_overlap": config.chunk_overlap,
                    "top_k": config.top_k,
                    "rerank_enabled": config.rerank_enabled,
                    "rerank_algorithm": config.rerank_algorithm,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update Vector RAG config: {str(e)}"}), 500