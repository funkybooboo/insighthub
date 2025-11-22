"""SQL implementation of user repository."""

from sqlalchemy.orm import Session

from shared.models.user import User
from shared.types.option import Nothing, Option, Some

from .user_repository import UserRepository


class SqlUserRepository(UserRepository):
    """Repository for User operations using SQL database."""

    def __init__(self, db: Session) -> None:
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self._db = db

    def create(
        self, username: str, email: str, password: str, full_name: str | None = None
    ) -> User:
        """Create a new user with hashed password."""
        user = User(username=username, email=email, full_name=full_name)
        user.set_password(password)
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> Option[User]:
        """Get user by ID."""
        user = self._db.query(User).filter(User.id == user_id).first()
        if user is None:
            return Nothing()
        return Some(user)

    def get_by_username(self, username: str) -> Option[User]:
        """Get user by username."""
        user = self._db.query(User).filter(User.username == username).first()
        if user is None:
            return Nothing()
        return Some(user)

    def get_by_email(self, email: str) -> Option[User]:
        """Get user by email."""
        user = self._db.query(User).filter(User.email == email).first()
        if user is None:
            return Nothing()
        return Some(user)

    def get_all(self, skip: int, limit: int) -> list[User]:
        """Get all users with pagination."""
        return self._db.query(User).offset(skip).limit(limit).all()

    def update(self, user_id: int, **kwargs: str) -> Option[User]:
        """Update user fields."""
        result = self.get_by_id(user_id)
        if result.is_nothing():
            return Nothing()

        user = result.unwrap()
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        self._db.commit()
        self._db.refresh(user)
        return Some(user)

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        result = self.get_by_id(user_id)
        if result.is_nothing():
            return False

        user = result.unwrap()
        self._db.delete(user)
        self._db.commit()
        return True
