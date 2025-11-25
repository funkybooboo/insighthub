"""Graph RAG configuration routes for workspace-specific configurations."""

from flask import Blueprint, Response, g, jsonify, request

from src.infrastructure.auth import get_current_user, require_auth

graph_rag_config_bp = Blueprint("graph_rag_config", __name__, url_prefix="/api/workspaces")


@graph_rag_config_bp.route("/<workspace_id>/graph-rag-config", methods=["GET"])
@require_auth
def get_graph_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Get Graph RAG configuration for a workspace.

    Returns:
        200: {
            "id": int,
            "workspace_id": int,
            "entity_extraction_algorithm": "string",
            "relationship_extraction_algorithm": "string",
            "clustering_algorithm": "string",
            "max_hops": int,
            "min_cluster_size": int,
            "max_cluster_size": int,
            "created_at": "string",
            "updated_at": "string"
        }
        403: {"error": "string"} - No access to workspace
        404: {"error": "string"} - Workspace not found or no config
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()

        # Get Graph RAG config via service
        config = g.app_context.graph_rag_config_service.get_graph_rag_config(
            workspace_id=int(workspace_id), user_id=user.id
        )

        if not config:
            return jsonify({"error": "Graph RAG configuration not found"}), 404

        return (
            jsonify(
                {
                    "id": config.id,
                    "workspace_id": config.workspace_id,
                    "entity_extraction_algorithm": config.entity_extraction_algorithm,
                    "relationship_extraction_algorithm": config.relationship_extraction_algorithm,
                    "clustering_algorithm": config.clustering_algorithm,
                    "max_hops": config.max_hops,
                    "min_cluster_size": config.min_cluster_size,
                    "max_cluster_size": config.max_cluster_size,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": f"Invalid workspace ID: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to get Graph RAG config: {str(e)}"}), 500


@graph_rag_config_bp.route("/<workspace_id>/graph-rag-config", methods=["POST"])
@require_auth
def create_graph_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Create Graph RAG configuration for a workspace.

    Request Body:
    {
        "entity_extraction_algorithm": "ollama",
        "relationship_extraction_algorithm": "ollama",
        "clustering_algorithm": "leiden",
        "max_hops": 2,
        "min_cluster_size": 5,
        "max_cluster_size": 50
    }

    Returns:
        201: {
            "id": int,
            "workspace_id": int,
            "entity_extraction_algorithm": "string",
            "relationship_extraction_algorithm": "string",
            "clustering_algorithm": "string",
            "max_hops": int,
            "min_cluster_size": int,
            "max_cluster_size": int,
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

        # Create Graph RAG config via service
        config = g.app_context.graph_rag_config_service.create_graph_rag_config(
            workspace_id=int(workspace_id), user_id=user.id, **data
        )

        return (
            jsonify(
                {
                    "id": config.id,
                    "workspace_id": config.workspace_id,
                    "entity_extraction_algorithm": config.entity_extraction_algorithm,
                    "relationship_extraction_algorithm": config.relationship_extraction_algorithm,
                    "clustering_algorithm": config.clustering_algorithm,
                    "max_hops": config.max_hops,
                    "min_cluster_size": config.min_cluster_size,
                    "max_cluster_size": config.max_cluster_size,
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
        return jsonify({"error": f"Failed to create Graph RAG config: {str(e)}"}), 500


@graph_rag_config_bp.route("/<workspace_id>/graph-rag-config", methods=["PATCH"])
@require_auth
def update_graph_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Update Graph RAG configuration for a workspace.

    Request Body (all fields optional):
    {
        "entity_extraction_algorithm": "ollama",
        "relationship_extraction_algorithm": "ollama",
        "clustering_algorithm": "leiden",
        "max_hops": 2,
        "min_cluster_size": 5,
        "max_cluster_size": 50
    }

    Returns:
        200: {
            "id": int,
            "workspace_id": int,
            "entity_extraction_algorithm": "string",
            "relationship_extraction_algorithm": "string",
            "clustering_algorithm": "string",
            "max_hops": int,
            "min_cluster_size": int,
            "max_cluster_size": int,
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

        # Update Graph RAG config via service
        config = g.app_context.graph_rag_config_service.update_graph_rag_config(
            workspace_id=int(workspace_id), user_id=user.id, **data
        )

        if not config:
            return jsonify({"error": "Graph RAG configuration not found"}), 404

        return (
            jsonify(
                {
                    "id": config.id,
                    "workspace_id": config.workspace_id,
                    "entity_extraction_algorithm": config.entity_extraction_algorithm,
                    "relationship_extraction_algorithm": config.relationship_extraction_algorithm,
                    "clustering_algorithm": config.clustering_algorithm,
                    "max_hops": config.max_hops,
                    "min_cluster_size": config.min_cluster_size,
                    "max_cluster_size": config.max_cluster_size,
                    "created_at": config.created_at.isoformat(),
                    "updated_at": config.updated_at.isoformat(),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update Graph RAG config: {str(e)}"}), 500