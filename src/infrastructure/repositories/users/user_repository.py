"""User repository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.infrastructure.models import User


class UserRepository(ABC):
    """Abstract users repository."""

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get users by ID."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Get users by username."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get users by email."""
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new users."""
        pass

    @abstractmethod
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update users."""
        pass

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination."""
        raise NotImplementedError

    @abstractmethod
    def count_all(self) -> int:
        """Count all users."""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete users."""
        pass
