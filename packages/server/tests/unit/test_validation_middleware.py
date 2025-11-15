"""Unit tests for request validation middleware."""

import json

import pytest
from flask import Flask

from src.infrastructure.middleware.validation import RequestValidationMiddleware


@pytest.fixture
def app() -> Flask:
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/test", methods=["GET", "POST", "PUT", "PATCH"])
    def test_route() -> str:
        return "OK"

    @app.route("/health")
    def health_route() -> str:
        return "OK"

    @app.route("/api/data", methods=["POST"])
    def api_data() -> dict[str, str]:
        return {"status": "success"}

    return app


class TestRequestValidationMiddleware:
    """Tests for request validation middleware."""

    def test_middleware_initialization(self, app: Flask) -> None:
        """Test middleware initialization."""
        middleware = RequestValidationMiddleware(app)
        assert middleware.app == app
        assert middleware.max_content_length == 16 * 1024 * 1024
        assert "application/json" in middleware.allowed_content_types

    def test_middleware_custom_max_content_length(self, app: Flask) -> None:
        """Test middleware with custom max content length."""
        middleware = RequestValidationMiddleware(app, max_content_length=1024)
        assert middleware.max_content_length == 1024

    def test_middleware_custom_allowed_content_types(self, app: Flask) -> None:
        """Test middleware with custom allowed content types."""
        custom_types = ["application/json", "text/xml"]
        middleware = RequestValidationMiddleware(app, allowed_content_types=custom_types)
        assert middleware.allowed_content_types == custom_types


class TestContentLengthValidation:
    """Tests for content length validation."""

    def test_request_within_size_limit_allowed(self, app: Flask) -> None:
        """Test that requests within size limit are allowed."""
        RequestValidationMiddleware(app, max_content_length=1000)

        with app.test_client() as client:
            data = {"message": "test"}
            response = client.post(
                "/test",
                data=json.dumps(data),
                content_type="application/json",
                headers={"Content-Length": "50"},
            )
            assert response.status_code == 200

    def test_request_exceeding_size_limit_rejected(self, app: Flask) -> None:
        """Test that requests exceeding size limit are rejected."""
        RequestValidationMiddleware(app, max_content_length=100)

        with app.test_client() as client:
            response = client.post(
                "/test",
                data="x" * 200,
                content_type="text/plain",
                headers={"Content-Length": "200"},
            )
            assert response.status_code == 413
            data = response.get_json()
            assert "too large" in data["error"].lower()
            assert data["max_size_bytes"] == 100

    def test_request_without_content_length_allowed(self, app: Flask) -> None:
        """Test that requests without Content-Length header are allowed."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 200


class TestContentTypeValidation:
    """Tests for content type validation."""

    def test_allowed_json_content_type(self, app: Flask) -> None:
        """Test that JSON content type is allowed."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.post(
                "/test",
                data=json.dumps({"key": "value"}),
                content_type="application/json",
            )
            assert response.status_code == 200

    def test_allowed_multipart_form_data(self, app: Flask) -> None:
        """Test that multipart/form-data is allowed."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.post(
                "/test",
                data={"key": "value"},
                content_type="multipart/form-data",
            )
            assert response.status_code == 200

    def test_allowed_form_urlencoded(self, app: Flask) -> None:
        """Test that form-urlencoded is allowed."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.post(
                "/test",
                data={"key": "value"},
                content_type="application/x-www-form-urlencoded",
            )
            assert response.status_code == 200

    def test_disallowed_content_type_rejected(self, app: Flask) -> None:
        """Test that disallowed content types are rejected."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.post("/test", data="test", content_type="application/xml")
            assert response.status_code == 415
            data = response.get_json()
            assert "Unsupported Content-Type" in data["error"]

    def test_content_type_with_charset_allowed(self, app: Flask) -> None:
        """Test that content type with charset is allowed."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.post(
                "/test",
                data=json.dumps({"key": "value"}),
                content_type="application/json; charset=utf-8",
            )
            assert response.status_code == 200

    def test_get_request_no_content_type_validation(self, app: Flask) -> None:
        """Test that GET requests skip content type validation."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 200


class TestJSONValidation:
    """Tests for JSON payload validation."""

    def test_valid_json_payload_accepted(self, app: Flask) -> None:
        """Test that valid JSON payload is accepted."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.post(
                "/test",
                data=json.dumps({"key": "value"}),
                content_type="application/json",
            )
            assert response.status_code == 200

    def test_invalid_json_payload_rejected(self, app: Flask) -> None:
        """Test that invalid JSON payload is rejected."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.post(
                "/test",
                data='{"invalid": json}',
                content_type="application/json",
            )
            assert response.status_code == 400
            data = response.get_json()
            assert "Invalid JSON payload" in data["error"]

    def test_empty_json_payload_accepted(self, app: Flask) -> None:
        """Test that empty JSON payload is accepted."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.post("/test", data="", content_type="application/json")
            assert response.status_code == 200

    def test_malformed_json_rejected(self, app: Flask) -> None:
        """Test that malformed JSON is rejected."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.post(
                "/test",
                data='{"key": "value",}',
                content_type="application/json",
            )
            assert response.status_code == 400


class TestPathTraversalPrevention:
    """Tests for path traversal attack prevention."""

    def test_normal_path_allowed(self, app: Flask) -> None:
        """Test that normal paths are allowed."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 200

    def test_path_traversal_with_dotdot_slash_blocked(self, app: Flask) -> None:
        """Test that ../ pattern is blocked."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test/../etc/passwd")
            assert response.status_code == 400
            data = response.get_json()
            assert "Invalid request path" in data["error"]

    def test_path_traversal_with_dotdot_backslash_blocked(self, app: Flask) -> None:
        r"""Test that ..\ pattern is blocked."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test/..\\etc\\passwd")
            assert response.status_code == 400

    def test_path_traversal_encoded_blocked(self, app: Flask) -> None:
        """Test that encoded path traversal patterns are blocked."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test/%2e%2e/etc/passwd")
            assert response.status_code == 400

    def test_path_traversal_double_encoded_blocked(self, app: Flask) -> None:
        """Test that double-encoded path traversal is blocked."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test/%252e%252e/etc/passwd")
            assert response.status_code == 400


