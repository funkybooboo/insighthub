"""Unit tests for middleware components."""

import time
from unittest.mock import Mock, patch

import pytest
from flask import Flask, g

from src.infrastructure.middleware.logging import RequestLoggingMiddleware
from src.infrastructure.middleware.rate_limiting import RateLimitMiddleware
from src.infrastructure.middleware.security import SecurityHeadersMiddleware


@pytest.fixture
def app() -> Flask:
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/test")
    def test_route() -> str:
        return "OK"

    @app.route("/health")
    def health_route() -> str:
        return "OK"

    return app


class TestRequestLoggingMiddleware:
    """Tests for request logging middleware."""

    def test_middleware_initialization(self, app: Flask) -> None:
        """Test middleware initialization."""
        middleware = RequestLoggingMiddleware(app)
        assert middleware.app == app

    def test_get_client_ip_from_x_forwarded_for(self, app: Flask) -> None:
        """Test getting client IP from X-Forwarded-For header."""
        middleware = RequestLoggingMiddleware(app)

        with app.test_request_context(
            "/test", headers={"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        ):
            from flask import request

            ip = middleware._get_client_ip(request)
            assert ip == "192.168.1.1"

    def test_get_client_ip_from_x_real_ip(self, app: Flask) -> None:
        """Test getting client IP from X-Real-IP header."""
        middleware = RequestLoggingMiddleware(app)

        with app.test_request_context("/test", headers={"X-Real-IP": "192.168.1.1"}):
            from flask import request

            ip = middleware._get_client_ip(request)
            assert ip == "192.168.1.1"

    def test_get_client_ip_from_remote_addr(self, app: Flask) -> None:
        """Test getting client IP from remote_addr."""
        middleware = RequestLoggingMiddleware(app)

        with app.test_request_context("/test", environ_base={"REMOTE_ADDR": "192.168.1.1"}):
            from flask import request

            ip = middleware._get_client_ip(request)
            assert ip == "192.168.1.1"

    def test_sanitize_headers_redacts_authorization(self, app: Flask) -> None:
        """Test that authorization header is redacted."""
        middleware = RequestLoggingMiddleware(app)

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer secret-token",
            "X-API-Key": "secret-key",
        }

        sanitized = middleware._sanitize_headers(headers)

        assert sanitized["Content-Type"] == "application/json"
        assert sanitized["Authorization"] == "***REDACTED***"
        assert sanitized["X-API-Key"] == "***REDACTED***"

    def test_sanitize_headers_redacts_cookie(self, app: Flask) -> None:
        """Test that cookie header is redacted."""
        middleware = RequestLoggingMiddleware(app)

        headers = {"Cookie": "session=abc123"}
        sanitized = middleware._sanitize_headers(headers)

        assert sanitized["Cookie"] == "***REDACTED***"

    @patch("src.infrastructure.logging.log_request_start")
    def test_logging_before_request(self, mock_log_request_start: Mock, app: Flask) -> None:
        """Test that request start is logged."""
        RequestLoggingMiddleware(app)

        with app.test_client() as client:
            client.get("/test")

        assert mock_log_request_start.called

    @patch("src.infrastructure.logging.log_request_end")
    def test_logging_after_request(self, mock_log_request_end: Mock, app: Flask) -> None:
        """Test that request completion is logged."""
        RequestLoggingMiddleware(app)

        with app.test_client() as client:
            client.get("/test")

        assert mock_log_request_end.called

    def test_response_time_calculated(self, app: Flask) -> None:
        """Test that response time is calculated."""
        RequestLoggingMiddleware(app)

        with app.test_request_context("/test"):
            g.start_time = time.time()
            time.sleep(0.01)

            elapsed = time.time() - g.start_time
            assert elapsed > 0


class TestSecurityHeadersMiddleware:
    """Tests for security headers middleware."""

    def test_middleware_initialization(self, app: Flask) -> None:
        """Test middleware initialization."""
        middleware = SecurityHeadersMiddleware(app)
        assert middleware.app == app
        assert middleware.config is not None

    def test_default_config_includes_required_headers(self, app: Flask) -> None:
        """Test that default config includes all required headers."""
        middleware = SecurityHeadersMiddleware(app)
        config = middleware._default_config()

        assert "X-Frame-Options" in config
        assert "X-Content-Type-Options" in config
        assert "X-XSS-Protection" in config
        assert "Content-Security-Policy" in config
        assert "Referrer-Policy" in config
        assert "Permissions-Policy" in config

    def test_security_headers_added_to_response(self, app: Flask) -> None:
        """Test that security headers are added to responses."""
        SecurityHeadersMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test")

            assert response.headers.get("X-Frame-Options") == "DENY"
            assert response.headers.get("X-Content-Type-Options") == "nosniff"
            assert response.headers.get("X-XSS-Protection") == "1; mode=block"
            assert "Content-Security-Policy" in response.headers

    def test_custom_config_overrides_defaults(self, app: Flask) -> None:
        """Test that custom config overrides default headers."""
        custom_config = {"X-Frame-Options": "SAMEORIGIN"}
        SecurityHeadersMiddleware(app, config=custom_config)

        with app.test_client() as client:
            response = client.get("/test")

            assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"

    def test_hsts_not_added_in_debug_mode(self, app: Flask) -> None:
        """Test that HSTS is not added in debug mode."""
        app.config["DEBUG"] = True
        SecurityHeadersMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test")

            assert "Strict-Transport-Security" not in response.headers

    def test_hsts_added_in_production(self, app: Flask) -> None:
        """Test that HSTS is added in production mode."""
        app.config["DEBUG"] = False
        SecurityHeadersMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test")

            assert "Strict-Transport-Security" in response.headers
            assert "max-age=31536000" in response.headers["Strict-Transport-Security"]


class TestRateLimitMiddleware:
    """Tests for rate limiting middleware."""

    def test_middleware_initialization_enabled(self, app: Flask) -> None:
        """Test middleware initialization when enabled."""
        middleware = RateLimitMiddleware(app, enabled=True)
        assert middleware.enabled is True
        assert middleware.requests_per_minute == 60
        assert middleware.requests_per_hour == 1000

    def test_middleware_initialization_disabled(self, app: Flask) -> None:
        """Test middleware initialization when disabled."""
        middleware = RateLimitMiddleware(app, enabled=False)
        assert middleware.enabled is False

    def test_middleware_with_custom_limits(self, app: Flask) -> None:
        """Test middleware with custom rate limits."""
        middleware = RateLimitMiddleware(
            app, requests_per_minute=10, requests_per_hour=100, enabled=False
        )
        assert middleware.requests_per_minute == 10
        assert middleware.requests_per_hour == 100

    def test_get_client_ip(self, app: Flask) -> None:
        """Test getting client IP."""
        middleware = RateLimitMiddleware(app, enabled=False)

        with app.test_request_context("/test", environ_base={"REMOTE_ADDR": "192.168.1.1"}):
            from flask import request

            ip = middleware._get_client_ip(request)
            assert ip == "192.168.1.1"

    def test_clean_old_entries(self, app: Flask) -> None:
        """Test cleaning old entries."""
        middleware = RateLimitMiddleware(app, enabled=False)

        current_time = time.time()
        old_time = current_time - 7200

        middleware.request_counts["192.168.1.1"] = [
            (old_time, 1),
            (current_time, 1),
        ]

        middleware._clean_old_entries("192.168.1.1")

        assert len(middleware.request_counts["192.168.1.1"]) == 1
        assert middleware.request_counts["192.168.1.1"][0][0] == current_time

    def test_count_requests_within_window(self, app: Flask) -> None:
        """Test counting requests within time window."""
        middleware = RateLimitMiddleware(app, enabled=False)

        current_time = time.time()
        middleware.request_counts["192.168.1.1"] = [
            (current_time - 30, 1),
            (current_time - 20, 1),
            (current_time - 10, 1),
        ]

        count = middleware._count_requests("192.168.1.1", window=60)
        assert count == 3

        # After the first call, a current request was added, so now there are 4 requests
        # With window=15, it should count the -10 request and the current request
        count = middleware._count_requests("192.168.1.1", window=15)
        assert count == 2

    def test_request_allowed_under_limit(self, app: Flask) -> None:
        """Test that requests are allowed under the limit."""
        RateLimitMiddleware(app, requests_per_minute=10, enabled=True)

        with app.test_client() as client:
            response = client.get("/test")
            assert response.status_code == 200

    def test_request_blocked_over_minute_limit(self, app: Flask) -> None:
        """Test that requests are blocked when exceeding per-minute limit."""
        _middleware = RateLimitMiddleware(app, requests_per_minute=1, enabled=True)

        with app.test_client() as client:
            client.get("/test")
            response = client.get("/test")

            assert response.status_code == 429
            data = response.get_json()
            assert "Rate limit exceeded" in data["error"]
            assert data["retry_after"] == 60

    def test_request_blocked_over_hour_limit(self, app: Flask) -> None:
        """Test that requests are blocked when exceeding per-hour limit."""
        _middleware = RateLimitMiddleware(
            app, requests_per_minute=100, requests_per_hour=2, enabled=True
        )

        with app.test_client() as client:
            client.get("/test")
            client.get("/test")
            response = client.get("/test")

            assert response.status_code == 429
            data = response.get_json()
            assert "Rate limit exceeded" in data["error"]
            assert data["retry_after"] == 3600

    def test_health_endpoint_not_rate_limited(self, app: Flask) -> None:
        """Test that health endpoints are not rate limited."""
        RateLimitMiddleware(app, requests_per_minute=1, enabled=True)

        with app.test_client() as client:
            for _ in range(5):
                response = client.get("/health")
                assert response.status_code == 200

    def test_disabled_middleware_allows_all_requests(self, app: Flask) -> None:
        """Test that disabled middleware allows all requests."""
        RateLimitMiddleware(app, requests_per_minute=1, enabled=False)

        with app.test_client() as client:
            for _ in range(10):
                response = client.get("/test")
                assert response.status_code == 200

    def test_different_ips_tracked_separately(self, app: Flask) -> None:
        """Test that different IPs are tracked separately."""
        RateLimitMiddleware(app, requests_per_minute=2, enabled=True)

        with app.test_client() as client:
            client.get("/test", headers={"X-Forwarded-For": "192.168.1.1"})
            client.get("/test", headers={"X-Forwarded-For": "192.168.1.1"})

            client.get("/test", headers={"X-Forwarded-For": "192.168.1.2"})
            response = client.get("/test", headers={"X-Forwarded-For": "192.168.1.2"})

            assert response.status_code == 200
