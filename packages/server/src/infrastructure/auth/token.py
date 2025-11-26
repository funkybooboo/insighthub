"""JWT token utilities for authentication."""

from datetime import datetime, timedelta
from typing import Any, Dict

import jwt

from src.infrastructure import config


def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token for a users.

    Args:
        user_id: User ID to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.utcnow() + expires_delta

    payload = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT access token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token payload

    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid
    """
    return jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])


def verify_token(token: str) -> bool:
    """
    Verify if a JWT token is valid.

    Args:
        token: JWT token to verify

    Returns:
        True if valid, False otherwise
    """
    try:
        decode_access_token(token)
        return True
    except jwt.InvalidTokenError:
        return False
