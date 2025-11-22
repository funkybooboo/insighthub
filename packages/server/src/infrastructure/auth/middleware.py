"""Authentication middleware for protecting routes."""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from flask import Response, jsonify
from jwt.exceptions import InvalidTokenError

from .jwt_utils import get_current_user

P = ParamSpec("P")
T = TypeVar("T")


def require_auth(f: Callable[P, T]) -> Callable[P, T | tuple[Response, int]]:
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
    def decorated_function(*args: P.args, **kwargs: P.kwargs) -> T | tuple[Response, int]:
        try:
            get_current_user()
        except InvalidTokenError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)

    return decorated_function
