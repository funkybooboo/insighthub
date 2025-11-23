"""Rate limiting middleware."""

import time
from collections import defaultdict

from flask import Flask, Request, Response, jsonify, request
from shared.logger import create_logger

logger = create_logger(__name__)


class RateLimitMiddleware:
    """
    Simple in-memory rate limiting middleware.

    For production, consider using Redis-backed rate limiting
    (e.g., Flask-Limiter with Redis backend).

    This implementation tracks requests per IP address and enforces
    configurable rate limits.
    """

    def __init__(
        self,
        app: Flask,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        enabled: bool = True,
    ) -> None:
        """
        Initialize rate limiting middleware.

        Args:
            app: Flask application instance
            requests_per_minute: Maximum requests per minute per IP
            requests_per_hour: Maximum requests per hour per IP
            enabled: Whether rate limiting is enabled
        """
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.enabled = enabled

        # In-memory storage: {ip: [(timestamp, count), ...]}
        self.request_counts: dict[str, list[tuple[float, int]]] = defaultdict(list)

        if self.enabled:
            self.setup_rate_limiting(app)
            logger.info(
                f"Rate limiting enabled: {requests_per_minute}/min, {requests_per_hour}/hour"
            )
        else:
            logger.info("Rate limiting disabled")

    def setup_rate_limiting(self, app: Flask) -> None:
        """Set up rate limiting before each request."""

        @app.before_request
        def check_rate_limit() -> tuple[Response, int] | None:
            """Check if the request should be rate limited."""
            # Skip rate limiting for health checks
            if request.path in ["/health", "/heartbeat"]:
                return None

            client_ip = self._get_client_ip(request)

            # Clean old entries
            self._clean_old_entries(client_ip)

            # Check rate limits
            minute_requests = self._count_requests(client_ip, window=60)
            hour_requests = self._count_requests(client_ip, window=3600)

            if minute_requests >= self.requests_per_minute:
                logger.warning(
                    f"Rate limit exceeded (per minute): {client_ip} - {minute_requests} requests"
                )
                return (
                    jsonify(
                        {
                            "error": "Rate limit exceeded. Please try again later.",
                            "retry_after": 60,
                        }
                    ),
                    429,
                )

            if hour_requests >= self.requests_per_hour:
                logger.warning(
                    f"Rate limit exceeded (per hour): {client_ip} - {hour_requests} requests"
                )
                return (
                    jsonify(
                        {
                            "error": "Rate limit exceeded. Please try again later.",
                            "retry_after": 3600,
                        }
                    ),
                    429,
                )

            # Record this request
            self.request_counts[client_ip].append((time.time(), 1))

            return None

    def _get_client_ip(self, req: Request) -> str:
        """Get the real client IP address, handling proxies."""
        if req.headers.get("X-Forwarded-For"):
            return req.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if req.headers.get("X-Real-IP"):
            return req.headers.get("X-Real-IP", "")
        return req.remote_addr or "unknown"

    def _clean_old_entries(self, ip: str) -> None:
        """Remove entries older than 1 hour."""
        if ip not in self.request_counts:
            return

        current_time = time.time()
        self.request_counts[ip] = [
            (ts, count) for ts, count in self.request_counts[ip] if current_time - ts < 3600
        ]

        # Clean up if empty
        if not self.request_counts[ip]:
            del self.request_counts[ip]

    def _count_requests(self, ip: str, window: int) -> int:
        """Count requests within the time window (in seconds)."""
        if ip not in self.request_counts:
            return 0

        current_time = time.time()
        return sum(count for ts, count in self.request_counts[ip] if current_time - ts < window)
