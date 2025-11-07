"""User repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.models import User


class UserRepository(ABC):
    """Interface for User repository operations."""

    @abstractmethod
    def create(self, username: str, email: str, full_name: Optional[str] = None) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        pass

    @abstractmethod
    def update(self, user_id: int, **kwargs: str) -> Optional[User]:
        """Update user fields."""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        pass