class TestSkippedValidation:
    """Tests for validation skipping."""

    def test_health_endpoint_skips_validation(self, app: Flask) -> None:
        """Test that health endpoints skip validation."""
        RequestValidationMiddleware(app, max_content_length=10)

        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200

    def test_options_request_skips_validation(self, app: Flask) -> None:
        """Test that OPTIONS requests skip validation."""
        RequestValidationMiddleware(app)

        with app.test_client() as client:
            response = client.options("/test")
            assert response.status_code == 200


class TestContainsPathTraversal:
    """Tests for _contains_path_traversal helper method."""

    def test_normal_path_not_flagged(self, app: Flask) -> None:
        """Test that normal paths are not flagged."""
        middleware = RequestValidationMiddleware(app)

        assert middleware._contains_path_traversal("/api/users") is False
        assert middleware._contains_path_traversal("/test/data") is False

    def test_dotdot_slash_detected(self, app: Flask) -> None:
        """Test that ../ is detected."""
        middleware = RequestValidationMiddleware(app)

        assert middleware._contains_path_traversal("/test/../etc") is True
        assert middleware._contains_path_traversal("../etc/passwd") is True

    def test_dotdot_backslash_detected(self, app: Flask) -> None:
        r"""Test that ..\ is detected."""
        middleware = RequestValidationMiddleware(app)

        assert middleware._contains_path_traversal("/test/..\\etc") is True

    def test_encoded_traversal_detected(self, app: Flask) -> None:
        """Test that encoded traversal patterns are detected."""
        middleware = RequestValidationMiddleware(app)

        assert middleware._contains_path_traversal("/test/%2e%2e/etc") is True
        assert middleware._contains_path_traversal("/test/%252e/etc") is True

    def test_case_insensitive_detection(self, app: Flask) -> None:
        """Test that detection is case-insensitive."""
        middleware = RequestValidationMiddleware(app)

        assert middleware._contains_path_traversal("/TEST/%2E%2E/etc") is True
