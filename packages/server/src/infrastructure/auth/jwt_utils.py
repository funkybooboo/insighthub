"""JWT token utilities for authentication."""

from datetime import datetime, timedelta
from typing import cast

import jwt
from flask import g, request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from shared.logger import create_logger
from shared.models import User

from src import config

logger = create_logger(__name__)

SECRET_KEY = config.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = config.JWT_EXPIRE_MINUTES


def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: The user's ID

    Returns:
        str: The encoded JWT token
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"user_id": user_id, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(
        "Created access token",
        extra={"user_id": user_id, "expires_in_minutes": ACCESS_TOKEN_EXPIRE_MINUTES},
    )
    return token


def decode_access_token(token: str) -> dict[str, int]:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT token to decode

    Returns:
        dict: The decoded payload containing user_id and expiration

    Raises:
        InvalidTokenError: If the token is invalid or expired
    """
    try:
        payload = cast(dict[str, int], jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]))
        logger.debug("Successfully decoded token", extra={"user_id": payload.get("user_id")})
        return payload
    except ExpiredSignatureError:
        logger.warning("Token decode failed: token has expired")
        raise InvalidTokenError("Token has expired") from None
    except Exception as e:
        logger.warning("Token decode failed", extra={"error": str(e)})
        raise InvalidTokenError("Invalid token") from e


def get_current_user() -> User:
    """
    Get the current authenticated user from the request context.

    Returns:
        User: The authenticated user

    Raises:
        InvalidTokenError: If authentication fails
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Authentication failed: missing or invalid authorization header")
        raise InvalidTokenError("Missing or invalid authorization header")

    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        logger.warning("Authentication failed: invalid token payload (no user_id)")
        raise InvalidTokenError("Invalid token payload")

    user = cast(User | None, g.app_context.user_service.get_user_by_id(user_id))
    if not user:
        logger.warning("Authentication failed: user not found", extra={"user_id": user_id})
        raise InvalidTokenError("User not found")

    logger.debug(
        "User authenticated successfully", extra={"user_id": user.id, "username": user.username}
    )
    return user
