"""Workspaces routes for managing workspaces and their resources."""

from flask import Blueprint, g, jsonify, request

from src.infrastructure.auth import get_current_user_id
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)

workspaces_bp = Blueprint("workspaces", __name__, url_prefix="/api/workspaces")


@workspaces_bp.route("", methods=["GET"])
def list_workspaces() -> tuple[list, int]:
    """List all workspaces for the current users."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    workspaces = service.list_user_workspaces(user_id)

    return (
        jsonify(
            [
                {
                    "id": w.id,
                    "name": w.name,
                    "description": w.description,
                    "rag_type": w.rag_type,
                    "created_at": w.created_at.isoformat(),
                    "updated_at": w.updated_at.isoformat(),
                }
                for w in workspaces
            ]
        ),
        200,
    )


@workspaces_bp.route("", methods=["POST"])
def create_workspace() -> tuple[dict, int]:
    """
    Create a new workspace with optional RAG configuration.

    Request Body:
        {
            "name": "Workspace Name",
            "description": "Optional description",
            "rag_type": "vector" | "graph",
            "rag_config": {
                // RAG configuration object (optional)
                // For vector: {embedding_algorithm, chunking_algorithm, rerank_algorithm, ...}
                // For graph: {entity_extraction_algorithm, relationship_extraction_algorithm, ...}
            }
        }

    Returns:
        201: {
            "id": int,
            "name": string,
            "description": string,
            "rag_type": string,
            "created_at": string,
            "updated_at": string
        }
    """
    user_id = get_current_user_id()
    service = g.app_context.workspace_service
    data = request.get_json() or {}

    # Extract RAG config if provided
    rag_config_data = data.get("rag_config")
    rag_type = data.get("rag_type", "vector")

    try:
        workspace = service.create_workspace(
            user_id=user_id,
            name=data.get("name", "New Workspace"),
            description=data.get("description"),
            rag_type=rag_type,
            rag_config=rag_config_data,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return (
        jsonify(
            {
                "id": workspace.id,
                "name": workspace.name,
                "description": workspace.description,
                "rag_type": workspace.rag_type,
                "created_at": workspace.created_at.isoformat(),
                "updated_at": workspace.updated_at.isoformat(),
            }
        ),
        201,
    )


@workspaces_bp.route("/<int:workspace_id>", methods=["GET"])
def get_workspace(workspace_id: int) -> tuple[dict, int]:
    """Get a specific workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    workspace = service.get_user_workspace(workspace_id, user_id)
    if not workspace:
        return jsonify({"error": "Workspace not found"}), 404

    return (
        jsonify(
            {
                "id": workspace.id,
                "name": workspace.name,
                "description": workspace.description,
                "rag_type": workspace.rag_type,
                "created_at": workspace.created_at.isoformat(),
                "updated_at": workspace.updated_at.isoformat(),
            }
        ),
        200,
    )


@workspaces_bp.route("/<int:workspace_id>", methods=["PATCH"])
def update_workspace(workspace_id: int) -> tuple[dict, int]:
    """Update a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    data = request.get_json() or {}

    try:
        workspace = service.update_workspace(
            workspace_id=workspace_id,
            name=data.get("name"),
            description=data.get("description"),
        )

        if not workspace:
            return jsonify({"error": "Workspace not found"}), 404

        return (
            jsonify(
                {
                    "id": workspace.id,
                    "name": workspace.name,
                    "description": workspace.description,
                    "rag_type": workspace.rag_type,
                    "created_at": workspace.created_at.isoformat(),
                    "updated_at": workspace.updated_at.isoformat(),
                }
            ),
            200,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@workspaces_bp.route("/<int:workspace_id>", methods=["DELETE"])
def delete_workspace(workspace_id: int) -> tuple[dict, int]:
    """Delete a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    success = service.delete_workspace(workspace_id)

    if not success:
        return jsonify({"error": "Workspace not found"}), 404

    return jsonify({"message": "Workspace deleted successfully"}), 200


# RAG Config endpoints
@workspaces_bp.route("/<int:workspace_id>/rag-config", methods=["GET"])
def get_rag_config(workspace_id: int) -> tuple[dict, int]:
    """Get RAG configuration for a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    config = service.get_rag_config(workspace_id)

    if not config:
        return jsonify({"error": "Workspace not found"}), 404

    return (
        jsonify(
            {
                "workspace_id": config.workspace_id,
                "rag_type": config.rag_type,
                "config": config.config,
            }
        ),
        200,
    )


# RAG Config is immutable - set only during workspace creation


# Vector RAG Config endpoints (read-only)
@workspaces_bp.route("/<int:workspace_id>/vector-rag-config", methods=["GET"])
def get_vector_rag_config(workspace_id: int) -> tuple[dict, int]:
    """Get vector RAG configuration for a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    config = service.get_vector_rag_config(workspace_id)
    if not config:
        return (
            jsonify(
                {
                    "embedding_algorithm": "ollama",
                    "chunking_algorithm": "sentence",
                    "rerank_algorithm": "none",
                    "chunk_size": 1000,
                    "chunk_overlap": 200,
                    "top_k": 5,
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "embedding_algorithm": config.embedding_algorithm,
                "chunking_algorithm": config.chunking_algorithm,
                "rerank_algorithm": config.rerank_algorithm,
                "chunk_size": config.chunk_size,
                "chunk_overlap": config.chunk_overlap,
                "top_k": config.top_k,
            }
        ),
        200,
    )


# Graph RAG Config endpoints (read-only)
@workspaces_bp.route("/<int:workspace_id>/graph-rag-config", methods=["GET"])
def get_graph_rag_config(workspace_id: int) -> tuple[dict, int]:
    """Get graph RAG configuration for a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    config = service.get_graph_rag_config(workspace_id)
    if not config:
        return (
            jsonify(
                {
                    "entity_extraction_algorithm": "spacy",
                    "relationship_extraction_algorithm": "dependency-parsing",
                    "clustering_algorithm": "leiden",
                }
            ),
            200,
        )

    return (
        jsonify(
            {
                "entity_extraction_algorithm": config.entity_extraction_algorithm,
                "relationship_extraction_algorithm": config.relationship_extraction_algorithm,
                "clustering_algorithm": config.clustering_algorithm,
            }
        ),
        200,
    )
