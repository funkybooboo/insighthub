"""Default RAG configuration routes."""

from flask import Blueprint, Response, g, jsonify, request

from src.domains.default_rag_configs.mappers import DefaultRagConfigMapper
from src.infrastructure.auth import get_current_user, require_auth

default_rag_configs_bp = Blueprint(
    "default_rag_configs", __name__, url_prefix="/api/default-rag-configs"
)


@default_rag_configs_bp.route("", methods=["GET"])
@require_auth
def get_default_config() -> tuple[Response, int]:
    """
    Get default RAG configuration for the current users.

    Returns:
        200: {
            "id": int,
            "user_id": int,
            "vector_config": {
                "embedding_algorithm": "string",
                "chunking_algorithm": "string",
                "rerank_algorithm": "string",
                "chunk_size": int,
                "chunk_overlap": int,
                "top_k": int
            },
            "graph_config": {
                "entity_extraction_algorithm": "string",
                "relationship_extraction_algorithm": "string",
                "clustering_algorithm": "string"
            },
            "created_at": "string",
            "updated_at": "string"
        }
        404: {"error": "string"} - No config found
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()
        service = g.app_context.default_rag_config_service

        config = service.get_user_config(user.id)

        if not config:
            return jsonify({"error": "No default RAG config found for users"}), 404

        # Convert model to DTO using mapper
        config_dto = DefaultRagConfigMapper.to_dto(config)

        # Convert DTO to response dict using mapper
        response_data = DefaultRagConfigMapper.to_response_dict(config_dto)

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get default RAG config: {str(e)}"}), 500


@default_rag_configs_bp.route("", methods=["POST", "PATCH"])
@require_auth
def create_or_update_config() -> tuple[Response, int]:
    """
    Create or update default RAG configuration for the current users.

    Request Body:
        {
            "vector_config": {
                "embedding_algorithm": "string" (optional),
                "chunking_algorithm": "string" (optional),
                "rerank_algorithm": "string" (optional),
                "chunk_size": int (optional),
                "chunk_overlap": int (optional),
                "top_k": int (optional)
            },
            "graph_config": {
                "entity_extraction_algorithm": "string" (optional),
                "relationship_extraction_algorithm": "string" (optional),
                "clustering_algorithm": "string" (optional)
            }
        }

    Returns:
        200/201: {
            "id": int,
            "user_id": int,
            "vector_config": {...},
            "graph_config": {...},
            "created_at": "string",
            "updated_at": "string"
        }
        400: {"error": "string"} - Invalid request
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()
        service = g.app_context.default_rag_config_service

        try:
            data = request.get_json() or {}
        except Exception:
            return jsonify({"error": "Invalid JSON payload"}), 400

        # Extract config data using mapper
        vector_config_data = None
        if "vector_config" in data:
            vector_config_data = DefaultRagConfigMapper.vector_config_from_dict(
                data["vector_config"]
            )

        graph_config_data = None
        if "graph_config" in data:
            graph_config_data = DefaultRagConfigMapper.graph_config_from_dict(data["graph_config"])

        config = service.create_or_update_config(
            user_id=user.id,
            vector_config=vector_config_data,
            graph_config=graph_config_data,
        )

        status_code = 201 if request.method == "POST" else 200

        # Convert model to DTO using mapper
        config_dto = DefaultRagConfigMapper.to_dto(config)

        # Convert DTO to response dict using mapper
        response_data = DefaultRagConfigMapper.to_response_dict(config_dto)

        return jsonify(response_data), status_code

    except Exception as e:
        return jsonify({"error": f"Failed to save default RAG config: {str(e)}"}), 500


@default_rag_configs_bp.route("", methods=["DELETE"])
@require_auth
def delete_config() -> tuple[Response, int]:
    """
    Delete default RAG configuration for the current users.

    Returns:
        200: {"message": "Default RAG config deleted successfully"}
        404: {"error": "string"} - No config found
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()
        service = g.app_context.default_rag_config_service

        success = service.delete_config(user.id)

        if not success:
            return jsonify({"error": "No default RAG config found for users"}), 404

        return jsonify({"message": "Default RAG config deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to delete default RAG config: {str(e)}"}), 500
