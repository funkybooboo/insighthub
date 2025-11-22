"""User repository module."""

from shared.repositories.user.sql_user_repository import SqlUserRepository
from shared.repositories.user.user_repository import UserRepository

__all__ = [
    "UserRepository",
    "SqlUserRepository",
]
