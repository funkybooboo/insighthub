"""Workspace-scoped document routes."""

from flask import Blueprint, Response, g, jsonify, request

from src.infrastructure.auth import get_current_user, require_auth

from .exceptions import DocumentNotFoundError, DocumentProcessingError, InvalidFileTypeError

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
            "application/pdf": [".pdf"],
            "text/plain": [".txt"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
        }

        if file.mimetype not in allowed_types:
            return jsonify({"error": "Unsupported file type. Allowed: PDF, TXT, DOCX"}), 415

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Upload document via service
        document_service = g.app_context.document_service
        result = document_service.upload_document_to_workspace(
            workspace_id=int(workspace_id),
            user_id=user.id,
            filename=file.filename,
            file_obj=file,
        )

        return jsonify({"message": result.message, "document": result.document}), 201

    except InvalidFileTypeError as e:
        return jsonify({"error": f"Unsupported file type. {str(e)}"}), 415
    except DocumentProcessingError as e:
        return jsonify({"error": f"Document processing failed: {str(e)}"}), 400
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

        # Validate workspace access first
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Parse query parameters
        limit = min(int(request.args.get("limit", 50)), 100)
        offset = max(int(request.args.get("offset", 0)), 0)
        status_filter = request.args.get("status")

        # List documents via service
        document_service = g.app_context.document_service
        result = document_service.list_workspace_documents(
            workspace_id=int(workspace_id),
            user_id=user.id,
            limit=limit,
            offset=offset,
            status_filter=status_filter,
        )

        return (
            jsonify(
                {
                    "documents": result.documents,
                    "count": result.count,
                    "total": result.total,
                }
            ),
            200,
        )

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

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Delete document via service
        document_service = g.app_context.document_service
        try:
            document_service.delete_workspace_document(
                document_id=doc_id, workspace_id=int(workspace_id), user_id=user.id
            )
        except DocumentNotFoundError:
            return jsonify({"error": "Document not found"}), 404

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
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Invalid JSON payload"}), 400

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

        # Validate workspace access
        workspace_service = g.app_context.workspace_service
        if not workspace_service.validate_workspace_access(workspace_id, user.id):
            return jsonify({"error": "No access to workspace"}), 403

        # Fetch Wikipedia article via service
        document_service = g.app_context.document_service
        result = document_service.fetch_wikipedia_article(
            workspace_id=int(workspace_id), user_id=user.id, query=query, language=language
        )

        return jsonify({"message": result.message, "document": result.document}), 200

    except DocumentProcessingError as e:
        return jsonify({"error": f"Wikipedia fetch failed: {str(e)}"}), 404
    except ValueError as e:
        return jsonify({"error": f"Invalid workspace ID: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to fetch Wikipedia article: {str(e)}"}), 500


@documents_bp.route("/<workspace_id>/documents/<int:doc_id>/status", methods=["PATCH"])
def update_document_status(workspace_id: str, doc_id: int) -> tuple[Response, int]:
    """
    Update document processing status.

    This endpoint is called by workers to update document processing status.
    In production, this should be authenticated with worker credentials.

    Request Body:
        {
            "status": "parsing|chunking|embedding|indexing|ready|failed",
            "error_message": "optional error message",
            "chunk_count": 42
        }

    Returns:
        200: {"message": "Status updated successfully"}
        400: {"error": "Invalid status or request"}
        404: {"error": "Document not found"}
        500: {"error": "Server error"}
    """
    try:
        try:
            data = request.get_json()
        except Exception:
            return jsonify({"error": "Invalid JSON payload"}), 400

        if not data or "status" not in data:
            return jsonify({"error": "status is required"}), 400

        status = data["status"]
        error_message = data.get("error_message")
        chunk_count = data.get("chunk_count")

        # Validate status
        valid_statuses = [
            "pending",
            "parsing",
            "chunking",
            "embedding",
            "indexing",
            "ready",
            "failed",
        ]
        if status not in valid_statuses:
            return (
                jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}),
                400,
            )

        # Validate that document belongs to workspace
        document_service = g.app_context.document_service
        document = document_service.get_document_by_id(doc_id)
        if not document or document.workspace_id != int(workspace_id):
            return jsonify({"error": "Document not found in workspace"}), 404

        # Update document status
        success = document_service.update_document_status(
            document_id=doc_id,
            status=status,
            error_message=error_message,
            chunk_count=chunk_count,
        )

        if not success:
            return jsonify({"error": "Document update failed"}), 500

        return jsonify({"message": "Status updated successfully"}), 200

    except ValueError as e:
        return jsonify({"error": f"Invalid request: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update status: {str(e)}"}), 500
