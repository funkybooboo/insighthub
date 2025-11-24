"""Workspace-scoped document routes."""

from flask import Blueprint, Response, g, jsonify, request
from werkzeug.datastructures import FileStorage

from src.infrastructure.auth import get_current_user, require_auth

documents_bp = Blueprint("documents", __name__, url_prefix="/api/workspaces")


@documents_bp.route("/<workspace_id>/documents/upload", methods=["POST"])
@require_auth
def upload_workspace_document(workspace_id: str) -> tuple[Response, int]:
    """
    Upload a document to a workspace.

    Request: multipart/form-data with 'file' field
    Supported formats: PDF, TXT, DOCX

    Returns:
        201: {
            "message": "Document uploaded successfully",
            "document": {
                "id": int,
                "filename": "string",
                "file_size": int,
                "mime_type": "string",
                "chunk_count": int,
                "created_at": "string"
            }
        }
        400: {"error": "string"} - Invalid file or request
        403: {"error": "string"} - No access to workspace
        413: {"error": "string"} - File too large
        415: {"error": "string"} - Unsupported file type
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()

        if "file" not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        file = request.files["file"]
        if not file or not file.filename:
            return jsonify({"error": "No file selected"}), 400

        # Validate file size (10MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({"error": "File too large (max 10MB)"}), 413

        # Validate file type
        allowed_types = {
            'application/pdf': ['.pdf'],
            'text/plain': ['.txt'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
        }

        if file.mimetype not in allowed_types:
            return jsonify({"error": "Unsupported file type. Allowed: PDF, TXT, DOCX"}), 415

        # TODO: Validate workspace access
        # TODO: Upload document via service
        # document = g.app_context.document_service.upload_document(
        #     workspace_id=int(workspace_id),
        #     user_id=user.id,
        #     file=file,
        #     filename=file.filename
        # )

        # Mock response for now
        mock_document = {
            "id": 1,
            "filename": file.filename,
            "file_size": file_size,
            "mime_type": file.mimetype,
            "chunk_count": 10,
            "created_at": "2025-01-01T00:00:00Z"
        }

        return jsonify({
            "message": "Document uploaded successfully",
            "document": mock_document
        }), 201

    except ValueError as e:
        return jsonify({"error": f"Invalid workspace ID: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to upload document: {str(e)}"}), 500


@documents_bp.route("/<workspace_id>/documents", methods=["GET"])
@require_auth
def list_workspace_documents(workspace_id: str) -> tuple[Response, int]:
    """
    List all documents in a workspace.

    Query Parameters:
        - limit: int (default: 50, max: 100)
        - offset: int (default: 0)
        - status: string (optional filter by processing status)

    Returns:
        200: {
            "documents": [
                {
                    "id": int,
                    "filename": "string",
                    "file_size": int,
                    "mime_type": "string",
                    "chunk_count": int,
                    "processing_status": "string",
                    "created_at": "string"
                }
            ],
            "count": int,
            "total": int
        }
        403: {"error": "string"} - No access to workspace
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()

        # Parse query parameters
        limit = min(int(request.args.get("limit", 50)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
        status_filter = request.args.get("status")

        # TODO: Validate workspace access
        # TODO: List documents via service
        # result = g.app_context.document_service.list_workspace_documents(
        #     workspace_id=int(workspace_id),
        #     user_id=user.id,
        #     limit=limit,
        #     offset=offset,
        #     status_filter=status_filter
        # )

        # Mock response for now
        mock_documents = [
            {
                "id": 1,
                "filename": "sample.pdf",
                "file_size": 1024,
                "mime_type": "application/pdf",
                "chunk_count": 10,
                "processing_status": "ready",
                "created_at": "2025-01-01T00:00:00Z"
            }
        ]

        return jsonify({
            "documents": mock_documents,
            "count": len(mock_documents),
            "total": len(mock_documents)
        }), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid workspace ID: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to list documents: {str(e)}"}), 500


@documents_bp.route("/<workspace_id>/documents/<int:doc_id>", methods=["DELETE"])
@require_auth
def delete_workspace_document(workspace_id: str, doc_id: int) -> tuple[Response, int]:
    """
    Delete a document from a workspace.

    Returns:
        200: {"message": "Document deleted successfully"}
        403: {"error": "string"} - No access to workspace/document
        404: {"error": "string"} - Document not found
        409: {"error": "string"} - Document in use or processing
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()

        # TODO: Validate workspace and document access
        # TODO: Check if document is currently being processed
        # TODO: Delete document via service (removes from vector store too)
        # g.app_context.document_service.delete_document(
        #     document_id=doc_id,
        #     workspace_id=int(workspace_id),
        #     user_id=user.id
        # )

        return jsonify({"message": "Document deleted successfully"}), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid ID format: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to delete document: {str(e)}"}), 500


@documents_bp.route("/<workspace_id>/documents/fetch-wikipedia", methods=["POST"])
@require_auth
def fetch_wikipedia_article(workspace_id: str) -> tuple[Response, int]:
    """
    Fetch a Wikipedia article and add it to the workspace's document collection.

    Request Body:
        {
            "query": "Article title or search query",
            "language": "en"  // Optional, default "en"
        }

    Returns:
        200: {
            "message": "Wikipedia article fetched and added to workspace",
            "document": {
                "id": int,
                "filename": "string",
                "file_size": int,
                "mime_type": "string",
                "chunk_count": int,
                "created_at": "string"
            }
        }
        400: {"error": "string"} - Invalid query or request
        403: {"error": "string"} - No access to workspace
        404: {"error": "string"} - Article not found
        429: {"error": "string"} - Rate limited
        500: {"error": "string"} - Server error
    """
    try:
        user = get_current_user()
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        query = data.get("query", "").strip()
        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        if len(query) > 200:  # Reasonable limit
            return jsonify({"error": "Query too long (max 200 characters)"}), 400

        language = data.get("language", "en")
        if language not in ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh"]:
            return jsonify({"error": "Unsupported language"}), 400

        # TODO: Validate workspace access
        # TODO: Fetch Wikipedia article via service
        # document = g.app_context.document_service.fetch_wikipedia_article(
        #     workspace_id=int(workspace_id),
        #     user_id=user.id,
        #     query=query,
        #     language=language
        # )

        # Mock response for now
        mock_document = {
            "id": 2,
            "filename": f"Wikipedia_{query.replace(' ', '_')}.txt",
            "file_size": 2048,
            "mime_type": "text/plain",
            "chunk_count": 15,
            "created_at": "2025-01-01T00:00:00Z"
        }

        return jsonify({
            "message": "Wikipedia article fetched and added to workspace",
            "document": mock_document
        }), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid workspace ID: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to fetch Wikipedia article: {str(e)}"}), 500