"""In-memory implementation of UserRepository."""

from datetime import datetime
from typing import Optional, List

from src.infrastructure.models import User

from .user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of UserRepository for development/testing."""

    def __init__(self):
        """Initialize the repository."""
        self._users: dict[int, User] = {}
        self._next_id = 1

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get users by ID."""
        return self._users.get(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get users by username."""
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get users by email."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def create(self, user: User) -> User:
        """Create a new users."""
        user.id = self._next_id
        self._users[self._next_id] = user
        self._next_id += 1
        return user

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update users."""
        user = self._users.get(user_id)
        if not user:
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        return user

    def delete(self, user_id: int) -> bool:
        """Delete users."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination."""
        all_users = list(self._users.values())
        return all_users[skip:skip + limit]

    def count_all(self) -> int:
        """Count all users."""
        return len(self._users)
