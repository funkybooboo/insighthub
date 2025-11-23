"""Performance monitoring middleware."""

import time
from collections import defaultdict
from typing import TypedDict

from flask import Flask, Response, g, request
from shared.logger import create_logger

logger = create_logger(__name__)


class EndpointStats(TypedDict):
    """TypedDict for endpoint statistics."""

    count: int
    total_time: float
    min_time: float
    max_time: float


class EndpointStatsReport(TypedDict):
    """TypedDict for endpoint statistics report."""

    count: int
    avg_time: float
    min_time: float
    max_time: float
    total_time: float


class PerformanceMonitoringMiddleware:
    """
    Middleware for monitoring application performance.

    Tracks:
    - Request response times
    - Endpoint performance statistics
    - Slow request warnings
    - Memory usage (optional)
    """

    def __init__(
        self,
        app: Flask,
        slow_request_threshold: float = 1.0,  # seconds
        enable_stats: bool = True,
    ) -> None:
        """
        Initialize performance monitoring middleware.

        Args:
            app: Flask application instance
            slow_request_threshold: Threshold in seconds for slow request warning
            enable_stats: Whether to collect endpoint statistics
        """
        self.app = app
        self.slow_request_threshold = slow_request_threshold
        self.enable_stats = enable_stats

        # Statistics storage
        self.endpoint_stats: dict[str, EndpointStats] = defaultdict(
            lambda: EndpointStats(count=0, total_time=0.0, min_time=float("inf"), max_time=0.0)
        )

        self.setup_monitoring(app)
        logger.info(
            f"Performance monitoring initialized (slow threshold: {slow_request_threshold}s)"
        )

    def setup_monitoring(self, app: Flask) -> None:
        """Set up performance monitoring hooks."""

        @app.before_request
        def start_timer() -> None:
            """Record request start time."""
            g.start_time = time.time()

        @app.after_request
        def monitor_performance(response: Response) -> Response:
            """Monitor request performance and collect statistics."""
            if not hasattr(g, "start_time"):
                return response

            elapsed_time = time.time() - g.start_time

            # Log slow requests
            if elapsed_time > self.slow_request_threshold:
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {elapsed_time:.2f}s",
                    extra={
                        "method": request.method,
                        "path": request.path,
                        "response_time": elapsed_time,
                        "status_code": response.status_code,
                    },
                )

            # Collect endpoint statistics
            if self.enable_stats:
                endpoint = f"{request.method} {request.path}"
                stats = self.endpoint_stats[endpoint]
                stats["count"] += 1
                stats["total_time"] += elapsed_time
                stats["min_time"] = min(stats["min_time"], elapsed_time)
                stats["max_time"] = max(stats["max_time"], elapsed_time)

            # Add performance headers to response
            response.headers["X-Response-Time"] = f"{elapsed_time:.3f}s"

            return response

    def get_stats(self) -> dict[str, EndpointStatsReport]:
        """
        Get performance statistics for all endpoints.

        Returns:
            Dictionary with endpoint statistics including avg response time
        """
        return {
            endpoint: EndpointStatsReport(
                count=stats["count"],
                avg_time=stats["total_time"] / stats["count"] if stats["count"] > 0 else 0.0,
                min_time=stats["min_time"] if stats["min_time"] != float("inf") else 0.0,
                max_time=stats["max_time"],
                total_time=stats["total_time"],
            )
            for endpoint, stats in self.endpoint_stats.items()
        }

    def reset_stats(self) -> None:
        """Reset all performance statistics."""
        self.endpoint_stats.clear()
        logger.info("Performance statistics reset")
