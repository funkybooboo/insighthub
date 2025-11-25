"""Unit tests for UserRepository interface and implementations."""

from datetime import datetime
from typing import Optional

import pytest

from shared.models.user import User
from shared.repositories.user.user_repository import UserRepository


class DummyUserRepository(UserRepository):
    """Dummy implementation of UserRepository for testing."""

    def __init__(self) -> None:
        """Initialize with in-memory storage."""
        self.users: dict[int, User] = {}
        self.next_id = 1

    def create(
        self, username: str, email: str, password: str, full_name: str | None = None
    ) -> User:
        """Create a new user."""
        user = User(
            id=self.next_id,
            username=username,
            email=email,
            password_hash=password,  # In real impl this would be hashed
            full_name=full_name,
        )
        self.users[user.id] = user
        self.next_id += 1
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        all_users = list(self.users.values())
        return all_users[skip : skip + limit]

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields."""
        user = self.users.get(user_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        return user

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False


@pytest.fixture
def repository() -> DummyUserRepository:
    """Provide a dummy user repository."""
    return DummyUserRepository()


class TestUserRepositoryCreate:
    """Tests for user creation."""

    def test_create_user_returns_user_with_correct_fields(
        self, repository: DummyUserRepository
    ) -> None:
        """create returns User with correct fields."""
        user = repository.create(
            username="testuser",
            email="test@example.com",
            password="hashed_password",
            full_name="Test User",
        )

        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.full_name == "Test User"

    def test_create_user_without_full_name(self, repository: DummyUserRepository) -> None:
        """create handles None full_name."""
        user = repository.create(
            username="testuser", email="test@example.com", password="hashed_password"
        )

        assert user.full_name is None

    def test_create_user_assigns_unique_ids(self, repository: DummyUserRepository) -> None:
        """create assigns unique IDs to users."""
        user1 = repository.create("user1", "user1@example.com", "pass1")
        user2 = repository.create("user2", "user2@example.com", "pass2")

        assert user1.id == 1
        assert user2.id == 2
        assert user1.id != user2.id

    def test_create_user_stores_user(self, repository: DummyUserRepository) -> None:
        """create stores user for later retrieval."""
        created = repository.create("testuser", "test@example.com", "password")

        retrieved = repository.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id


class TestUserRepositoryGetById:
    """Tests for get_by_id method."""

    def test_get_by_id_returns_correct_user(self, repository: DummyUserRepository) -> None:
        """get_by_id returns correct user when exists."""
        created = repository.create("testuser", "test@example.com", "password")

        result = repository.get_by_id(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.username == "testuser"

    def test_get_by_id_returns_none_when_not_exists(self, repository: DummyUserRepository) -> None:
        """get_by_id returns None when user doesn't exist."""
        result = repository.get_by_id(999)

        assert result is None

    def test_get_by_id_returns_none_for_negative_id(self, repository: DummyUserRepository) -> None:
        """get_by_id returns None for negative ID."""
        result = repository.get_by_id(-1)

        assert result is None


class TestUserRepositoryGetByUsername:
    """Tests for get_by_username method."""

    def test_get_by_username_returns_correct_user(self, repository: DummyUserRepository) -> None:
        """get_by_username returns correct user when exists."""
        created = repository.create("uniqueuser", "test@example.com", "password")

        result = repository.get_by_username("uniqueuser")

        assert result is not None
        assert result.id == created.id
        assert result.username == "uniqueuser"

    def test_get_by_username_returns_none_when_not_exists(
        self, repository: DummyUserRepository
    ) -> None:
        """get_by_username returns None when username doesn't exist."""
        result = repository.get_by_username("nonexistent")

        assert result is None

    def test_get_by_username_case_sensitive(self, repository: DummyUserRepository) -> None:
        """get_by_username is case sensitive."""
        repository.create("TestUser", "test@example.com", "password")

        result1 = repository.get_by_username("TestUser")
        result2 = repository.get_by_username("testuser")

        assert result1 is not None
        assert result2 is None

    def test_get_by_username_with_special_characters(self, repository: DummyUserRepository) -> None:
        """get_by_username handles usernames with special characters."""
        username = "user_name-123"
        created = repository.create(username, "test@example.com", "password")

        result = repository.get_by_username(username)

        assert result is not None
        assert result.id == created.id


