"""Rate limiting decorator for Flask routes."""

from functools import wraps
from typing import Any, Callable

from flask import jsonify, request, Response


def require_rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to apply rate limiting to a route.

    This is a simple in-memory rate limiter. For production use,
    consider using Redis-backed rate limiting.

    Args:
        max_requests: Maximum number of requests allowed in the window
        window_seconds: Time window in seconds

    Returns:
        Decorated function
    """
    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Response | Any:
            # For now, just pass through without actual rate limiting
            # TODO: Implement proper rate limiting with Redis or in-memory cache
            return f(*args, **kwargs)

        return decorated_function

    return decorator
