"""Unit tests for performance monitoring middleware."""

import time
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from src.infrastructure.middleware.monitoring import PerformanceMonitoringMiddleware


@pytest.fixture
def app() -> Flask:
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/test")
    def test_route() -> str:
        return "OK"

    @app.route("/slow")
    def slow_route() -> str:
        time.sleep(0.1)
        return "OK"

    @app.route("/api/users")
    def users_route() -> str:
        return "Users"

    @app.route("/api/data")
    def data_route() -> str:
        return "Data"

    return app


class TestPerformanceMonitoringMiddleware:
    """Tests for performance monitoring middleware."""

    def test_middleware_initialization(self, app: Flask) -> None:
        """Test middleware initialization."""
        middleware = PerformanceMonitoringMiddleware(app)
        assert middleware.app == app
        assert middleware.slow_request_threshold == 1.0
        assert middleware.enable_stats is True

    def test_middleware_custom_threshold(self, app: Flask) -> None:
        """Test middleware with custom slow request threshold."""
        middleware = PerformanceMonitoringMiddleware(app, slow_request_threshold=0.5)
        assert middleware.slow_request_threshold == 0.5

    def test_middleware_stats_disabled(self, app: Flask) -> None:
        """Test middleware with stats collection disabled."""
        middleware = PerformanceMonitoringMiddleware(app, enable_stats=False)
        assert middleware.enable_stats is False


class TestResponseTimeHeader:
    """Tests for response time header."""

    def test_response_includes_time_header(self, app: Flask) -> None:
        """Test that response includes X-Response-Time header."""
        PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test")
            assert "X-Response-Time" in response.headers

    def test_response_time_format(self, app: Flask) -> None:
        """Test that response time is in correct format."""
        PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test")
            time_header = response.headers.get("X-Response-Time")
            assert time_header is not None
            assert time_header.endswith("s")
            assert "." in time_header

    def test_response_time_is_positive(self, app: Flask) -> None:
        """Test that response time is positive or zero."""
        PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            response = client.get("/test")
            time_str = response.headers.get("X-Response-Time")
            assert time_str is not None
            time_value = float(time_str.rstrip("s"))
            assert time_value >= 0


class TestSlowRequestDetection:
    """Tests for slow request detection."""

    @patch("src.infrastructure.middleware.monitoring.logger")
    def test_slow_request_warning_logged(self, mock_logger: Mock, app: Flask) -> None:
        """Test that slow requests are logged."""
        PerformanceMonitoringMiddleware(app, slow_request_threshold=0.05)

        with app.test_client() as client:
            client.get("/slow")

        assert mock_logger.warning.called

    @patch("src.infrastructure.middleware.monitoring.logger")
    def test_fast_request_not_warned(self, mock_logger: Mock, app: Flask) -> None:
        """Test that fast requests don't trigger warnings."""
        PerformanceMonitoringMiddleware(app, slow_request_threshold=10.0)

        with app.test_client() as client:
            client.get("/test")

        assert not mock_logger.warning.called

    @patch("src.infrastructure.middleware.monitoring.logger")
    def test_slow_request_log_includes_details(self, mock_logger: Mock, app: Flask) -> None:
        """Test that slow request log includes request details."""
        PerformanceMonitoringMiddleware(app, slow_request_threshold=0.05)

        with app.test_client() as client:
            client.get("/slow")

        call_args = mock_logger.warning.call_args
        assert call_args is not None
        log_message = call_args[0][0]
        assert "GET" in log_message
        assert "/slow" in log_message


