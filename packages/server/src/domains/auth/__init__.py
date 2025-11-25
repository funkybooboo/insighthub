"""Auth domain - handles authentication and user management."""

from shared.models import User
from shared.repositories import UserRepository

from .exceptions import (
    InvalidEmailError,
    InvalidUsernameError,
    UserAlreadyExistsError,
    UserAuthenticationError,
    UserNotFoundError,
)
from .mappers import UserMapper
from .routes import auth_bp
from .service import UserService

__all__ = [
    "User",
    "UserRepository",
    "UserService",
    "UserMapper",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "UserAuthenticationError",
    "InvalidEmailError",
    "InvalidUsernameError",
    "auth_bp",
]
