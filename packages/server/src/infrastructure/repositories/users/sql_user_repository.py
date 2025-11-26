"""SQL implementation of UserRepository."""

from datetime import datetime
from typing import Optional

from src.infrastructure.database.sql import SqlDatabase
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
            FROM users WHERE id = ?
        """
        result = self.db.execute(query, (user_id,)).fetchone()
        if result:
            return User(*result)
        return None

    def get_by_username(self, username: str) -> Optional[User]:
        """Get users by username."""
        query = """
            SELECT id, username, email, password_hash, full_name, created_at, updated_at, theme_preference
            FROM users WHERE username = ?
        """
        result = self.db.execute(query, (username,)).fetchone()
        if result:
            return User(*result)
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get users by email."""
        query = """
            SELECT id, username, email, password_hash, full_name, created_at, updated_at, theme_preference
            FROM users WHERE email = ?
        """
        result = self.db.execute(query, (email,)).fetchone()
        if result:
            return User(*result)
        return None

    def create(self, user: User) -> User:
        """Create a new users."""
        query = """
            INSERT INTO users (username, email, password_hash, full_name, created_at, updated_at, theme_preference)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        user_id = self.db.execute(
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
        ).lastrowid

        user.id = user_id
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

        user.updated_at = datetime.utcnow()

        # Update in database
        query = """
            UPDATE users
            SET username = ?, email = ?, password_hash = ?, full_name = ?,
                updated_at = ?, theme_preference = ?
            WHERE id = ?
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
        query = "DELETE FROM users WHERE id = ?"
        result = self.db.execute(query, (user_id,))
        return result.rowcount > 0
