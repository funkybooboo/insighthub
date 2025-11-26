"""Workspaces routes for managing workspaces and their resources."""

from flask import Blueprint, Response, g, jsonify, request

from src.infrastructure.auth import get_current_user_id
from src.infrastructure.logger import create_logger

from .dtos import GraphRagConfigDTO, VectorRagConfigDTO
from .mappers import GraphRagConfigMapper, RagConfigMapper, VectorRagConfigMapper, WorkspaceMapper

logger = create_logger(__name__)

workspaces_bp = Blueprint("workspaces", __name__, url_prefix="/api/workspaces")


@workspaces_bp.route("", methods=["GET"])
def list_workspaces() -> tuple[Response, int]:
    """List all workspaces for the current users."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    workspaces = service.list_user_workspaces(user_id)

    # Convert to DTO and then to response dict
    workspace_list_dto = WorkspaceMapper.to_dto_list(workspaces)
    response_data = WorkspaceMapper.dto_list_to_dict(workspace_list_dto)

    return jsonify(response_data), 200


@workspaces_bp.route("", methods=["POST"])
def create_workspace() -> tuple[Response, int]:
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

    # Convert to DTO and then to response dict
    workspace_dto = WorkspaceMapper.to_dto(workspace)
    response_data = WorkspaceMapper.dto_to_dict(workspace_dto)

    # Note: RAG configuration setup happens asynchronously
    response_data["message"] = (
        "Workspace created successfully. RAG configuration setup is in progress."
    )

    return jsonify(response_data), 201


@workspaces_bp.route("/<int:workspace_id>", methods=["GET"])
def get_workspace(workspace_id: int) -> tuple[Response, int]:
    """Get a specific workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    workspace = service.get_user_workspace(workspace_id, user_id)
    if not workspace:
        return jsonify({"error": "Workspace not found"}), 404

    # Convert to DTO and then to response dict
    workspace_dto = WorkspaceMapper.to_dto(workspace)
    response_data = WorkspaceMapper.dto_to_dict(workspace_dto)

    return jsonify(response_data), 200


@workspaces_bp.route("/<int:workspace_id>", methods=["PATCH"])
def update_workspace(workspace_id: int) -> tuple[Response, int]:
    """Update a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    data = request.get_json() or {}

    try:
        # RAG Config is immutable - set only during workspace creation
        workspace = service.update_workspace(
            workspace_id=workspace_id,
            name=data.get("name"),
            description=data.get("description"),
        )

        if not workspace:
            return jsonify({"error": "Workspace not found"}), 404

        # Convert to DTO and then to response dict
        workspace_dto = WorkspaceMapper.to_dto(workspace)
        response_data = WorkspaceMapper.dto_to_dict(workspace_dto)

        return jsonify(response_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@workspaces_bp.route("/<int:workspace_id>", methods=["DELETE"])
def delete_workspace(workspace_id: int) -> tuple[Response, int]:
    """Delete a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    success = service.delete_workspace(workspace_id)

    if not success:
        return jsonify({"error": "Workspace not found"}), 404

    return (
        jsonify({"message": "Workspace deletion initiated successfully. Cleanup is in progress."}),
        200,
    )


# RAG Config endpoints
@workspaces_bp.route("/<int:workspace_id>/rag-config", methods=["GET"])
def get_rag_config(workspace_id: int) -> tuple[Response, int]:
    """Get RAG configuration for a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    config = service.get_rag_config(workspace_id)

    if not config:
        return jsonify({"error": "Workspace not found"}), 404

    # Convert to DTO and then to response dict
    config_dto = RagConfigMapper.to_dto(config)
    response_data = RagConfigMapper.dto_to_dict(config_dto)

    return jsonify(response_data), 200


# Vector RAG Config endpoints
@workspaces_bp.route("/<int:workspace_id>/vector-rag-config", methods=["GET"])
def get_vector_rag_config(workspace_id: int) -> tuple[Response, int]:
    """Get vector RAG configuration for a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    config = service.get_vector_rag_config(workspace_id)
    if not config:
        # Return default config
        default_dto = VectorRagConfigDTO(
            embedding_algorithm="ollama",
            chunking_algorithm="sentence",
            rerank_algorithm="none",
            chunk_size=1000,
            chunk_overlap=200,
            top_k=5,
        )
        response_data = VectorRagConfigMapper.dto_to_dict(default_dto)
        return jsonify(response_data), 200

    # Convert to DTO and then to response dict
    config_dto = VectorRagConfigMapper.to_dto(config)
    response_data = VectorRagConfigMapper.dto_to_dict(config_dto)

    return jsonify(response_data), 200


