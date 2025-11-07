"""User service interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.models import User


class UserService(ABC):
    """Interface for user-related business logic."""

    @abstractmethod
    def create_user(
        self, username: str, email: str, full_name: Optional[str] = None
    ) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    def get_or_create_default_user(self) -> User:
        """Get or create a default user for demo purposes."""
        pass

    @abstractmethod
    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List all users with pagination."""
        pass

    @abstractmethod
    def update_user(self, user_id: int, **kwargs: str) -> Optional[User]:
        """Update user fields."""
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        pass
