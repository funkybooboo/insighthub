"""Authentication decorators for Flask routes."""

from functools import wraps
from typing import Any, Callable

from flask import Response, g, jsonify, request

from src.infrastructure.auth.token import decode_access_token


def require_auth(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to require authentication for a route.

    Extracts and validates JWT token from Authorization header,
    and vector_stores users information in Flask g object.

    Returns 401 if no token or invalid token.
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Response | Any:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "No authorization header"}), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Invalid authorization header format"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = decode_access_token(token)
            g.user_id = payload.get("user_id")

            if not g.user_id:
                return jsonify({"error": "Invalid token payload"}), 401

        except Exception as e:
            return jsonify({"error": f"Token verification failed: {str(e)}"}), 401

        return f(*args, **kwargs)

    return decorated_function
