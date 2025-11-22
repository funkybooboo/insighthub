"""User repository interface."""

from abc import ABC, abstractmethod

from shared.models.user import User
from shared.types.option import Option


class UserRepository(ABC):
    """Interface for User repository operations."""

    @abstractmethod
    def create(
        self, username: str, email: str, password: str, full_name: str | None = None
    ) -> User:
        """
        Create a new user with hashed password.

        Args:
            username: User's username
            email: User's email
            password: Plain text password (will be hashed)
            full_name: Optional full name

        Returns:
            Created user
        """
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> Option[User]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            Some(User) if found, Nothing() if not found
        """
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Option[User]:
        """
        Get user by username.

        Args:
            username: Username to search for

        Returns:
            Some(User) if found, Nothing() if not found
        """
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Option[User]:
        """
        Get user by email.

        Args:
            email: Email to search for

        Returns:
            Some(User) if found, Nothing() if not found
        """
        pass

    @abstractmethod
    def get_all(self, skip: int, limit: int) -> list[User]:
        """
        Get all users with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of users
        """
        pass

    @abstractmethod
    def update(self, user_id: int, **kwargs: str) -> Option[User]:
        """
        Update user fields.

        Args:
            user_id: User ID
            **kwargs: Fields to update

        Returns:
            Some(User) if found and updated, Nothing() if not found
        """
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """
        Delete user by ID.

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        pass
