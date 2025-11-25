"""Rate limiting decorators for Flask routes."""

from functools import wraps
from flask import request, g
from typing import Callable, Any

def require_rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """
    Decorator to apply rate limiting to a route.

    Args:
        max_requests: Maximum number of requests allowed in the window
        window_seconds: Time window in seconds

    Returns:
        Decorated function
    """
    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get rate limiter from app context
            if hasattr(g, 'app_context') and hasattr(g.app_context, 'rate_limiter'):
                rate_limiter = g.app_context.rate_limiter
                if rate_limiter:
                    # Check rate limit
                    client_ip = request.remote_addr or "unknown"
                    requests_in_window = rate_limiter._count_requests(client_ip, window_seconds)

                    if requests_in_window >= max_requests:
                        from flask import jsonify
                        return jsonify({
                            "error": "Rate limit exceeded. Please try again later.",
                            "retry_after": window_seconds
                        }), 429

            # Call the original function
            return f(*args, **kwargs)
        return wrapper
    return decorator