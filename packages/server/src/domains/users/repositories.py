"""User domain repositories."""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from .models import User


class UserRepository(ABC):
    """Interface for User repository operations."""

    @abstractmethod
    def create(self, username: str, email: str, full_name: str | None = None) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        pass

    @abstractmethod
    def update(self, user_id: int, **kwargs: str) -> User | None:
        """Update user fields."""
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        pass


class SqlUserRepository(UserRepository):
    """Repository for User operations using SQL database."""

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, username: str, email: str, full_name: str | None = None) -> User:
        """Create a new user."""
        user = User(username=username, email=email, full_name=full_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        return self.db.query(User).offset(skip).limit(limit).all()

    def update(self, user_id: int, **kwargs: str) -> User | None:
        """Update user fields."""
        user = self.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
