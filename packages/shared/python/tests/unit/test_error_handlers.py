"""Unit tests for error handlers."""

import pytest
from flask import Flask
from werkzeug.exceptions import BadRequest

from packages.shared.python.src.shared.errors import (
    AlreadyExistsError,
    ConflictError,
    DomainException,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from packages.shared.python.src.shared.errors import ErrorResponse
from packages.shared.python.src.shared.errors import register_error_handlers


@pytest.fixture
def app() -> Flask:
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    register_error_handlers(app)

    @app.route("/test/domain-exception")
    def test_domain_exception() -> str:
        raise DomainException("Test domain error", status_code=500)

    @app.route("/test/validation-error")
    def test_validation_error() -> str:
        raise ValidationError("Invalid input")

    @app.route("/test/not-found-error")
    def test_not_found_error() -> str:
        raise NotFoundError("User", 123)

    @app.route("/test/already-exists-error")
    def test_already_exists_error() -> str:
        raise AlreadyExistsError("User", "john@example.com")

    @app.route("/test/unauthorized-error")
    def test_unauthorized_error() -> str:
        raise UnauthorizedError()

    @app.route("/test/forbidden-error")
    def test_forbidden_error() -> str:
        raise ForbiddenError()

    @app.route("/test/conflict-error")
    def test_conflict_error() -> str:
        raise ConflictError("Resource is locked")

    @app.route("/test/http-exception")
    def test_http_exception() -> str:
        raise BadRequest("Bad request error")

    @app.route("/test/generic-exception")
    def test_generic_exception() -> str:
        raise Exception("Unexpected error")

    return app


class TestErrorResponse:
    """Tests for ErrorResponse DTO."""

    def test_from_exception_creates_response(self) -> None:
        """Test creating ErrorResponse from exception."""
        exception = ValueError("Test error")
        response = ErrorResponse.from_exception(exception, status_code=400)

        assert response.error == "ValueError"
        assert response.message == "Test error"
        assert response.status_code == 400
        assert "T" in response.timestamp
        assert "Z" in response.timestamp

    def test_to_dict_converts_to_dictionary(self) -> None:
        """Test converting ErrorResponse to dictionary."""
        response = ErrorResponse(
            error="TestError",
            message="Test message",
            status_code=500,
            timestamp="2024-01-01T00:00:00Z",
        )

        result = response.to_dict()

        assert result["error"] == "TestError"
        assert result["message"] == "Test message"
        assert result["status_code"] == 500
        assert result["timestamp"] == "2024-01-01T00:00:00Z"

    def test_from_exception_different_types(self) -> None:
        """Test ErrorResponse with different exception types."""
        exceptions = [
            (ValueError("value error"), 400),
            (RuntimeError("runtime error"), 500),
            (KeyError("key error"), 404),
        ]

        for exception, status_code in exceptions:
            response = ErrorResponse.from_exception(exception, status_code)
            assert response.error == exception.__class__.__name__
            assert response.status_code == status_code


class TestDomainExceptionHandler:
    """Tests for domain exception handling."""

    def test_validation_error_returns_400(self, app: Flask) -> None:
        """Test that ValidationError returns 400."""
        with app.test_client() as client:
            response = client.get("/test/validation-error")

            assert response.status_code == 400
            data = response.get_json()
            assert data["error"] == "ValidationError"
            assert data["message"] == "Invalid input"
            assert data["status_code"] == 400

    def test_not_found_error_returns_404(self, app: Flask) -> None:
        """Test that NotFoundError returns 404."""
        with app.test_client() as client:
            response = client.get("/test/not-found-error")

            assert response.status_code == 404
            data = response.get_json()
            assert data["error"] == "NotFoundError"
            assert "User with id '123' not found" in data["message"]
            assert data["status_code"] == 404

    def test_already_exists_error_returns_409(self, app: Flask) -> None:
        """Test that AlreadyExistsError returns 409."""
        with app.test_client() as client:
            response = client.get("/test/already-exists-error")

            assert response.status_code == 409
            data = response.get_json()
            assert data["error"] == "AlreadyExistsError"
            assert "already exists" in data["message"]
            assert data["status_code"] == 409

    def test_unauthorized_error_returns_401(self, app: Flask) -> None:
        """Test that UnauthorizedError returns 401."""
        with app.test_client() as client:
            response = client.get("/test/unauthorized-error")

            assert response.status_code == 401
            data = response.get_json()
            assert data["error"] == "UnauthorizedError"
            assert data["status_code"] == 401

    def test_forbidden_error_returns_403(self, app: Flask) -> None:
        """Test that ForbiddenError returns 403."""
        with app.test_client() as client:
            response = client.get("/test/forbidden-error")

            assert response.status_code == 403
            data = response.get_json()
            assert data["error"] == "ForbiddenError"
            assert data["status_code"] == 403

    def test_conflict_error_returns_409(self, app: Flask) -> None:
        """Test that ConflictError returns 409."""
        with app.test_client() as client:
            response = client.get("/test/conflict-error")

            assert response.status_code == 409
            data = response.get_json()
            assert data["error"] == "ConflictError"
            assert data["message"] == "Resource is locked"
            assert data["status_code"] == 409

    def test_domain_exception_includes_timestamp(self, app: Flask) -> None:
        """Test that error responses include timestamps."""
        with app.test_client() as client:
            response = client.get("/test/validation-error")
            data = response.get_json()

            assert "timestamp" in data
            assert isinstance(data["timestamp"], str)


class TestHTTPExceptionHandler:
    """Tests for HTTP exception handling."""

    def test_http_bad_request_returns_400(self, app: Flask) -> None:
        """Test that HTTP BadRequest returns 400."""
        with app.test_client() as client:
            response = client.get("/test/http-exception")

            assert response.status_code == 400
            data = response.get_json()
            assert data["error"] == "BadRequest"
            assert data["status_code"] == 400

    def test_http_exception_includes_message(self, app: Flask) -> None:
        """Test that HTTP exceptions include error message."""
        with app.test_client() as client:
            response = client.get("/test/http-exception")
            data = response.get_json()

            assert "message" in data
            assert isinstance(data["message"], str)


class TestGenericExceptionHandler:
    """Tests for generic exception handling."""

    def test_generic_exception_returns_500(self, app: Flask) -> None:
        """Test that generic exceptions return 500."""
        with app.test_client() as client:
            response = client.get("/test/generic-exception")

            assert response.status_code == 500
            data = response.get_json()
            assert data["error"] == "InternalServerError"
            assert data["status_code"] == 500

    def test_generic_exception_hides_details(self, app: Flask) -> None:
        """Test that generic exceptions don't leak implementation details."""
        with app.test_client() as client:
            response = client.get("/test/generic-exception")
            data = response.get_json()

            assert "Unexpected error" not in data["message"]
            assert "unexpected error occurred" in data["message"].lower()

    def test_generic_exception_includes_timestamp(self, app: Flask) -> None:
        """Test that generic exception responses include timestamps."""
        with app.test_client() as client:
            response = client.get("/test/generic-exception")
            data = response.get_json()

            assert "timestamp" in data
            assert isinstance(data["timestamp"], str)


class TestDomainExceptionClasses:
    """Tests for domain exception classes."""

    def test_validation_error_has_400_status(self) -> None:
        """Test that ValidationError has 400 status code."""
        error = ValidationError("Invalid input")
        assert error.status_code == 400
        assert error.message == "Invalid input"

    def test_not_found_error_has_404_status(self) -> None:
        """Test that NotFoundError has 404 status code."""
        error = NotFoundError("Document", 123)
        assert error.status_code == 404
        assert error.resource_type == "Document"
        assert error.identifier == 123

    def test_already_exists_error_has_409_status(self) -> None:
        """Test that AlreadyExistsError has 409 status code."""
        error = AlreadyExistsError("User", "test@example.com")
        assert error.status_code == 409
        assert error.resource_type == "User"
        assert error.identifier == "test@example.com"

    def test_unauthorized_error_has_401_status(self) -> None:
        """Test that UnauthorizedError has 401 status code."""
        error = UnauthorizedError()
        assert error.status_code == 401
        assert "Authentication required" in error.message

    def test_forbidden_error_has_403_status(self) -> None:
        """Test that ForbiddenError has 403 status code."""
        error = ForbiddenError()
        assert error.status_code == 403
        assert "Permission denied" in error.message

    def test_conflict_error_has_409_status(self) -> None:
        """Test that ConflictError has 409 status code."""
        error = ConflictError("Cannot delete locked resource")
        assert error.status_code == 409
        assert error.message == "Cannot delete locked resource"

    def test_custom_error_messages(self) -> None:
        """Test that custom error messages work correctly."""
        error1 = UnauthorizedError("Token expired")
        error2 = ForbiddenError("Admin access required")

        assert error1.message == "Token expired"
        assert error2.message == "Admin access required"
