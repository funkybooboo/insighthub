"""User service implementation."""

import logging

from shared.models import User
from shared.repositories import UserRepository

from .exceptions import UserAlreadyExistsError, UserAuthenticationError

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related business logic."""

    def __init__(self, repository: UserRepository):
        """
        Initialize service with repository.

        Args:
            repository: User repository implementation
        """
        self.repository = repository

    def create_user(
        self, username: str, email: str, password: str, full_name: str | None = None
    ) -> User:
        """Create a new user with password."""
        return self.repository.create(
            username=username, email=email, password=password, full_name=full_name
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return self.repository.get_by_username(username)

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.repository.get_by_email(email)

    def get_or_create_default_user(self) -> User:
        """Get or create a default user for demo purposes."""
        user = self.repository.get_by_username("demo_user")
        if not user:
            user = self.repository.create(
                username="demo_user",
                email="demo@insighthub.local",
                password="demo_password",
                full_name="Demo User",
            )
        return user

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List all users with pagination."""
        return self.repository.get_all(skip=skip, limit=limit)

    def update_user(self, user_id: int, **kwargs: str) -> User | None:
        """Update user fields."""
        return self.repository.update(user_id, **kwargs)

    def delete_user(self, user_id: int) -> bool:
        """Delete user by ID."""
        return self.repository.delete(user_id)

    def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate a user with username and password.

        Args:
            username: The username
            password: The plain text password

        Returns:
            User: The authenticated user

        Raises:
            UserAuthenticationError: If authentication fails
        """
        logger.info(f"Authentication attempt for username={username}")
        user = self.repository.get_by_username(username)
        if not user:
            logger.warning(f"Authentication failed: user not found (username={username})")
            raise UserAuthenticationError("Invalid username or password")

        if not user.check_password(password):
            logger.warning(
                f"Authentication failed: invalid password (username={username}, user_id={user.id})"
            )
            raise UserAuthenticationError("Invalid username or password")

        logger.info(f"User authenticated successfully: user_id={user.id}, username={username}")
        return user

    def register_user(
        self, username: str, email: str, password: str, full_name: str | None = None
    ) -> User:
        """
        Register a new user.

        Args:
            username: The username
            email: The email address
            password: The plain text password
            full_name: Optional full name

        Returns:
            User: The newly created user

        Raises:
            UserAlreadyExistsError: If username or email already exists
        """
        logger.info(f"User registration attempt: username={username}, email={email}")

        if self.repository.get_by_username(username):
            logger.warning(f"Registration failed: username already exists (username={username})")
            raise UserAlreadyExistsError(f"Username '{username}' already exists")

        if self.repository.get_by_email(email):
            logger.warning(f"Registration failed: email already exists (email={email})")
            raise UserAlreadyExistsError(f"Email '{email}' already exists")

        user = self.create_user(
            username=username, email=email, password=password, full_name=full_name
        )
        logger.info(
            f"User registered successfully: user_id={user.id}, username={username}, email={email}"
        )
        return user
