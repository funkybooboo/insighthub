"""User repository module."""

from shared.repositories.user.user_repository import UserRepository
from shared.repositories.user.sql_user_repository import SqlUserRepository

__all__ = [
    "UserRepository",
    "SqlUserRepository",
]