class TestUserRepositoryGetByEmail:
    """Tests for get_by_email method."""

    def test_get_by_email_returns_correct_user(self, repository: DummyUserRepository) -> None:
        """get_by_email returns correct user when exists."""
        created = repository.create("testuser", "unique@example.com", "password")

        result = repository.get_by_email("unique@example.com")

        assert result is not None
        assert result.id == created.id
        assert result.email == "unique@example.com"

    def test_get_by_email_returns_none_when_not_exists(
        self, repository: DummyUserRepository
    ) -> None:
        """get_by_email returns None when email doesn't exist."""
        result = repository.get_by_email("nonexistent@example.com")

        assert result is None

    def test_get_by_email_case_sensitive(self, repository: DummyUserRepository) -> None:
        """get_by_email should be case sensitive."""
        repository.create("testuser", "Test@Example.Com", "password")

        # Should not find user with different case
        result = repository.get_by_email("test@example.com")
        assert result is None

        # Should find user with exact case match
        result = repository.get_by_email("Test@Example.Com")
        assert result is not None
        assert result.email == "Test@Example.Com"


class TestUserRepositoryGetAll:
    """Tests for get_all method."""

    def test_get_all_returns_empty_list_when_no_users(
        self, repository: DummyUserRepository
    ) -> None:
        """get_all returns empty list when no users exist."""
        result = repository.get_all()

        assert result == []

    def test_get_all_returns_all_users(self, repository: DummyUserRepository) -> None:
        """get_all returns all users when no pagination."""
        user1 = repository.create("user1", "user1@example.com", "pass1")
        user2 = repository.create("user2", "user2@example.com", "pass2")
        user3 = repository.create("user3", "user3@example.com", "pass3")

        result = repository.get_all()

        assert len(result) == 3
        assert user1 in result
        assert user2 in result
        assert user3 in result

    def test_get_all_with_skip(self, repository: DummyUserRepository) -> None:
        """get_all skips correct number of users."""
        repository.create("user1", "user1@example.com", "pass1")
        repository.create("user2", "user2@example.com", "pass2")
        repository.create("user3", "user3@example.com", "pass3")

        result = repository.get_all(skip=1)

        assert len(result) == 2
        assert result[0].username == "user2"
        assert result[1].username == "user3"

    def test_get_all_with_limit(self, repository: DummyUserRepository) -> None:
        """get_all limits number of returned users."""
        repository.create("user1", "user1@example.com", "pass1")
        repository.create("user2", "user2@example.com", "pass2")
        repository.create("user3", "user3@example.com", "pass3")

        result = repository.get_all(limit=2)

        assert len(result) == 2
        assert result[0].username == "user1"
        assert result[1].username == "user2"

    def test_get_all_with_skip_and_limit(self, repository: DummyUserRepository) -> None:
        """get_all handles both skip and limit."""
        repository.create("user1", "user1@example.com", "pass1")
        repository.create("user2", "user2@example.com", "pass2")
        repository.create("user3", "user3@example.com", "pass3")
        repository.create("user4", "user4@example.com", "pass4")

        result = repository.get_all(skip=1, limit=2)

        assert len(result) == 2
        assert result[0].username == "user2"
        assert result[1].username == "user3"

    def test_get_all_skip_beyond_available(self, repository: DummyUserRepository) -> None:
        """get_all returns empty list when skip exceeds available users."""
        repository.create("user1", "user1@example.com", "pass1")

        result = repository.get_all(skip=10)

        assert result == []

    def test_get_all_limit_zero(self, repository: DummyUserRepository) -> None:
        """get_all returns empty list when limit is zero."""
        repository.create("user1", "user1@example.com", "pass1")

        result = repository.get_all(limit=0)

        assert result == []


