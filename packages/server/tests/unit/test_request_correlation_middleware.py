"""Unit tests for RequestCorrelationMiddleware."""

import pytest
from flask import Flask, g

from src.infrastructure.middleware.request_correlation import RequestCorrelationMiddleware


class TestRequestCorrelationMiddleware:
    """Tests for request correlation middleware."""

    @pytest.fixture
    def app(self) -> Flask:
        """Create a test Flask application."""
        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.route("/test")
        def test_route() -> str:
            return "OK"

        return app

    def test_middleware_initialization(self, app: Flask) -> None:
        """Test middleware initialization."""
        middleware = RequestCorrelationMiddleware(app)
        assert middleware.app == app
        assert middleware.header_name == "X-Request-ID"

    def test_custom_header_name(self, app: Flask) -> None:
        """Test middleware with custom header name."""
        middleware = RequestCorrelationMiddleware(app, header_name="X-Correlation-ID")
        assert middleware.header_name == "X-Correlation-ID"

    def test_correlation_id_generation(self, app: Flask) -> None:
        """Test that correlation ID is generated for requests."""
        RequestCorrelationMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test")
            assert "X-Request-ID" in response.headers
            correlation_id = response.headers["X-Request-ID"]
            assert len(correlation_id) > 0

    def test_correlation_id_from_header(self, app: Flask) -> None:
        """Test that correlation ID from request header is used."""
        RequestCorrelationMiddleware(app)

        with app.test_client() as client:
            custom_id = "custom-correlation-id-123"
            response = client.get("/test", headers={"X-Request-ID": custom_id})
            assert response.headers["X-Request-ID"] == custom_id

    def test_correlation_id_in_flask_g(self, app: Flask) -> None:
        """Test that correlation ID is stored in Flask g object."""
        RequestCorrelationMiddleware(app)

        @app.route("/check_g")
        def check_g() -> str:
            correlation_id = getattr(g, "correlation_id", None)
            return correlation_id or "None"

        with app.test_client() as client:
            response = client.get("/check_g")
            correlation_id = response.headers["X-Request-ID"]
            assert correlation_id in response.get_data(as_text=True)

    def test_correlation_id_uniqueness(self, app: Flask) -> None:
        """Test that correlation IDs are unique across requests."""
        RequestCorrelationMiddleware(app)

        with app.test_client() as client:
            response1 = client.get("/test")
            response2 = client.get("/test")

            id1 = response1.headers["X-Request-ID"]
            id2 = response2.headers["X-Request-ID"]

            assert id1 != id2
            assert len(id1) > 0
            assert len(id2) > 0

    def test_correlation_id_persistence_across_requests(self, app: Flask) -> None:
        """Test that correlation ID persists across multiple requests from same client."""
        RequestCorrelationMiddleware(app)

        with app.test_client() as client:
            # First request
            response1 = client.get("/test")
            id1 = response1.headers["X-Request-ID"]

            # Second request from same client
            response2 = client.get("/test", headers={"X-Request-ID": id1})
            id2 = response2.headers["X-Request-ID"]

            assert id1 == id2

    def test_middleware_with_exception_handling(self, app: Flask) -> None:
        """Test that middleware handles exceptions gracefully."""
        RequestCorrelationMiddleware(app)

        @app.route("/error")
        def error_route() -> str:
            raise Exception("Test error")

        with app.test_client() as client:
            response = client.get("/error")
            # Should still have correlation ID header even on error
            assert "X-Request-ID" in response.headers

    def test_get_correlation_id_static_method(self, app: Flask) -> None:
        """Test the static get_correlation_id method."""
        middleware = RequestCorrelationMiddleware(app)

        # Without request context
        correlation_id = middleware.get_correlation_id()
        assert correlation_id is None

        # With request context
        with app.test_request_context("/test"):
            # Should generate ID
            correlation_id = middleware.get_correlation_id()
            assert correlation_id is not None
            assert len(correlation_id) > 0
