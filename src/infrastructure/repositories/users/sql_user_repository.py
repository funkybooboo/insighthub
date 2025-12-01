"""SQL implementation of UserRepository."""

from datetime import UTC, datetime
from typing import List, Optional

from src.infrastructure.database import SqlDatabase
from src.infrastructure.models import User

from .user_repository import UserRepository


class SqlUserRepository(UserRepository):
    """SQL implementation of users repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get users by ID."""
        query = """
            SELECT id, username, email, password_hash, full_name, created_at, updated_at, theme_preference
            FROM users WHERE id = %s
        """
        result = self.db.fetch_one(query, (user_id,))
        if result:
            return User(**result)
        return None

    def get_by_username(self, username: str) -> Optional[User]:
        """Get users by username."""
        query = """
            SELECT id, username, email, password_hash, full_name, created_at, updated_at, theme_preference
            FROM users WHERE username = %s
        """
        result = self.db.fetch_one(query, (username,))
        if result:
            return User(**result)
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get users by email."""
        query = """
            SELECT id, username, email, password_hash, full_name, created_at, updated_at, theme_preference
            FROM users WHERE email = %s
        """
        result = self.db.fetch_one(query, (email,))
        if result:
            return User(**result)
        return None

    def create(self, user: User) -> User:
        """Create a new users."""
        query = """
            INSERT INTO users (username, email, password_hash, full_name, created_at, updated_at, theme_preference)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.fetch_one(
            query,
            (
                user.username,
                user.email,
                user.password_hash,
                user.full_name,
                user.created_at,
                user.updated_at,
                user.theme_preference,
            ),
        )

        if result:
            user.id = result["id"]
        return user

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update users."""
        # Get current users
        user = self.get_by_id(user_id)
        if not user:
            return None

        # Update fields
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.now(UTC)

        # Update in database
        query = """
            UPDATE users
            SET username = %s, email = %s, password_hash = %s, full_name = %s,
                updated_at = %s, theme_preference = %s
            WHERE id = %s
        """
        self.db.execute(
            query,
            (
                user.username,
                user.email,
                user.password_hash,
                user.full_name,
                user.updated_at,
                user.theme_preference,
                user_id,
            ),
        )

        return user

    def delete(self, user_id: int) -> bool:
        """Delete users."""
        query = "DELETE FROM users WHERE id = %s"
        affected_rows = self.db.execute(query, (user_id,))
        return affected_rows > 0

    def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination."""
        query = "SELECT * FROM users ORDER BY id LIMIT ? OFFSET ?"
        result = self.db.fetch_all(query, (limit, skip))
        users = []
        for row in result:
            users.append(User(**row))
        return users

    def count_all(self) -> int:
        """Count all users."""
        query = "SELECT COUNT(*) as count FROM users"
        result = self.db.fetch_one(query)
        return result["count"] if result else 0
