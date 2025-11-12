"""Unit tests for UserRepository."""

import pytest
from src.domains.users.models import User
from src.domains.users.repositories import UserRepository

pytestmark = [pytest.mark.unit, pytest.mark.database]


def test_create_user(user_repository: UserRepository) -> None:
    """Test creating a new user."""
    repo = user_repository

    user = repo.create(
        username="testuser", email="test@example.com", password="password123", full_name="Test User"
    )

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.password_hash is not None
    assert user.check_password("password123")
    assert user.created_at is not None
    assert user.updated_at is not None


def test_get_user_by_id(user_repository: UserRepository) -> None:
    """Test retrieving a user by ID."""
    repo = user_repository

    # Create user
    created_user = repo.create(
        username="testuser", email="test@example.com", password="password123"
    )

    # Retrieve user
    retrieved_user = repo.get_by_id(created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == "testuser"


def test_get_user_by_username(user_repository: UserRepository) -> None:
    """Test retrieving a user by username."""
    repo = user_repository

    # Create user
    repo.create(username="testuser", email="test@example.com", password="password123")

    # Retrieve user
    user = repo.get_by_username("testuser")

    assert user is not None
    assert user.username == "testuser"


def test_get_user_by_email(user_repository: UserRepository) -> None:
    """Test retrieving a user by email."""
    repo = user_repository

    # Create user
    repo.create(username="testuser", email="test@example.com", password="password123")

    # Retrieve user
    user = repo.get_by_email("test@example.com")

    assert user is not None
    assert user.email == "test@example.com"


def test_get_all_users(user_repository: UserRepository) -> None:
    """Test retrieving all users with pagination."""
    repo = user_repository

    # Create multiple users
    repo.create(username="user1", email="user1@example.com", password="password123")
    repo.create(username="user2", email="user2@example.com", password="password123")
    repo.create(username="user3", email="user3@example.com", password="password123")

    # Get all users
    users = repo.get_all(skip=0, limit=10)

    assert len(users) == 3
    assert all(isinstance(user, User) for user in users)


def test_update_user(user_repository: UserRepository) -> None:
    """Test updating a user."""
    repo = user_repository

    # Create user
    user = repo.create(username="testuser", email="test@example.com", password="password123")
    original_updated_at = user.updated_at

    # Update user
    updated_user = repo.update(user.id, full_name="Updated Name")

    assert updated_user is not None
    assert updated_user.full_name == "Updated Name"
    assert updated_user.updated_at >= original_updated_at


def test_delete_user(user_repository: UserRepository) -> None:
    """Test deleting a user."""
    repo = user_repository

    # Create user
    user = repo.create(username="testuser", email="test@example.com", password="password123")
    user_id = user.id

    # Delete user
    result = repo.delete(user_id)

    assert result is True
    assert repo.get_by_id(user_id) is None


def test_delete_nonexistent_user(user_repository: UserRepository) -> None:
    """Test deleting a user that doesn't exist."""
    repo = user_repository

    result = repo.delete(99999)

    assert result is False
