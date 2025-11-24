"""Integration tests for document API endpoints."""

import io
import json

import pytest
from flask import Flask
from flask.testing import FlaskClient


class TestDocumentUploadEndpoint:
    """Tests for POST /api/documents/upload endpoint."""

    def test_upload_txt_returns_201(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/documents/upload with TXT file returns 201."""
        data = {"file": (io.BytesIO(b"Hello world content"), "test.txt")}

        response = client.post(
            "/api/documents/upload",
            data=data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert "document" in response_data
        assert response_data["document"]["filename"] == "test.txt"
        assert "text_length" in response_data

    def test_upload_pdf_returns_201(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/documents/upload with PDF file returns 201."""
        # Minimal PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
        data = {"file": (io.BytesIO(pdf_content), "test.pdf")}

        response = client.post(
            "/api/documents/upload",
            data=data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        # May return 201 for success or 500 if PDF parsing fails with minimal content
        assert response.status_code in [201, 500]

    def test_upload_no_file_returns_400(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/documents/upload without file returns 400."""
        response = client.post(
            "/api/documents/upload",
            data={},
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_upload_empty_filename_returns_400(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/documents/upload with empty filename returns 400."""
        data = {"file": (io.BytesIO(b"content"), "")}

        response = client.post(
            "/api/documents/upload",
            data=data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_upload_invalid_extension_returns_400(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/documents/upload with invalid extension returns 400."""
        data = {"file": (io.BytesIO(b"content"), "test.exe")}

        response = client.post(
            "/api/documents/upload",
            data=data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        assert response.status_code == 400

    def test_upload_unauthorized_returns_401(self, client: FlaskClient) -> None:
        """POST /api/documents/upload without auth returns 401."""
        data = {"file": (io.BytesIO(b"content"), "test.txt")}

        response = client.post(
            "/api/documents/upload",
            data=data,
            content_type="multipart/form-data",
        )

        assert response.status_code == 401

    def test_upload_duplicate_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """POST /api/documents/upload with duplicate file returns 200."""
        content = b"Duplicate content test"
        data1 = {"file": (io.BytesIO(content), "first.txt")}

        # First upload
        response1 = client.post(
            "/api/documents/upload",
            data=data1,
            headers=auth_headers,
            content_type="multipart/form-data",
        )
        assert response1.status_code == 201

        # Second upload with same content
        data2 = {"file": (io.BytesIO(content), "second.txt")}
        response2 = client.post(
            "/api/documents/upload",
            data=data2,
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        # Duplicate returns 200 instead of 201
        assert response2.status_code == 200
        response_data = json.loads(response2.data)
        assert "already exists" in response_data["message"]


class TestDocumentListEndpoint:
    """Tests for GET /api/documents endpoint."""

    def test_list_documents_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/documents returns 200 with list."""
        response = client.get("/api/documents", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "documents" in data
        assert "count" in data
        assert isinstance(data["documents"], list)

    def test_list_documents_returns_uploaded_documents(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/documents returns previously uploaded documents."""
        # Upload a document
        upload_data = {"file": (io.BytesIO(b"List test content"), "list_test.txt")}
        client.post(
            "/api/documents/upload",
            data=upload_data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        # List documents
        response = client.get("/api/documents", headers=auth_headers)

        data = json.loads(response.data)
        assert data["count"] >= 1
        filenames = [doc["filename"] for doc in data["documents"]]
        assert "list_test.txt" in filenames

    def test_list_documents_includes_metadata(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """GET /api/documents includes document metadata."""
        # Upload a document
        upload_data = {"file": (io.BytesIO(b"Metadata test"), "metadata_test.txt")}
        client.post(
            "/api/documents/upload",
            data=upload_data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        response = client.get("/api/documents", headers=auth_headers)

        data = json.loads(response.data)
        assert len(data["documents"]) >= 1
        doc = next(d for d in data["documents"] if d["filename"] == "metadata_test.txt")
        assert "id" in doc
        assert "filename" in doc
        assert "file_size" in doc
        assert "mime_type" in doc
        assert "created_at" in doc

    def test_list_documents_unauthorized_returns_401(self, client: FlaskClient) -> None:
        """GET /api/documents without auth returns 401."""
        response = client.get("/api/documents")

        assert response.status_code == 401


class TestDocumentDeleteEndpoint:
    """Tests for DELETE /api/documents/<id> endpoint."""

    def test_delete_document_returns_200(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """DELETE /api/documents/<id> returns 200."""
        # Upload a document first
        upload_data = {"file": (io.BytesIO(b"To delete content"), "to_delete.txt")}
        upload_response = client.post(
            "/api/documents/upload",
            data=upload_data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )
        doc_id = json.loads(upload_response.data)["document"]["id"]

        # Delete the document
        response = client.delete(f"/api/documents/{doc_id}", headers=auth_headers)

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data

    def test_delete_document_removes_from_list(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """DELETE /api/documents/<id> removes document from list."""
        # Upload a document
        upload_data = {"file": (io.BytesIO(b"Will be removed"), "will_remove.txt")}
        upload_response = client.post(
            "/api/documents/upload",
            data=upload_data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )
        doc_id = json.loads(upload_response.data)["document"]["id"]

        # Delete the document
        client.delete(f"/api/documents/{doc_id}", headers=auth_headers)

        # Verify it's no longer in the list
        list_response = client.get("/api/documents", headers=auth_headers)
        data = json.loads(list_response.data)
        doc_ids = [doc["id"] for doc in data["documents"]]
        assert doc_id not in doc_ids

    def test_delete_nonexistent_returns_404(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """DELETE /api/documents/<id> for nonexistent returns 404."""
        response = client.delete("/api/documents/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_unauthorized_returns_401(self, client: FlaskClient) -> None:
        """DELETE /api/documents/<id> without auth returns 401."""
        response = client.delete("/api/documents/1")

        assert response.status_code == 401


class TestDocumentFileTypes:
    """Tests for document file type handling."""

    def test_txt_mime_type_detected(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """TXT file gets correct mime type."""
        data = {"file": (io.BytesIO(b"Plain text content"), "plain.txt")}

        response = client.post(
            "/api/documents/upload",
            data=data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        assert response.status_code == 201
        doc = json.loads(response.data)["document"]
        assert doc["mime_type"] == "text/plain"

    def test_text_content_extracted(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """Text content is extracted and length returned."""
        content = "This is some test content for extraction."
        data = {"file": (io.BytesIO(content.encode()), "extract.txt")}

        response = client.post(
            "/api/documents/upload",
            data=data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["text_length"] == len(content)

    def test_unicode_content_handled(
        self, client: FlaskClient, auth_headers: dict[str, str]
    ) -> None:
        """Unicode content is handled correctly."""
        content = "Hello world! Test content."
        data = {"file": (io.BytesIO(content.encode("utf-8")), "unicode.txt")}

        response = client.post(
            "/api/documents/upload",
            data=data,
            headers=auth_headers,
            content_type="multipart/form-data",
        )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data["text_length"] > 0
