"""Unit tests for UserRepository."""

import pytest
from sqlalchemy.orm import Session

from src.db.models import User
from src.db.repository import UserRepository

pytestmark = [pytest.mark.unit, pytest.mark.database]


def test_create_user(db_session: Session) -> None:
    """Test creating a new user."""
    repo = UserRepository(db_session)

    user = repo.create(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.created_at is not None
    assert user.updated_at is not None


def test_get_user_by_id(db_session: Session) -> None:
    """Test retrieving a user by ID."""
    repo = UserRepository(db_session)

    # Create user
    created_user = repo.create(
        username="testuser",
        email="test@example.com"
    )

    # Retrieve user
    retrieved_user = repo.get_by_id(created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == "testuser"


def test_get_user_by_username(db_session: Session) -> None:
    """Test retrieving a user by username."""
    repo = UserRepository(db_session)

    # Create user
    repo.create(username="testuser", email="test@example.com")

    # Retrieve user
    user = repo.get_by_username("testuser")

    assert user is not None
    assert user.username == "testuser"


def test_get_user_by_email(db_session: Session) -> None:
    """Test retrieving a user by email."""
    repo = UserRepository(db_session)

    # Create user
    repo.create(username="testuser", email="test@example.com")

    # Retrieve user
    user = repo.get_by_email("test@example.com")

    assert user is not None
    assert user.email == "test@example.com"


def test_get_all_users(db_session: Session) -> None:
    """Test retrieving all users with pagination."""
    repo = UserRepository(db_session)

    # Create multiple users
    repo.create(username="user1", email="user1@example.com")
    repo.create(username="user2", email="user2@example.com")
    repo.create(username="user3", email="user3@example.com")

    # Get all users
    users = repo.get_all(skip=0, limit=10)

    assert len(users) == 3
    assert all(isinstance(user, User) for user in users)


def test_update_user(db_session: Session) -> None:
    """Test updating a user."""
    repo = UserRepository(db_session)

    # Create user
    user = repo.create(username="testuser", email="test@example.com")
    original_updated_at = user.updated_at

    # Update user
    updated_user = repo.update(user.id, full_name="Updated Name")

    assert updated_user is not None
    assert updated_user.full_name == "Updated Name"
    assert updated_user.updated_at >= original_updated_at


def test_delete_user(db_session: Session) -> None:
    """Test deleting a user."""
    repo = UserRepository(db_session)

    # Create user
    user = repo.create(username="testuser", email="test@example.com")
    user_id = user.id

    # Delete user
    result = repo.delete(user_id)

    assert result is True
    assert repo.get_by_id(user_id) is None


def test_delete_nonexistent_user(db_session: Session) -> None:
    """Test deleting a user that doesn't exist."""
    repo = UserRepository(db_session)

    result = repo.delete(99999)

    assert result is False
