"""Rate limiting middleware."""

import time
from collections import defaultdict

from flask import Flask, Request, Response, abort, jsonify, request
from shared.logger import create_logger

logger = create_logger(__name__)


class RateLimitMiddleware:
    """
    Redis-backed rate limiting middleware with in-memory fallback.

    Uses Redis for distributed rate limiting in production, falls back
    to in-memory storage for development/single-instance deployments.
    """

    def __init__(
        self,
        app: Flask,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        enabled: bool = True,
        redis_url: str | None = None,
    ):
        """
        Initialize rate limiting middleware.

        Args:
            app: Flask application instance
            requests_per_minute: Maximum requests per minute per IP
            requests_per_hour: Maximum requests per hour per IP
            enabled: Whether rate limiting is enabled
            redis_url: Redis URL for distributed rate limiting (optional)
        """
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.enabled = enabled
        self.redis_url = redis_url

        # Try to initialize Redis client
        self.redis_client = None
        if redis_url:
            try:
                import redis

                self.redis_client = redis.from_url(redis_url)
                # Test connection
                self.redis_client.ping()
                logger.info("Redis rate limiting enabled")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}, falling back to in-memory")
                self.redis_client = None

        # In-memory fallback storage: {ip: [(timestamp, count), ...]}
        self.request_counts: dict[str, list[tuple[float, int]]] = defaultdict(list)

        if self.enabled:
            self.setup_rate_limiting(app)
            backend = "Redis" if self.redis_client else "in-memory"
            logger.info(
                f"Rate limiting enabled ({backend}): {requests_per_minute}/min, {requests_per_hour}/hour"
            )
        else:
            logger.info("Rate limiting disabled")

    def setup_rate_limiting(self, app: Flask) -> None:
        """Set up rate limiting before each request."""

        @app.before_request
        def check_rate_limit() -> tuple[Response, int] | None:
            """Check if the request should be rate limited."""
            try:
                # Skip rate limiting for health checks
                if request.path in ["/health", "/heartbeat", "/ready", "/live"]:
                    return None

                client_ip = self._get_client_ip(request)

                # Check rate limits
                minute_requests = self._count_requests(client_ip, window=60)
                hour_requests = self._count_requests(client_ip, window=3600)

                if minute_requests >= self.requests_per_minute:
                    logger.warning(
                        f"Rate limit exceeded (per minute): {client_ip} - {minute_requests} requests"
                    )
                    abort(429, description="Rate limit exceeded. Please try again later.", retry_after=60)

                if hour_requests >= self.requests_per_hour:
                    logger.warning(
                        f"Rate limit exceeded (per hour): {client_ip} - {hour_requests} requests"
                    )
                    abort(429, description="Rate limit exceeded. Please try again later.", retry_after=3600)
            except Exception as e:
                # Don't break the request if rate limiting fails
                logger.warning(f"Rate limiting check failed: {e}")
                return None

            return None

    def _get_client_ip(self, req: Request) -> str:
        """Get the real client IP address, handling proxies."""
        if req.headers.get("X-Forwarded-For"):
            return req.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if req.headers.get("X-Real-IP"):
            return req.headers.get("X-Real-IP", "")
        return req.remote_addr or "unknown"

    def _clean_old_entries(self, ip: str) -> None:
        """Remove entries older than 1 hour (in-memory fallback only)."""
        if not self.redis_client:
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
        current_time = time.time()
        window_start = current_time - window

        try:
            if self.redis_client:
                # Use Redis sorted set to count requests in window
                key = f"ratelimit:{ip}:{window}"
                count = self.redis_client.zcount(key, window_start, current_time)

                # Add current request
                self.redis_client.zadd(key, {str(current_time): 1})
                # Set expiration to clean up old keys
                self.redis_client.expire(key, 3600)

                return int(count)
            else:
                # Fall back to in-memory storage
                return self._count_requests_memory(ip, window)
        except Exception as e:
            logger.warning(f"Redis rate limit check failed: {e}, falling back to memory")
            return self._count_requests_memory(ip, window)

    def _count_requests_memory(self, ip: str, window: int) -> int:
        """Count requests using in-memory storage (fallback)."""
        if ip not in self.request_counts:
            return 0

        current_time = time.time()
        # Count existing requests in window
        count = sum(count for ts, count in self.request_counts[ip] if current_time - ts < window)

        # Add current request
        self.request_counts[ip].append((current_time, 1))

        return count
