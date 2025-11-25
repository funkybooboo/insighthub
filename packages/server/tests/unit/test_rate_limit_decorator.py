"""Unit tests for rate limiting decorator."""

import pytest
from unittest.mock import Mock, patch
from flask import Flask, g

from src.infrastructure.security.rate_limit_decorator import require_rate_limit


class TestRateLimitDecorator:
    """Tests for rate limiting decorator."""

    @pytest.fixture
    def app(self) -> Flask:
        """Create a test Flask application."""
        app = Flask(__name__)
        app.config["TESTING"] = True

        @app.route("/test")
        @require_rate_limit(max_requests=2, window_seconds=60)
        def test_route() -> str:
            return "OK"

        @app.route("/health")
        def health_route() -> str:
            return "OK"

        return app

    def test_decorator_without_rate_limiter(self, app: Flask) -> None:
        """Test decorator when no rate limiter is available."""
        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 200
            assert response.get_data(as_text=True) == "OK"

    def test_decorator_with_mock_rate_limiter(self, app: Flask) -> None:
        """Test decorator with mock rate limiter."""
        # Mock the rate limiter in Flask g
        mock_rate_limiter = Mock()
        mock_rate_limiter._count_requests.return_value = 1  # Under limit

        with app.test_client() as client:
            with patch.object(g, 'app_context', Mock()) as mock_ctx:
                mock_ctx.rate_limiter = mock_rate_limiter

                response = client.get("/test")
                assert response.status_code == 200
                assert response.get_data(as_text=True) == "OK"

                # Verify rate limiter was called
                mock_rate_limiter._count_requests.assert_called()

    def test_decorator_rate_limit_exceeded(self, app: Flask) -> None:
        """Test decorator when rate limit is exceeded."""
        # Mock the rate limiter in Flask g
        mock_rate_limiter = Mock()
        mock_rate_limiter._count_requests.return_value = 5  # Over limit

        with app.test_client() as client:
            with patch.object(g, 'app_context', Mock()) as mock_ctx:
                mock_ctx.rate_limiter = mock_rate_limiter

                response = client.get("/test")
                assert response.status_code == 429
                assert "Rate limit exceeded" in response.get_json()["error"]
                assert response.headers.get("Retry-After") == "60"

    def test_decorator_health_endpoints_exempt(self, app: Flask) -> None:
        """Test that health endpoints are exempt from rate limiting."""
        # Mock the rate limiter in Flask g
        mock_rate_limiter = Mock()
        mock_rate_limiter._count_requests.return_value = 10  # Way over limit

        with app.test_client() as client:
            with patch.object(g, 'app_context', Mock()) as mock_ctx:
                mock_ctx.rate_limiter = mock_rate_limiter

                # Health endpoint should not be rate limited
                response = client.get("/health")
                assert response.status_code == 200
                assert response.get_data(as_text=True) == "OK"

                # Rate limiter should not have been called
                mock_rate_limiter._count_requests.assert_not_called()

    def test_decorator_exception_handling(self, app: Flask) -> None:
        """Test decorator handles exceptions gracefully."""
        # Mock the rate limiter to raise an exception
        mock_rate_limiter = Mock()
        mock_rate_limiter._count_requests.side_effect = Exception("Test error")

        with app.test_client() as client:
            with patch.object(g, 'app_context', Mock()) as mock_ctx:
                mock_ctx.rate_limiter = mock_rate_limiter

                # Should still work despite rate limiter error
                response = client.get("/test")
                assert response.status_code == 200
                assert response.get_data(as_text=True) == "OK"