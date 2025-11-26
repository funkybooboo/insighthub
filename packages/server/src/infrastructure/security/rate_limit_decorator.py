"""Rate limiting decorator for Flask routes."""

import time
from collections import defaultdict, deque
from functools import wraps
from typing import Callable

from flask import Response, request

# In-memory storage for rate limiting (not suitable for multi-process deployments)
_rate_limit_storage: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=1000))


def require_rate_limit(
    max_requests: int = 100,
    window_seconds: int = 60,
) -> 'Callable[[Callable[..., object]], Callable[..., object]]':
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

    def decorator(f: 'Callable[..., object]') -> 'Callable[..., object]':
        @wraps(f)
        def decorated_function(*args: object, **kwargs: object) -> object:
            # Get client identifier (IP address for now)
            client_id = request.remote_addr or "unknown"

            # Get current timestamp
            now = time.time()

            # Get or create request timestamps for this client
            timestamps = _rate_limit_storage[client_id]

            # Remove timestamps outside the window
            while timestamps and timestamps[0] < now - window_seconds:
                timestamps.popleft()

            # Check if rate limit exceeded
            if len(timestamps) >= max_requests:
                return Response(
                    "Rate limit exceeded. Try again later.",
                    status=429,
                    headers={"Retry-After": str(int(window_seconds))}
                )

            # Add current timestamp
            timestamps.append(now)

            # Call the original function
            return f(*args, **kwargs)

        return decorated_function

    return decorator
