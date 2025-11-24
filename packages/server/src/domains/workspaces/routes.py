"""Workspace API endpoints for InsightHub."""

from typing import TypedDict

from flask import Blueprint, Response, g, jsonify, request
from shared.models.workspace import RagConfig, Workspace

from src.domains.workspaces.service import WorkspaceService
from src.infrastructure.auth import get_current_user, require_auth

workspace_bp = Blueprint("workspaces", __name__, url_prefix="/api/workspaces")


def get_workspace_service() -> WorkspaceService:
    """Get workspace service from app context."""
    return g.app_context.workspace_service


class RagConfigDict(TypedDict, total=False):
    """TypedDict for RAG config response."""

    id: int
    workspace_id: int
    embedding_model: str
    embedding_dim: int | None
    retriever_type: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    rerank_enabled: bool
    rerank_model: str | None
    created_at: str
    updated_at: str


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
    rag_config: RagConfigDict
    document_count: int
    session_count: int


def workspace_to_dict(workspace: Workspace, rag_config: RagConfig | None = None) -> WorkspaceDict:
    """Convert workspace model to dict for JSON response."""
    result: WorkspaceDict = {
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

    if rag_config:
        result["rag_config"] = rag_config_to_dict(rag_config)

    return result


def rag_config_to_dict(config: RagConfig) -> RagConfigDict:
    """Convert RagConfig model to dict for JSON response."""
    return {
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

        if len(name) < 1 or len(name) > 100:
            return jsonify({"error": "Workspace name must be 1-100 characters"}), 400

        user_id = get_current_user().id

        # Extract RAG config if provided
        rag_config_data = data.get("rag_config")

        service = get_workspace_service()
        workspace = service.create_workspace(
            name=name,
            user_id=user_id,
            description=description,
            rag_config_data=rag_config_data,
        )

        rag_config = service.get_rag_config(workspace.id, user_id)
        return jsonify(workspace_to_dict(workspace, rag_config)), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create workspace: {str(e)}"}), 500


@workspace_bp.route("", methods=["GET"])
@require_auth
def list_workspaces() -> tuple[Response, int]:
    """
    List all workspaces for the authenticated user.

    Query Parameters:
    - include_inactive: boolean (default: false)
    """
    try:
        user_id = get_current_user().id
        include_inactive = request.args.get("include_inactive", "false").lower() == "true"

        service = get_workspace_service()
        workspaces = service.list_workspaces(user_id, include_inactive)

        # Get stats for each workspace
        result = []
        for ws in workspaces:
            rag_config = service.get_rag_config(ws.id, user_id)
            ws_dict = workspace_to_dict(ws, rag_config)
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
        user_id = get_current_user().id

        service = get_workspace_service()
        workspace = service.get_workspace(workspace_id, user_id)

        if not workspace:
            return jsonify({"error": "Workspace not found"}), 404

        rag_config = service.get_rag_config(workspace_id, user_id)
        ws_dict = workspace_to_dict(workspace, rag_config)

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
        user_id = get_current_user().id

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

        rag_config = service.get_rag_config(workspace_id, user_id)
        return jsonify(workspace_to_dict(workspace, rag_config)), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update workspace: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>", methods=["DELETE"])
@require_auth
def delete_workspace(workspace_id: str) -> tuple[Response, int]:
    """
    Delete a workspace and all its data (cascades to documents, chats, etc.).
    """
    try:
        user_id = get_current_user().id

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
        user_id = get_current_user().id

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


@workspace_bp.route("/<workspace_id>/rag-config", methods=["GET"])
@require_auth
def get_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Get RAG configuration for a workspace.
    """
    try:
        user_id = get_current_user().id

        service = get_workspace_service()
        rag_cfg = service.get_rag_config(workspace_id, user_id)

        if not rag_cfg:
            return jsonify({"error": "Workspace not found"}), 404

        return jsonify(rag_config_to_dict(rag_cfg)), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get RAG config: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/rag-config", methods=["POST"])
@require_auth
def create_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Create RAG configuration for a workspace.

    Note: RAG config is automatically created with workspace, so this
    endpoint returns the existing config or updates it with provided values.

    Request Body:
    {
        "embedding_model": "nomic-embed-text",
        "embedding_dim": 768,
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
        data = request.get_json() or {}

        service = get_workspace_service()

        # Check if workspace exists and user has access
        workspace = service.get_workspace(workspace_id, user_id)
        if not workspace:
            return jsonify({"error": "Workspace not found"}), 404

        # Get existing config (should always exist as it's created with workspace)
        rag_cfg = service.get_rag_config(workspace_id, user_id)

        if rag_cfg:
            # Update with provided values
            update_fields = {}
            allowed_fields = [
                "embedding_model",
                "embedding_dim",
                "retriever_type",
                "chunk_size",
                "chunk_overlap",
                "top_k",
                "rerank_enabled",
                "rerank_model",
            ]
            for field in allowed_fields:
                if field in data:
                    update_fields[field] = data[field]

            if update_fields:
                rag_cfg = service.update_rag_config(workspace_id, user_id, **update_fields)

            if rag_cfg:
                return jsonify(rag_config_to_dict(rag_cfg)), 200

        return jsonify({"error": "RAG config not found for workspace"}), 404

    except Exception as e:
        return jsonify({"error": f"Failed to create RAG config: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/rag-config", methods=["PATCH"])
@require_auth
def update_rag_config(workspace_id: str) -> tuple[Response, int]:
    """
    Update RAG configuration for a workspace.

    Request Body (all fields optional):
    {
        "embedding_model": "nomic-embed-text",
        "embedding_dim": 768,
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

        # Build update dict with only provided fields
        update_fields = {}
        allowed_fields = [
            "embedding_model",
            "embedding_dim",
            "retriever_type",
            "chunk_size",
            "chunk_overlap",
            "top_k",
            "rerank_enabled",
            "rerank_model",
        ]

        for field in allowed_fields:
            if field in data:
                update_fields[field] = data[field]

        if not update_fields:
            return jsonify({"error": "No valid fields to update"}), 400

        # Validate fields
        if "retriever_type" in update_fields:
            if update_fields["retriever_type"] not in ["vector", "graph", "hybrid"]:
                return (
                    jsonify({"error": "retriever_type must be 'vector', 'graph', or 'hybrid'"}),
                    400,
                )

        if "chunk_size" in update_fields:
            if not (100 <= update_fields["chunk_size"] <= 5000):
                return jsonify({"error": "chunk_size must be between 100 and 5000"}), 400

        if "chunk_overlap" in update_fields:
            if not (0 <= update_fields["chunk_overlap"] <= 1000):
                return (
                    jsonify({"error": "chunk_overlap must be between 0 and 1000"}),
                    400,
                )

        if "top_k" in update_fields:
            if not (1 <= update_fields["top_k"] <= 50):
                return jsonify({"error": "top_k must be between 1 and 50"}), 400

        service = get_workspace_service()
        rag_cfg = service.update_rag_config(workspace_id, user_id, **update_fields)

        if not rag_cfg:
            return jsonify({"error": "Workspace not found"}), 404

        return jsonify(rag_config_to_dict(rag_cfg)), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update RAG config: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/validate-access", methods=["GET"])
@require_auth
def validate_workspace_access(workspace_id: str) -> tuple[Response, int]:
    """
    Validate that the current user has access to a workspace.
    Useful for client-side permission checks.
    """
    try:
        user_id = get_current_user().id

        service = get_workspace_service()
        has_access = service.validate_workspace_access(workspace_id, user_id)

        return jsonify({"has_access": has_access, "workspace_id": workspace_id}), 200

    except Exception as e:\n        return jsonify({"error": f"Failed to validate access: {str(e)}"}), 500\n\n\n# ===== Workspace Documents & Rag Endpoints (TODO) =====\n# Note: These are scaffolds to align client expectations. Implement full logic later.\n\nfrom werkzeug.datastructures import FileStorage  # type: ignore\nfrom werkzeug.utils import secure_filename  # type: ignore\n\n@workspace_bp.route("/<workspace_id>/documents/upload", methods=["POST"])\n@require_auth\ndef upload_workspace_document(workspace_id: str) -> tuple[Response, int]:\n    \"\"\"Upload a document to a workspace (stub). TODO: hook to DocumentService.\"\"\"\n    if "file" not in request.files:\n        return jsonify({"error": "No file part in request"}), 400\n    file: FileStorage = request.files["file"]\n    if not file.filename:\n        return jsonify({"error": "No file selected"}), 400\n    filename = secure_filename(file.filename)\n    # TODO: Persist document in workspace scope\n    return jsonify({"message": "Workspace document upload not implemented", "document": {"id": 0, "filename": filename}}), 201\n\n@workspace_bp.route("/<workspace_id>/documents", methods=["GET"])\ndef list_workspace_documents(workspace_id: str) -> tuple[Response, int]:\n    \"\"\"List workspace-scoped documents (stub).\"\"\"\n    # TODO: Replace with real document listing from workspace scope\n    return jsonify({"documents": [], "count": 0}), 200\n\n@workspace_bp.route("/<workspace_id>/documents/<int:doc_id>", methods=["DELETE"])\n@require_auth\ndef delete_workspace_document(workspace_id: str, doc_id: int) -> tuple[Response, int]:\n    \"\"\"Delete a workspace-scoped document (stub).\"\"\"\n    # TODO: Replace with call to document service to delete by doc_id within workspace\n    return jsonify({"message": "Workspace document deleted (not implemented)"}), 200\n\n@workspace_bp.route("/<workspace_id>/rag/wikipedia", methods=["POST"])\n@require_auth\ndef rag_wikipedia(workspace_id: str) -> tuple[Response, int]:\n    \"\"\"Fetch a Wikipedia article for the given workspace (stub).\"\"\"\n    data = request.get_json(silent=True) or {}\n    query = data.get("query") if isinstance(data, dict) else None\n    if not query:\n        return jsonify({"error": "query is required"}), 400\n    # TODO: hook into actual Wikipedia fetch/integration\n    return jsonify({"message": "Wikipedia fetch initiated for workspace", "workspace_id": workspace_id, "query": query}), 200\n