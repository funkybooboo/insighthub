"""User service implementation."""

from src.infrastructure.logger import create_logger
from src.infrastructure.models import User
from src.infrastructure.repositories.users import UserRepository

from .exceptions import UserAlreadyExistsError, UserAuthenticationError

logger = create_logger(__name__)


class UserService:
    """Service for users-related business logic."""

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
        """Create a new users with password."""
        return self.repository.create(
            User(username, email, User.hash_password(password), full_name)
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        """Get users by ID."""
        return self.repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> User | None:
        """Get users by username."""
        return self.repository.get_by_username(username)

    def get_user_by_email(self, email: str) -> User | None:
        """Get users by email."""
        return self.repository.get_by_email(email)

    def get_or_create_default_user(self) -> User:
        """Get or create a default users for demo purposes."""
        user = self.repository.get_by_username("demo_user")
        if user:
            return user
        return self.repository.create(
            User(
                username="demo_user",
                email="demo@insighthub.local",
                password_hash=User.hash_password("demo_password"),
                full_name="Demo User",
            )
        )

    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List all users with pagination."""
        return self.repository.list_all(skip=skip, limit=limit)

    def count_users(self) -> int:
        """Count all users."""
        return self.repository.count_all()

    def update_user(self, user_id: int, **kwargs) -> User | None:
        """Update users fields."""
        return self.repository.update(user_id, **kwargs)

    def delete_user(self, user_id: int) -> bool:
        """Delete users by ID."""
        return self.repository.delete(user_id)

    def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate a users with username and password.

        Args:
            username: The username
            password: The plain text password

        Returns:
            User: The authenticated users

        Raises:
            UserAuthenticationError: If authentication fails
        """
        logger.info(f"Authentication attempt for username={username}")
        user = self.repository.get_by_username(username)
        if user:
            if not user.check_password(password):
                logger.warning(
                    f"Authentication failed: invalid password (username={username}, user_id={user.id})"
                )
                raise UserAuthenticationError("Invalid username or password")
            logger.info(f"User authenticated successfully: user_id={user.id}, username={username}")
            return user
        else:
            logger.warning(f"Authentication failed: users not found (username={username})")
            raise UserAuthenticationError("Invalid username or password")

    def register_user(
        self, username: str, email: str, password: str, full_name: str | None = None
    ) -> User:
        """
        Register a new users.

        Args:
            username: The username
            email: The email address
            password: The plain text password
            full_name: Optional full name

        Returns:
            User: The newly created users

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

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change a user's password.

        Args:
            user_id: The user ID
            current_password: The current password
            new_password: The new password

        Returns:
            bool: True if password was changed successfully

        Raises:
            UserAuthenticationError: If current password is incorrect
        """
        logger.info(f"Password change attempt for user_id={user_id}")

        user = self.repository.get_by_id(user_id)
        if not user:
            logger.warning(f"Password change failed: user not found (user_id={user_id})")
            return False

        if not user.check_password(current_password):
            logger.warning(
                f"Password change failed: incorrect current password (user_id={user_id})"
            )
            raise UserAuthenticationError("Current password is incorrect")

        # Update password
        updated_user = self.repository.update(
            user_id, password_hash=User.hash_password(new_password)
        )
        if updated_user:
            logger.info(f"Password changed successfully for user_id={user_id}")
            return True
        else:
            logger.warning(f"Password change failed: update failed (user_id={user_id})")
            return False
