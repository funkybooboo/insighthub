"""Workspace-scoped Documents & Rag endpoints (scaffolds with TODOs)."""

from flask import Blueprint, request, jsonify, Response
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

# Lightweight auth check to avoid dependency on external decorator

def _require_auth():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401
    return None

# Blueprint mounted under /api/workspaces
workspace_documents_bp = Blueprint("workspace_documents", __name__, url_prefix="/api/workspaces")


def _allowed_filename(filename: str) -> bool:
    lower = filename.lower()
    return lower.endswith(".txt") or lower.endswith(".pdf")


@workspace_documents_bp.route("/<workspace_id>/documents/upload", methods=["POST"])
def upload_workspace_document(workspace_id: str) -> tuple[Response, int]:
    """Upload a document to a workspace (scaffold)."""
    # Simple auth check
    auth_err = _require_auth()
    if auth_err:
        return auth_err

    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file: FileStorage = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    if not _allowed_filename(filename):
        return jsonify({"error": "Unsupported file extension"}), 400

    # TODO: Persist document in workspace-scoped storage
    return (
        jsonify(
            {
                "message": "Workspace document upload not implemented",
                "document": {"id": 0, "filename": filename, "workspace_id": workspace_id},
            }
        ),
        201,
    )


@workspace_documents_bp.route("/<workspace_id>/documents", methods=["GET"])
def list_workspace_documents(workspace_id: str) -> tuple[Response, int]:
    """List workspace-scoped documents (scaffold)."""
    auth_err = _require_auth()
    if auth_err:
        return auth_err
    # TODO: Integrate with workspace-specific document store
    return jsonify({"documents": [], "count": 0}), 200


@workspace_documents_bp.route("/<workspace_id>/documents/<int:doc_id>", methods=["DELETE"])
def delete_workspace_document(workspace_id: str, doc_id: int) -> tuple[Response, int]:
    """Delete workspace-scoped document (scaffold)."""
    auth_err = _require_auth()
    if auth_err:
        return auth_err
    # TODO: Implement actual delete from workspace document store
    return jsonify({"message": "Workspace document deleted (not implemented)"}), 200


@workspace_documents_bp.route("/<workspace_id>/rag/wikipedia", methods=["POST"])
def rag_wikipedia(workspace_id: str) -> tuple[Response, int]:
    """Trigger a Wikipedia fetch for a workspace (scaffold)."""
    auth_err = _require_auth()
    if auth_err:
        return auth_err
    data = request.get_json(silent=True) or {}
    query = data.get("query") if isinstance(data, dict) else None
    if not query:
        return jsonify({"error": "query is required"}), 400
    # TODO: Wire to actual Wikipedia fetch integration
    return (
        jsonify(
            {
                "message": "Wikipedia fetch initiated for workspace",
                "workspace_id": workspace_id,
                "query": query,
            }
        ),
        200,
    )
