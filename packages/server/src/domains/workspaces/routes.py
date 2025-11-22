"""Workspace API endpoints for InsightHub."""

import contextlib
import os
from pathlib import Path
from typing import TypedDict

from flask import Blueprint, Response, g, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from shared.models.workspace import RagConfig, Workspace
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from src.domains.workspaces.service import WorkspaceService
from src.infrastructure.database import get_db_connection

workspace_bp = Blueprint("workspaces", __name__, url_prefix="/api/workspaces")

# Upload configuration
UPLOAD_FOLDER = Path(os.getenv("UPLOAD_FOLDER", "uploads"))
UPLOAD_FOLDER.mkdir(exist_ok=True)


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


def workspace_to_dict(workspace: Workspace, include_stats: bool = False) -> WorkspaceDict:
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

    # Include RAG config if loaded
    if workspace.rag_config:
        result["rag_config"] = rag_config_to_dict(workspace.rag_config)

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
@jwt_required()
async def create_workspace() -> tuple[Response, int]:
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

        user_id = get_jwt_identity()

        # Extract RAG config if provided
        rag_config_data = data.get("rag_config")

        async with get_db_connection() as db:
            service = WorkspaceService(db)
            workspace = await service.create_workspace(
                name=name,
                user_id=user_id,
                description=description,
                rag_config_data=rag_config_data,
            )

            # Reload to get the rag_config relationship
            workspace = await service.get_workspace(workspace.id, user_id)

            return jsonify(workspace_to_dict(workspace)), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create workspace: {str(e)}"}), 500


@workspace_bp.route("", methods=["GET"])
@jwt_required()
async def list_workspaces() -> tuple[Response, int]:
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

            # Get stats for each workspace
            result = []
            for ws in workspaces:
                ws_dict = workspace_to_dict(ws)
                stats = await service.get_workspace_stats(ws.id, user_id)
                if stats:
                    ws_dict["document_count"] = stats.document_count
                    ws_dict["session_count"] = stats.chat_session_count
                result.append(ws_dict)

            return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Failed to list workspaces: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>", methods=["GET"])
@jwt_required()
async def get_workspace(workspace_id: str) -> tuple[Response, int]:
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

            ws_dict = workspace_to_dict(workspace)

            # Include stats
            stats = await service.get_workspace_stats(workspace_id, user_id)
            if stats:
                ws_dict["document_count"] = stats.document_count
                ws_dict["session_count"] = stats.chat_session_count

            return jsonify(ws_dict), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get workspace: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>", methods=["PUT", "PATCH"])
@jwt_required()
async def update_workspace(workspace_id: str) -> tuple[Response, int]:
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
            description = data["description"].strip() if data["description"] else None
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

            return jsonify(workspace_to_dict(workspace)), 200

    except Exception as e:
        return jsonify({"error": f"Failed to update workspace: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>", methods=["DELETE"])
@jwt_required()
async def delete_workspace(workspace_id: str) -> tuple[Response, int]:
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
async def get_workspace_stats(workspace_id: str) -> tuple[Response, int]:
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
async def get_rag_config(workspace_id: str) -> tuple[Response, int]:
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

            return jsonify(rag_config_to_dict(config)), 200

    except Exception as e:
        return jsonify({"error": f"Failed to get RAG config: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/validate-access", methods=["GET"])
@jwt_required()
async def validate_workspace_access(workspace_id: str) -> tuple[Response, int]:
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


# ============================================================================
# Document endpoints for workspace-specific document management
# ============================================================================


@workspace_bp.route("/<workspace_id>/documents", methods=["GET"])
@jwt_required()
async def list_workspace_documents(workspace_id: str) -> tuple[Response, int]:
    """
    List all documents in a workspace.
    """
    try:
        user_id = get_jwt_identity()

        async with get_db_connection() as db:
            service = WorkspaceService(db)

            # Validate access
            if not await service.validate_workspace_access(workspace_id, user_id):
                return jsonify({"error": "Workspace not found"}), 404

            documents = await service.get_workspace_documents(workspace_id, user_id)

            return (
                jsonify(
                    {
                        "documents": [
                            {
                                "id": doc.id,
                                "filename": doc.filename,
                                "file_size": doc.file_size,
                                "mime_type": doc.mime_type,
                                "chunk_count": doc.chunk_count,
                                "processing_status": doc.processing_status,
                                "processing_error": doc.processing_error,
                                "created_at": doc.created_at.isoformat(),
                                "updated_at": doc.updated_at.isoformat(),
                            }
                            for doc in documents
                        ],
                        "count": len(documents),
                    }
                ),
                200,
            )

    except Exception as e:
        return jsonify({"error": f"Failed to list documents: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/documents/upload", methods=["POST"])
@jwt_required()
async def upload_workspace_document(workspace_id: str) -> tuple[Response, int]:
    """
    Upload a document to a workspace.
    """
    try:
        user_id = get_jwt_identity()

        # Validate file is present
        if "file" not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        file: FileStorage = request.files["file"]

        if not file.filename or file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Validate file type
        filename = secure_filename(file.filename)
        allowed_extensions = {"txt", "pdf", "md"}
        extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
        if extension not in allowed_extensions:
            return jsonify({"error": f"File type not allowed. Allowed: {allowed_extensions}"}), 400

        async with get_db_connection() as db:
            service = WorkspaceService(db)

            # Validate workspace access
            workspace = await service.get_workspace(workspace_id, user_id)
            if not workspace:
                return jsonify({"error": "Workspace not found"}), 404

            # Save file temporarily
            file_path = UPLOAD_FOLDER / filename
            file.save(str(file_path))

            try:
                # Use the document service from app context
                with open(file_path, "rb") as f:
                    response_dto = g.app_context.document_service.upload_document_with_user(
                        user_id=user_id,
                        filename=filename,
                        file_obj=f,
                    )

                # Associate document with workspace
                document = g.app_context.document_service.get_document_by_id(
                    response_dto.document.id
                )
                if document:
                    document = await service.add_document_to_workspace(
                        workspace_id, user_id, document
                    )

                status_code = 200 if "already exists" in response_dto.message else 201
                return jsonify(response_dto.to_dict()), status_code

            finally:
                # Clean up temp file
                if file_path.exists():
                    os.remove(file_path)

    except Exception as e:
        return jsonify({"error": f"Failed to upload document: {str(e)}"}), 500


@workspace_bp.route("/<workspace_id>/documents/<int:document_id>", methods=["DELETE"])
@jwt_required()
async def delete_workspace_document(workspace_id: str, document_id: int) -> tuple[Response, int]:
    """
    Delete a document from a workspace.
    """
    try:
        user_id = get_jwt_identity()

        async with get_db_connection() as db:
            service = WorkspaceService(db)

            # Validate workspace access and delete document
            success = await service.remove_document_from_workspace(
                workspace_id, document_id, user_id
            )

            if not success:
                return jsonify({"error": "Document not found in workspace"}), 404

            # Also delete from blob storage via document service
            with contextlib.suppress(Exception):
                g.app_context.document_service.delete_document(
                    document_id, delete_from_storage=True
                )

            return jsonify({"message": "Document deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to delete document: {str(e)}"}), 500