class TestUserRepositoryUpdate:
    """Tests for update method."""

    def test_update_existing_user(self, repository: DummyUserRepository) -> None:
        """update modifies existing user fields."""
        user = repository.create("testuser", "test@example.com", "password")

        updated = repository.update(user.id, full_name="Updated Name", email="updated@example.com")

        assert updated is not None
        assert updated.id == user.id
        assert updated.full_name == "Updated Name"
        assert updated.email == "updated@example.com"

    def test_update_nonexistent_user(self, repository: DummyUserRepository) -> None:
        """update returns None for nonexistent user."""
        result = repository.update(999, full_name="Updated Name")

        assert result is None

    def test_update_partial_fields(self, repository: DummyUserRepository) -> None:
        """update only modifies specified fields."""
        user = repository.create("testuser", "test@example.com", "password", "Original Name")

        updated = repository.update(user.id, full_name="New Name")

        assert updated is not None
        assert updated.username == "testuser"  # Unchanged
        assert updated.email == "test@example.com"  # Unchanged
        assert updated.full_name == "New Name"  # Changed

    def test_update_no_fields(self, repository: DummyUserRepository) -> None:
        """update with no fields returns user unchanged."""
        user = repository.create("testuser", "test@example.com", "password")

        updated = repository.update(user.id)

        assert updated is not None
        assert updated.id == user.id
        assert updated.username == "testuser"

    def test_update_invalid_field_ignored(self, repository: DummyUserRepository) -> None:
        """update ignores invalid field names."""
        user = repository.create("testuser", "test@example.com", "password")

        updated = repository.update(user.id, invalid_field="value", full_name="Valid Name")

        assert updated is not None
        assert updated.full_name == "Valid Name"
        assert not hasattr(updated, "invalid_field")


class TestUserRepositoryDelete:
    """Tests for delete method."""

    def test_delete_existing_user(self, repository: DummyUserRepository) -> None:
        """delete removes existing user."""
        user = repository.create("testuser", "test@example.com", "password")

        result = repository.delete(user.id)

        assert result is True
        assert repository.get_by_id(user.id) is None

    def test_delete_nonexistent_user(self, repository: DummyUserRepository) -> None:
        """delete returns False for nonexistent user."""
        result = repository.delete(999)

        assert result is False

    def test_delete_user_not_findable_after(self, repository: DummyUserRepository) -> None:
        """deleted user not findable by any method."""
        user = repository.create("testuser", "test@example.com", "password")

        repository.delete(user.id)

        assert repository.get_by_id(user.id) is None
        assert repository.get_by_username("testuser") is None
        assert repository.get_by_email("test@example.com") is None


class TestUserRepositoryIntegration:
    """Integration tests for multiple operations."""

    def test_create_then_get_by_id(self, repository: DummyUserRepository) -> None:
        """create followed by get_by_id works."""
        created = repository.create("testuser", "test@example.com", "password")
        retrieved = repository.get_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_create_multiple_then_get_all(self, repository: DummyUserRepository) -> None:
        """multiple creates then get_all works."""
        user1 = repository.create("user1", "user1@example.com", "pass1")
        user2 = repository.create("user2", "user2@example.com", "pass2")

        all_users = repository.get_all()

        assert len(all_users) == 2
        assert user1 in all_users
        assert user2 in all_users

    def test_update_then_get_by_username(self, repository: DummyUserRepository) -> None:
        """update then get_by_username works."""
        user = repository.create("oldname", "test@example.com", "password")
        repository.update(user.id, username="newname")

        retrieved = repository.get_by_username("newname")
        assert retrieved is not None
        assert retrieved.username == "newname"

    def test_delete_then_get_all(self, repository: DummyUserRepository) -> None:
        """delete then get_all excludes deleted user."""
        user1 = repository.create("user1", "user1@example.com", "pass1")
        user2 = repository.create("user2", "user2@example.com", "pass2")

        repository.delete(user1.id)

        remaining = repository.get_all()
        assert len(remaining) == 1
        assert remaining[0].id == user2.id
