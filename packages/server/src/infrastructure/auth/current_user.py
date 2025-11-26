"""Get current users from Flask context."""

from flask import g
from flask import request


from src.infrastructure.models import User


def get_current_user_id() -> int:
    """Get current users ID from JWT token in Authorization header."""
    from src.infrastructure.auth.token import decode_access_token

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return 1  # Default users for development

    token = auth_header.split(" ")[1]
    try:
        payload = decode_access_token(token)
        return int(payload.get("user_id", 1))
    except Exception:
        return 1  # Default users if token invalid


def get_current_user() -> User:
    """
    Get the current authenticated users from Flask g object.

    This should only be called within routes decorated with @require_auth,
    as it assumes g.user_id and g.app_context are set.

    Returns:
        User object for the current users

    Raises:
        RuntimeError: If called outside of auth context
    """
    if not hasattr(g, "user_id"):
        raise RuntimeError("No authenticated users in context. Use @require_auth decorator.")

    if not hasattr(g, "app_context"):
        raise RuntimeError("No app context available")

    user = g.app_context.user_service.get_user_by_id(g.user_id)

    if not user:
        raise RuntimeError(f"User {g.user_id} not found")

    return user