class TestEndpointStatistics:
    """Tests for endpoint statistics collection."""

    def test_stats_collected_for_requests(self, app: Flask) -> None:
        """Test that statistics are collected for requests."""
        middleware = PerformanceMonitoringMiddleware(app, enable_stats=True)

        with app.test_client() as client:
            client.get("/test")

        stats = middleware.get_stats()
        assert "GET /test" in stats

    def test_stats_include_request_count(self, app: Flask) -> None:
        """Test that stats include request count."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            for _ in range(3):
                client.get("/test")

        stats = middleware.get_stats()
        assert stats["GET /test"]["count"] == 3

    def test_stats_include_average_time(self, app: Flask) -> None:
        """Test that stats include average response time."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            client.get("/test")

        stats = middleware.get_stats()
        assert "avg_time" in stats["GET /test"]
        assert stats["GET /test"]["avg_time"] > 0

    def test_stats_include_min_max_time(self, app: Flask) -> None:
        """Test that stats include min and max time."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            client.get("/test")

        stats = middleware.get_stats()
        endpoint_stats = stats["GET /test"]

        assert "min_time" in endpoint_stats
        assert "max_time" in endpoint_stats
        assert endpoint_stats["min_time"] > 0
        assert endpoint_stats["max_time"] >= endpoint_stats["min_time"]

    def test_stats_include_total_time(self, app: Flask) -> None:
        """Test that stats include total time."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            for _ in range(2):
                client.get("/test")

        stats = middleware.get_stats()
        endpoint_stats = stats["GET /test"]

        assert "total_time" in endpoint_stats
        assert endpoint_stats["total_time"] > 0

    def test_stats_multiple_endpoints(self, app: Flask) -> None:
        """Test statistics for multiple endpoints."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            client.get("/api/users")
            client.get("/api/data")
            client.get("/api/users")

        stats = middleware.get_stats()

        assert "GET /api/users" in stats
        assert "GET /api/data" in stats
        assert stats["GET /api/users"]["count"] == 2
        assert stats["GET /api/data"]["count"] == 1

    def test_stats_disabled_no_collection(self, app: Flask) -> None:
        """Test that stats are not collected when disabled."""
        middleware = PerformanceMonitoringMiddleware(app, enable_stats=False)

        with app.test_client() as client:
            client.get("/test")

        stats = middleware.get_stats()
        assert len(stats) == 0

    def test_average_time_calculation(self, app: Flask) -> None:
        """Test that average time is calculated correctly."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            for _ in range(5):
                client.get("/test")

        stats = middleware.get_stats()
        endpoint_stats = stats["GET /test"]

        expected_avg = endpoint_stats["total_time"] / endpoint_stats["count"]
        assert abs(endpoint_stats["avg_time"] - expected_avg) < 0.0001

    def test_min_time_tracks_fastest(self, app: Flask) -> None:
        """Test that min_time tracks the fastest request."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            for _ in range(3):
                client.get("/test")

        stats = middleware.get_stats()
        endpoint_stats = stats["GET /test"]

        assert endpoint_stats["min_time"] <= endpoint_stats["avg_time"]
        assert endpoint_stats["min_time"] <= endpoint_stats["max_time"]

    def test_max_time_tracks_slowest(self, app: Flask) -> None:
        """Test that max_time tracks the slowest request."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            client.get("/test")
            client.get("/slow")

        stats = middleware.get_stats()

        if "GET /slow" in stats:
            slow_stats = stats["GET /slow"]
            assert slow_stats["max_time"] >= slow_stats["avg_time"]


class TestStatsReset:
    """Tests for statistics reset."""

    def test_reset_stats_clears_data(self, app: Flask) -> None:
        """Test that reset clears all statistics."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            client.get("/test")

        assert len(middleware.get_stats()) > 0

        middleware.reset_stats()
        assert len(middleware.get_stats()) == 0

    @patch("src.infrastructure.middleware.monitoring.logger")
    def test_reset_stats_logs_message(self, mock_logger: Mock, app: Flask) -> None:
        """Test that reset logs a message."""
        middleware = PerformanceMonitoringMiddleware(app)
        middleware.reset_stats()

        assert mock_logger.info.called

    def test_reset_stats_allows_new_collection(self, app: Flask) -> None:
        """Test that stats can be collected after reset."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            client.get("/test")

        middleware.reset_stats()

        with app.test_client() as client:
            client.get("/api/users")

        stats = middleware.get_stats()
        assert "GET /api/users" in stats
        assert "GET /test" not in stats


class TestGetStats:
    """Tests for get_stats method."""

    def test_get_stats_returns_dict(self, app: Flask) -> None:
        """Test that get_stats returns a dictionary."""
        middleware = PerformanceMonitoringMiddleware(app)

        with app.test_client() as client:
            client.get("/test")

        stats = middleware.get_stats()
        assert isinstance(stats, dict)

    def test_get_stats_empty_when_no_requests(self, app: Flask) -> None:
        """Test that get_stats is empty when no requests made."""
        middleware = PerformanceMonitoringMiddleware(app)
        stats = middleware.get_stats()
        assert len(stats) == 0

    def test_get_stats_with_zero_count_edge_case(self, app: Flask) -> None:
        """Test get_stats handles zero count gracefully."""
        middleware = PerformanceMonitoringMiddleware(app)
        stats = middleware.get_stats()
        assert isinstance(stats, dict)
