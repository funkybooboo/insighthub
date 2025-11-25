"""Unit tests for SecurityHeadersMiddleware."""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from src.infrastructure.middleware.security import SecurityHeadersMiddleware


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware."""

    @pytest.fixture
    def app(self) -> Flask:
        """Create a test Flask app."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def mock_logger(self) -> MagicMock:
        """Mock logger."""
        return MagicMock()

    def test_init_sets_up_middleware(self, app: Flask) -> None:
        """init sets up security headers middleware on app."""
        with patch("src.infrastructure.middleware.security.logger") as mock_logger:
            middleware = SecurityHeadersMiddleware(app)

            # Verify logger was called
            mock_logger.info.assert_called_once_with("Security headers middleware initialized")

            # Verify middleware has app reference
            assert middleware.app == app

    def test_default_config_contains_expected_headers(self, app: Flask) -> None:
        """_default_config returns expected security headers."""
        middleware = SecurityHeadersMiddleware(app)

        config = middleware._default_config()

        # Check that all expected headers are present
        expected_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Content-Security-Policy",
            "Referrer-Policy",
            "Permissions-Policy",
        ]

        for header in expected_headers:
            assert header in config
            assert isinstance(config[header], str)
            assert len(config[header]) > 0

    def test_default_config_csp_includes_connect_src(self, app: Flask) -> None:
        """_default_config CSP includes connect-src directive."""
        middleware = SecurityHeadersMiddleware(app)

        config = middleware._default_config()
        csp = config["Content-Security-Policy"]

        assert "connect-src" in csp

    def test_custom_config_overrides_defaults(self, app: Flask) -> None:
        """Custom config overrides default headers."""
        custom_config = {"X-Frame-Options": "SAMEORIGIN", "Custom-Header": "custom-value"}

        middleware = SecurityHeadersMiddleware(app, custom_config)

        assert middleware.config["X-Frame-Options"] == "SAMEORIGIN"
        assert middleware.config["Custom-Header"] == "custom-value"

    @patch("src.config.CORS_ORIGINS", ["https://example.com", "https://api.example.com"])
    def test_default_config_includes_cors_origins_in_csp(self, app: Flask) -> None:
        """_default_config includes CORS origins in CSP when configured."""
        middleware = SecurityHeadersMiddleware(app)

        config = middleware._default_config()
        csp = config["Content-Security-Policy"]

        assert "https://example.com" in csp
        assert "https://api.example.com" in csp

    @patch("src.config.CORS_ORIGINS", ["*"])
    def test_default_config_handles_wildcard_cors(self, app: Flask) -> None:
        """_default_config handles wildcard CORS origins."""
        middleware = SecurityHeadersMiddleware(app)

        config = middleware._default_config()
        csp = config["Content-Security-Policy"]

        # Should include localhost ports for development
        assert "http://localhost:*" in csp
        assert "ws://localhost:*" in csp
        assert "wss://localhost:*" in csp

    def test_setup_security_headers_registers_after_request_handler(self, app: Flask) -> None:
        """setup_security_headers registers after_request handler."""
        SecurityHeadersMiddleware(app)

        # Check that after_request handlers were registered
        assert len(app.after_request_funcs[None]) > 0

    def test_after_request_handler_adds_security_headers(self, app: Flask) -> None:
        """after_request handler adds security headers to response."""
        SecurityHeadersMiddleware(app)

        with app.test_request_context():
            # Simulate a response
            response = app.response_class("test response", 200)

            # Get the after_request handler
            handler = app.after_request_funcs[None][0]

            # Call the handler
            result = handler(response)

            # In Flask, after_request handlers return the response
            assert result is response
            from flask import Response

            assert isinstance(result, Response)

            csp = result.headers["Content-Security-Policy"]  # type: ignore

            # Should start with restrictive default-src
            assert csp.startswith("default-src 'self'")

    def test_csp_allows_unsafe_inline_for_compatibility(self, app: Flask) -> None:
        """Content-Security-Policy allows unsafe-inline for compatibility."""
        SecurityHeadersMiddleware(app)

        with app.test_request_context():
            response = app.response_class("test response", 200)

            handler = app.after_request_funcs[None][0]
            result = handler(response)

            # In Flask, after_request handlers return the response
            assert result is response

            csp = result.headers["Content-Security-Policy"]  # type: ignore

            # Should allow unsafe-inline for script and style (common in SPAs)
            assert "'unsafe-inline'" in csp
            assert "script-src 'self' 'unsafe-inline' 'unsafe-eval'" in csp
            assert "style-src 'self' 'unsafe-inline'" in csp

    def test_middleware_handles_multiple_requests(self, app: Flask) -> None:
        """Middleware handles multiple requests correctly."""
        SecurityHeadersMiddleware(app)

        # Simulate multiple requests
        for i in range(3):
            with app.test_request_context(f"/test{i}"):
                response = app.response_class(f"response {i}", 200)

                handler = app.after_request_funcs[None][0]
                result = handler(response)

                # In Flask, after_request handlers return the response
                assert result is response

                # Each response should have security headers
                assert "X-Frame-Options" in result.headers  # type: ignore
                assert result.headers["X-Frame-Options"] == "DENY"  # type: ignore

    def test_custom_config_preserves_custom_headers(self, app: Flask) -> None:
        """Custom config preserves custom headers through requests."""
        custom_config = {"X-Custom-Security": "custom-value", "X-Another-Header": "another-value"}

        SecurityHeadersMiddleware(app, custom_config)

        with app.test_request_context():
            response = app.response_class("test response", 200)

            handler = app.after_request_funcs[None][0]
            result = handler(response)

            # In Flask, after_request handlers return the response
            assert result is response

            # Custom headers should be present
            assert result.headers["X-Custom-Security"] == "custom-value"  # type: ignore
            assert result.headers["X-Another-Header"] == "another-value"  # type: ignore

    def test_middleware_works_with_different_response_types(self, app: Flask) -> None:
        """Middleware works with different response types."""
        SecurityHeadersMiddleware(app)

        # Test with different response codes
        for status_code in [200, 201, 400, 404, 500]:
            with app.test_request_context():
                response = app.response_class("test response", status_code)

                handler = app.after_request_funcs[None][0]
                result = handler(response)

                # In Flask, after_request handlers return the response
                assert result is response

                # Security headers should be added regardless of status
                assert "X-Frame-Options" in result.headers  # type: ignore
                assert result.status_code == status_code  # type: ignore
