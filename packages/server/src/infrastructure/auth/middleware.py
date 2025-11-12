"""Authentication middleware for protecting routes."""

from functools import wraps
from typing import Any, Callable

from flask import jsonify
from jwt.exceptions import InvalidTokenError

from .jwt_utils import get_current_user


def require_auth(f: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to require authentication for a route.

    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            user = get_current_user()
            return {'message': f'Hello {user.username}'}

    Args:
        f: The route function to decorate

    Returns:
        The decorated function
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            get_current_user()
        except InvalidTokenError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)

    return decorated_function
