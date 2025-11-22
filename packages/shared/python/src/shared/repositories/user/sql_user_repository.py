"""SQL implementation of user repository using SqlDatabase."""

from shared.database.sql.sql_database import SqlDatabase
from shared.models.user import User
from shared.types.option import Nothing, Option, Some

from .user_repository import UserRepository


class SqlUserRepository(UserRepository):
    """Repository for User operations using direct SQL queries."""

    def __init__(self, db: SqlDatabase) -> None:
        """
        Initialize repository with SqlDatabase.

        Args:
            db: SqlDatabase instance
        """
        self._db = db

    def create(
        self, username: str, email: str, password: str, full_name: str | None = None
    ) -> User:
        """Create a new user with hashed password."""
        hashed_password = User.hash_password(password)
        query = """
        INSERT INTO users (username, email, full_name, password_hash)
        VALUES (%(username)s, %(email)s, %(full_name)s, %(password_hash)s)
        RETURNING id, username, email, password_hash, full_name, theme_preference, created_at, updated_at;
        """
        params = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password_hash": hashed_password,
        }
        row = self._db.fetchone(query, params)
        if row is None:
            raise ValueError("Failed to create user")
        return User(**row)

    def get_by_id(self, user_id: int) -> Option[User]:
        """Get user by ID."""
        query = "SELECT * FROM users WHERE id = %(id)s;"
        row = self._db.fetchone(query, {"id": user_id})
        if row is None:
            return Nothing()
        return Some(User(**row))

    def get_by_username(self, username: str) -> Option[User]:
        """Get user by username."""
        query = "SELECT * FROM users WHERE username = %(username)s;"
        row = self._db.fetchone(query, {"username": username})
        if row is None:
            return Nothing()
        return Some(User(**row))

    def get_by_email(self, email: str) -> Option[User]:
        """Get user by email."""
        query = "SELECT * FROM users WHERE email = %(email)s;"
        row = self._db.fetchone(query, {"email": email})
        if row is None:
            return Nothing()
        return Some(User(**row))

    def get_all(self, skip: int, limit: int) -> list[User]:
        """Get all users with pagination."""
        query = "SELECT * FROM users OFFSET %(skip)s LIMIT %(limit)s;"
        rows = self._db.fetchall(query, {"skip": skip, "limit": limit})
        return [User(**row) for row in rows]

    def update(self, user_id: int, **kwargs: str) -> Option[User]:
        """Update user fields."""
        if not kwargs:
            return self.get_by_id(user_id)

        set_clause = ", ".join(f"{key} = %({key})s" for key in kwargs.keys())
        kwargs["id"] = str(user_id)
        query = f"""
        UPDATE users
        SET {set_clause}, updated_at = NOW()
        WHERE id = %(id)s
        RETURNING *;
        """
        row = self._db.fetchone(query, kwargs)
        if row is None:
            return Nothing()
        return Some(User(**row))

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        query = "DELETE FROM users WHERE id = %(id)s;"
        self._db.execute(query, {"id": user_id})
        return True
