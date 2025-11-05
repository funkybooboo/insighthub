"""User service for business logic."""

from typing import Optional

from src.db.interfaces import UserRepository
from src.db.models import User


class UserService:
    """Service for user-related business logic."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(
        self, username: str, email: str, full_name: Optional[str] = None
    ) -> User:
        """Create a new user."""
        return self.repository.create(username=username, email=email, full_name=full_name)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.repository.get_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.repository.get_by_email(email)

    def get_or_create_default_user(self) -> User:
        """Get or create a default user for demo purposes."""
        user = self.repository.get_by_username("demo_user")
        if not user:
            user = self.repository.create(
                username="demo_user", email="demo@insighthub.local", full_name="Demo User"
            )
        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List all users with pagination."""
        return self.repository.get_all(skip=skip, limit=limit)

    def update_user(self, user_id: int, **kwargs: str) -> Optional[User]:
        """Update user fields."""
        return self.repository.update(user_id, **kwargs)

    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        return self.repository.delete(user_id)