@workspaces_bp.route("/<int:workspace_id>/vector-rag-config", methods=["POST"])
def create_vector_rag_config(workspace_id: int) -> tuple[Response, int]:
    """Create vector RAG configuration for a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    data = request.get_json() or {}

    try:
        config = service.create_vector_rag_config(
            workspace_id=workspace_id,
            embedding_algorithm=data.get("embedding_algorithm", "ollama"),
            chunking_algorithm=data.get("chunking_algorithm", "sentence"),
            rerank_algorithm=data.get("rerank_algorithm", "none"),
            chunk_size=data.get("chunk_size", 1000),
            chunk_overlap=data.get("chunk_overlap", 200),
            top_k=data.get("top_k", 5),
        )

        # Convert to DTO and then to response dict
        config_dto = VectorRagConfigMapper.to_dto(config)
        response_data = VectorRagConfigMapper.dto_to_dict(config_dto)

        return jsonify(response_data), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@workspaces_bp.route("/<int:workspace_id>/vector-rag-config", methods=["PATCH"])
def update_vector_rag_config(workspace_id: int) -> tuple[Response, int]:
    """Update vector RAG configuration for a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    data = request.get_json() or {}

    try:
        config = service.update_vector_rag_config(
            workspace_id=workspace_id,
            embedding_algorithm=data.get("embedding_algorithm"),
            chunking_algorithm=data.get("chunking_algorithm"),
            rerank_algorithm=data.get("rerank_algorithm"),
            chunk_size=data.get("chunk_size"),
            chunk_overlap=data.get("chunk_overlap"),
            top_k=data.get("top_k"),
        )

        if not config:
            return jsonify({"error": "Vector RAG config not found"}), 404

        # Convert to DTO and then to response dict
        config_dto = VectorRagConfigMapper.to_dto(config)
        response_data = VectorRagConfigMapper.dto_to_dict(config_dto)

        return jsonify(response_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# Graph RAG Config endpoints
@workspaces_bp.route("/<int:workspace_id>/graph-rag-config", methods=["GET"])
def get_graph_rag_config(workspace_id: int) -> tuple[Response, int]:
    """Get graph RAG configuration for a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    config = service.get_graph_rag_config(workspace_id)
    if not config:
        # Return default config
        default_dto = GraphRagConfigDTO(
            entity_extraction_algorithm="spacy",
            relationship_extraction_algorithm="dependency-parsing",
            clustering_algorithm="leiden",
        )
        response_data = GraphRagConfigMapper.dto_to_dict(default_dto)
        return jsonify(response_data), 200

    # Convert to DTO and then to response dict
    config_dto = GraphRagConfigMapper.to_dto(config)
    response_data = GraphRagConfigMapper.dto_to_dict(config_dto)

    return jsonify(response_data), 200


@workspaces_bp.route("/<int:workspace_id>/graph-rag-config", methods=["POST"])
def create_graph_rag_config(workspace_id: int) -> tuple[Response, int]:
    """Create graph RAG configuration for a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    data = request.get_json() or {}

    try:
        config = service.create_graph_rag_config(
            workspace_id=workspace_id,
            entity_extraction_algorithm=data.get("entity_extraction_algorithm", "spacy"),
            relationship_extraction_algorithm=data.get(
                "relationship_extraction_algorithm", "dependency-parsing"
            ),
            clustering_algorithm=data.get("clustering_algorithm", "leiden"),
        )

        # Convert to DTO and then to response dict
        config_dto = GraphRagConfigMapper.to_dto(config)
        response_data = GraphRagConfigMapper.dto_to_dict(config_dto)

        return jsonify(response_data), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@workspaces_bp.route("/<int:workspace_id>/graph-rag-config", methods=["PATCH"])
def update_graph_rag_config(workspace_id: int) -> tuple[Response, int]:
    """Update graph RAG configuration for a workspace."""
    user_id = get_current_user_id()
    service = g.app_context.workspace_service

    # Check access
    if not service.validate_workspace_access(workspace_id, user_id):
        return jsonify({"error": "Workspace not found"}), 404

    data = request.get_json() or {}

    try:
        config = service.update_graph_rag_config(
            workspace_id=workspace_id,
            entity_extraction_algorithm=data.get("entity_extraction_algorithm"),
            relationship_extraction_algorithm=data.get("relationship_extraction_algorithm"),
            clustering_algorithm=data.get("clustering_algorithm"),
        )

        if not config:
            return jsonify({"error": "Graph RAG config not found"}), 404

        # Convert to DTO and then to response dict
        config_dto = GraphRagConfigMapper.to_dto(config)
        response_data = GraphRagConfigMapper.dto_to_dict(config_dto)

        return jsonify(response_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
