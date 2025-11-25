"""Unit tests for document routes."""

import json
from io import BytesIO
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from werkzeug.datastructures import FileStorage

from src.domains.workspaces.documents.routes import documents_bp


@pytest.fixture
def app() -> Flask:
    """Create a test Flask app."""
    app = Flask(__name__)
    app.register_blueprint(documents_bp)
    app.config["TESTING"] = True
    app.config["UPLOAD_FOLDER"] = "/tmp"
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB
    return app


@pytest.fixture
def client(app: Flask):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def mock_document_service():
    """Mock document service."""
    return Mock()


@pytest.fixture
def mock_workspace_service():
    """Mock workspace service."""
    return Mock()


@pytest.fixture
def mock_app_context(mock_document_service, mock_workspace_service):
    """Mock app context."""
    mock_context = Mock()
    mock_context.document_service = mock_document_service
    mock_context.workspace_service = mock_workspace_service
    return mock_context


class TestUploadDocument:
    """Test cases for document upload."""

    def test_upload_document_success(
        self,
        client: Flask,
        mock_app_context: Mock,
        mock_document_service: Mock,
        mock_workspace_service: Mock,
    ) -> None:
        """Test successful document upload."""
        mock_workspace_service.validate_workspace_access.return_value = True

        # Mock the upload result
        mock_result = Mock()
        mock_result.document.filename = "test.txt"
        mock_result.document.processing_status = "pending"
        mock_result.is_duplicate = False
        mock_document_service.process_document_upload.return_value = mock_result

        # Create test file
        test_content = b"This is a test document"
        test_file = FileStorage(
            stream=BytesIO(test_content), filename="test.txt", content_type="text/plain"
        )

        with patch("src.domains.workspaces.documents.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/workspaces/1/documents/upload",
                data={"file": test_file},
                content_type="multipart/form-data",
            )

            assert response.status_code == 201
            data = json.loads(response.data)
            assert "document" in data
            assert data["document"]["filename"] == "test.txt"
            assert data["document"]["processing_status"] == "pending"

    def test_upload_document_no_file(self, client: Flask) -> None:
        """Test upload with no file provided."""
        response = client.post(
            "/api/workspaces/1/documents/upload", content_type="multipart/form-data"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_upload_document_empty_filename(self, client: Flask) -> None:
        """Test upload with empty filename."""
        test_file = FileStorage(stream=BytesIO(b"content"), filename="", content_type="text/plain")

        response = client.post(
            "/api/workspaces/1/documents/upload",
            data={"file": test_file},
            content_type="multipart/form-data",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_upload_document_no_workspace_access(
        self, client: Flask, mock_app_context: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test upload without workspace access."""
        mock_workspace_service.validate_workspace_access.return_value = False

        test_file = FileStorage(
            stream=BytesIO(b"content"), filename="test.txt", content_type="text/plain"
        )

        with patch("src.domains.workspaces.documents.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/workspaces/1/documents/upload",
                data={"file": test_file},
                content_type="multipart/form-data",
            )

            assert response.status_code == 403
            data = json.loads(response.data)
            assert "error" in data


class TestFetchWikipedia:
    """Test cases for Wikipedia article fetching."""

    def test_fetch_wikipedia_success(
        self,
        client: Flask,
        mock_app_context: Mock,
        mock_document_service: Mock,
        mock_workspace_service: Mock,
    ) -> None:
        """Test successful Wikipedia fetch."""
        mock_workspace_service.validate_workspace_access.return_value = True

        # Mock the fetch result
        mock_result = Mock()
        mock_result.document.filename = "Wikipedia_Machine_Learning_pending.md"
        mock_result.message = "Wikipedia article fetched and added to workspace"
        mock_document_service.fetch_wikipedia_article.return_value = mock_result

        fetch_data = {"query": "Machine Learning", "language": "en"}

        with patch("src.domains.workspaces.documents.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.post(
                "/api/workspaces/1/documents/fetch-wikipedia",
                data=json.dumps(fetch_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "document" in data
            assert "message" in data

    def test_fetch_wikipedia_missing_query(self, client: Flask) -> None:
        """Test Wikipedia fetch with missing query."""
        fetch_data = {"language": "en"}

        response = client.post(
            "/api/workspaces/1/documents/fetch-wikipedia",
            data=json.dumps(fetch_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_fetch_wikipedia_empty_query(self, client: Flask) -> None:
        """Test Wikipedia fetch with empty query."""
        fetch_data = {"query": "", "language": "en"}

        response = client.post(
            "/api/workspaces/1/documents/fetch-wikipedia",
            data=json.dumps(fetch_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_fetch_wikipedia_query_too_long(self, client: Flask) -> None:
        """Test Wikipedia fetch with query that's too long."""
        long_query = "a" * 201  # Over 200 character limit
        fetch_data = {"query": long_query, "language": "en"}

        response = client.post(
            "/api/workspaces/1/documents/fetch-wikipedia",
            data=json.dumps(fetch_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_fetch_wikipedia_invalid_language(self, client: Flask) -> None:
        """Test Wikipedia fetch with invalid language."""
        fetch_data = {"query": "Test", "language": "invalid"}

        response = client.post(
            "/api/workspaces/1/documents/fetch-wikipedia",
            data=json.dumps(fetch_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data


class TestUpdateDocumentStatus:
    """Test cases for document status updates."""

    def test_update_status_success(
        self,
        client: Flask,
        mock_app_context: Mock,
        mock_document_service: Mock,
        mock_workspace_service: Mock,
    ) -> None:
        """Test successful status update."""
        mock_workspace_service.validate_workspace_access.return_value = True
        mock_document_service.update_document_status.return_value = True

        status_data = {"status": "ready", "chunk_count": 10}

        with patch("src.domains.workspaces.documents.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.patch(
                "/api/workspaces/1/documents/1/status",
                data=json.dumps(status_data),
                content_type="application/json",
            )

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "message" in data

    def test_update_status_missing_status(self, client: Flask) -> None:
        """Test status update with missing status field."""
        status_data = {"chunk_count": 10}

        response = client.patch(
            "/api/workspaces/1/documents/1/status",
            data=json.dumps(status_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_update_status_invalid_status(self, client: Flask) -> None:
        """Test status update with invalid status value."""
        status_data = {"status": "invalid_status"}

        response = client.patch(
            "/api/workspaces/1/documents/1/status",
            data=json.dumps(status_data),
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_update_status_document_not_found(
        self,
        client: Flask,
        mock_app_context: Mock,
        mock_document_service: Mock,
        mock_workspace_service: Mock,
    ) -> None:
        """Test status update for non-existent document."""
        mock_workspace_service.validate_workspace_access.return_value = True
        mock_document_service.get_document_by_id.return_value = None

        status_data = {"status": "ready"}

        with patch("src.domains.workspaces.documents.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.patch(
                "/api/workspaces/1/documents/999/status",
                data=json.dumps(status_data),
                content_type="application/json",
            )

            assert response.status_code == 404
            data = json.loads(response.data)
            assert "error" in data

    def test_update_status_wrong_workspace(
        self,
        client: Flask,
        mock_app_context: Mock,
        mock_document_service: Mock,
        mock_workspace_service: Mock,
    ) -> None:
        """Test status update for document in wrong workspace."""
        mock_workspace_service.validate_workspace_access.return_value = True

        # Mock document that belongs to workspace 2, not 1
        mock_document = Mock()
        mock_document.workspace_id = 2
        mock_document_service.get_document_by_id.return_value = mock_document

        status_data = {"status": "ready"}

        with patch("src.domains.workspaces.documents.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.patch(
                "/api/workspaces/1/documents/1/status",
                data=json.dumps(status_data),
                content_type="application/json",
            )

            assert response.status_code == 404
            data = json.loads(response.data)
            assert "error" in data


class TestListDocuments:
    """Test cases for listing documents."""

    def test_list_documents_success(
        self,
        client: Flask,
        mock_app_context: Mock,
        mock_document_service: Mock,
        mock_workspace_service: Mock,
    ) -> None:
        """Test successful document listing."""
        mock_workspace_service.validate_workspace_access.return_value = True

        # Mock document list response
        mock_response = Mock()
        mock_response.documents = []
        mock_response.total_count = 0
        mock_document_service.list_workspace_documents_as_dto.return_value = mock_response

        with patch("src.domains.workspaces.documents.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.get("/api/workspaces/1/documents")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, list)

    def test_list_documents_no_workspace_access(
        self, client: Flask, mock_app_context: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test listing documents without workspace access."""
        mock_workspace_service.validate_workspace_access.return_value = False

        with patch("src.domains.workspaces.documents.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.get("/api/workspaces/1/documents")

            assert response.status_code == 403
            data = json.loads(response.data)
            assert "error" in data


class TestDeleteDocument:
    """Test cases for document deletion."""

    def test_delete_document_success(
        self,
        client: Flask,
        mock_app_context: Mock,
        mock_document_service: Mock,
        mock_workspace_service: Mock,
    ) -> None:
        """Test successful document deletion."""
        mock_workspace_service.validate_workspace_access.return_value = True
        mock_document_service.delete_workspace_document.return_value = None  # Success

        with patch("src.domains.workspaces.documents.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.delete("/api/workspaces/1/documents/1")

            assert response.status_code == 200
            data = json.loads(response.data)
            assert "message" in data

    def test_delete_document_no_workspace_access(
        self, client: Flask, mock_app_context: Mock, mock_workspace_service: Mock
    ) -> None:
        """Test deleting document without workspace access."""
        mock_workspace_service.validate_workspace_access.return_value = False

        with patch("src.domains.workspaces.documents.routes.g") as mock_g:
            mock_g.app_context = mock_app_context

            response = client.delete("/api/workspaces/1/documents/1")

            assert response.status_code == 403
            data = json.loads(response.data)
            assert "error" in data
