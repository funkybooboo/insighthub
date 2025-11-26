"""Unit tests for auth domain."""

import pytest

from src.domains.auth.exceptions import UserAlreadyExistsError, UserAuthenticationError
from src.domains.auth.service import UserService
from src.infrastructure.repositories.users.in_memory_user_repository import InMemoryUserRepository


@pytest.mark.unit
class TestUserService:
    """Test cases for UserService."""

    @pytest.fixture
    def user_repository(self):
        """Create a fresh in-memory user repository for each test."""
        return InMemoryUserRepository()

    @pytest.fixture
    def user_service(self, user_repository):
        """Create a UserService with in-memory repository."""
        return UserService(user_repository)

    def test_create_user_success(self, user_service):
        """Test successful user creation."""
        user = user_service.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            full_name="Test User",
        )

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.check_password("password123")

    def test_get_user_by_id_existing(self, user_service):
        """Test getting existing user by ID."""
        created_user = user_service.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        retrieved_user = user_service.get_user_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == "testuser"

    def test_get_user_by_id_nonexistent(self, user_service):
        """Test getting nonexistent user by ID returns None."""
        user = user_service.get_user_by_id(999)
        assert user is None

    def test_get_user_by_username_existing(self, user_service):
        """Test getting existing user by username."""
        user_service.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        user = user_service.get_user_by_username("testuser")
        assert user is not None
        assert user.username == "testuser"

    def test_get_user_by_username_nonexistent(self, user_service):
        """Test getting nonexistent user by username returns None."""
        user = user_service.get_user_by_username("nonexistent")
        assert user is None

    def test_get_user_by_email_existing(self, user_service):
        """Test getting existing user by email."""
        user_service.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        user = user_service.get_user_by_email("test@example.com")
        assert user is not None
        assert user.email == "test@example.com"

    def test_get_user_by_email_nonexistent(self, user_service):
        """Test getting nonexistent user by email returns None."""
        user = user_service.get_user_by_email("nonexistent@example.com")
        assert user is None

    def test_get_or_create_default_user_creates_new(self, user_service):
        """Test get_or_create_default_user creates new user when none exists."""
        user = user_service.get_or_create_default_user()

        assert user.username == "demo_user"
        assert user.email == "demo@insighthub.local"
        assert user.full_name == "Demo User"
        assert user.check_password("demo_password")

    def test_get_or_create_default_user_returns_existing(self, user_service):
        """Test get_or_create_default_user returns existing user."""
        # Create default user first
        user1 = user_service.get_or_create_default_user()

        # Get it again - should return the same user
        user2 = user_service.get_or_create_default_user()

        assert user1.id == user2.id
        assert user1.username == user2.username

    def test_list_users_empty(self, user_service):
        """Test listing users when none exist."""
        users = user_service.list_users()
        assert users == []

    def test_list_users_with_data(self, user_service):
        """Test listing users with data."""
        user_service.create_user("user1", "user1@example.com", "pass1")
        user_service.create_user("user2", "user2@example.com", "pass2")

        users = user_service.list_users()
        assert len(users) == 2
        assert users[0].username == "user1"
        assert users[1].username == "user2"

    def test_list_users_pagination(self, user_service):
        """Test user listing with pagination."""
        for i in range(5):
            user_service.create_user(f"user{i}", f"user{i}@example.com", "pass")

        # Test skip
        users = user_service.list_users(skip=2, limit=2)
        assert len(users) == 2
        assert users[0].username == "user2"
        assert users[1].username == "user3"

    def test_count_users_empty(self, user_service):
        """Test counting users when none exist."""
        count = user_service.count_users()
        assert count == 0

    def test_count_users_with_data(self, user_service):
        """Test counting users with data."""
        user_service.create_user("user1", "user1@example.com", "pass1")
        user_service.create_user("user2", "user2@example.com", "pass2")

        count = user_service.count_users()
        assert count == 2

    def test_update_user_success(self, user_service):
        """Test successful user update."""
        user = user_service.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            full_name="Test User",
        )

        updated_user = user_service.update_user(
            user.id, full_name="Updated Name", email="updated@example.com"
        )

        assert updated_user is not None
        assert updated_user.id == user.id
        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == "updated@example.com"

    def test_update_user_nonexistent(self, user_service):
        """Test updating nonexistent user returns None."""
        result = user_service.update_user(999, full_name="Updated Name")
        assert result is None

    def test_delete_user_success(self, user_service):
        """Test successful user deletion."""
        user = user_service.create_user("testuser", "test@example.com", "password123")

        result = user_service.delete_user(user.id)
        assert result is True

        # Verify user is gone
        retrieved = user_service.get_user_by_id(user.id)
        assert retrieved is None

    def test_delete_user_nonexistent(self, user_service):
        """Test deleting nonexistent user returns False."""
        result = user_service.delete_user(999)
        assert result is False

    def test_authenticate_user_success(self, user_service):
        """Test successful user authentication."""
        user_service.create_user("testuser", "test@example.com", "password123")

        authenticated_user = user_service.authenticate_user("testuser", "password123")

        assert authenticated_user is not None
        assert authenticated_user.username == "testuser"

    def test_authenticate_user_wrong_password(self, user_service):
        """Test authentication with wrong password raises error."""
        user_service.create_user("testuser", "test@example.com", "password123")

        with pytest.raises(UserAuthenticationError, match="Invalid username or password"):
            user_service.authenticate_user("testuser", "wrongpassword")

    def test_authenticate_user_nonexistent_username(self, user_service):
        """Test authentication with nonexistent username raises error."""
        with pytest.raises(UserAuthenticationError, match="Invalid username or password"):
            user_service.authenticate_user("nonexistent", "password123")

    def test_register_user_success(self, user_service):
        """Test successful user registration."""
        user = user_service.register_user(
            username="newuser",
            email="new@example.com",
            password="password123",
            full_name="New User",
        )

        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.full_name == "New User"
        assert user.check_password("password123")

    def test_register_user_duplicate_username(self, user_service):
        """Test registration with duplicate username raises error."""
        user_service.create_user("existing", "existing@example.com", "password123")

        with pytest.raises(UserAlreadyExistsError, match="Username 'existing' already exists"):
            user_service.register_user("existing", "different@example.com", "password123")

    def test_register_user_duplicate_email(self, user_service):
        """Test registration with duplicate email raises error."""
        user_service.create_user("existing", "existing@example.com", "password123")

        with pytest.raises(
            UserAlreadyExistsError, match="Email 'existing@example.com' already exists"
        ):
            user_service.register_user("different", "existing@example.com", "password123")

    def test_change_password_success(self, user_service):
        """Test successful password change."""
        user = user_service.create_user("testuser", "test@example.com", "oldpassword")

        result = user_service.change_password(user.id, "oldpassword", "newpassword")

        assert result is True

        # Verify new password works
        authenticated = user_service.authenticate_user("testuser", "newpassword")
        assert authenticated is not None

        # Verify old password doesn't work
        with pytest.raises(UserAuthenticationError):
            user_service.authenticate_user("testuser", "oldpassword")

    def test_change_password_wrong_current(self, user_service):
        """Test password change with wrong current password raises error."""
        user = user_service.create_user("testuser", "test@example.com", "oldpassword")

        with pytest.raises(UserAuthenticationError, match="Current password is incorrect"):
            user_service.change_password(user.id, "wrongpassword", "newpassword")

    def test_change_password_nonexistent_user(self, user_service):
        """Test password change for nonexistent user returns False."""
        result = user_service.change_password(999, "oldpassword", "newpassword")
        assert result is False
