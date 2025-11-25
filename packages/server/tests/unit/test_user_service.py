"""Unit tests for UserService."""

import pytest
from shared.models import User
from shared.repositories import UserRepository

from src.domains.auth.exceptions import UserAlreadyExistsError, UserAuthenticationError
from src.domains.auth.service import UserService


class FakeUserRepository(UserRepository):
    """Fake user repository for testing."""

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
            password_hash="",
            full_name=full_name or "",
        )
        user.set_password(password)
        self.users[user.id] = user
        self.next_id += 1
        return user

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.users.get(user_id)

    def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        all_users = list(self.users.values())
        return all_users[skip : skip + limit]

    def update(self, user_id: int, **kwargs: str) -> User | None:
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
def fake_repository() -> FakeUserRepository:
    """Provide a fake repository."""
    return FakeUserRepository()


@pytest.fixture
def service(fake_repository: FakeUserRepository) -> UserService:
    """Provide a UserService with fake repository."""
    return UserService(repository=fake_repository)


class TestUserServiceCreate:
    """Tests for user creation."""

    def test_create_user_success(self, service: UserService) -> None:
        """Test creating a new user."""
        user = service.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            full_name="Test User",
        )

        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.check_password("password123")

    def test_create_user_without_full_name(self, service: UserService) -> None:
        """Test creating a user without full name."""
        user = service.create_user(
            username="testuser", email="test@example.com", password="password123"
        )

        assert user.username == "testuser"
        assert user.full_name == ""


class TestUserServiceGet:
    """Tests for retrieving users."""

    def test_get_user_by_id(self, service: UserService) -> None:
        """Test getting user by ID."""
        created = service.create_user("testuser", "test@example.com", "password123")
        user = service.get_user_by_id(created.id)

        assert user is not None
        assert user.id == created.id
        assert user.username == "testuser"

    def test_get_user_by_id_not_found(self, service: UserService) -> None:
        """Test getting non-existent user by ID."""
        user = service.get_user_by_id(999)
        assert user is None

    def test_get_user_by_username(self, service: UserService) -> None:
        """Test getting user by username."""
        service.create_user("testuser", "test@example.com", "password123")
        user = service.get_user_by_username("testuser")

        assert user is not None
        assert user.username == "testuser"

    def test_get_user_by_username_not_found(self, service: UserService) -> None:
        """Test getting non-existent user by username."""
        user = service.get_user_by_username("nonexistent")
        assert user is None

    def test_get_user_by_email(self, service: UserService) -> None:
        """Test getting user by email."""
        service.create_user("testuser", "test@example.com", "password123")
        user = service.get_user_by_email("test@example.com")

        assert user is not None
        assert user.email == "test@example.com"

    def test_get_user_by_email_not_found(self, service: UserService) -> None:
        """Test getting non-existent user by email."""
        user = service.get_user_by_email("nonexistent@example.com")
        assert user is None


class TestUserServiceList:
    """Tests for listing users."""

    def test_list_users_empty(self, service: UserService) -> None:
        """Test listing users when none exist."""
        users = service.list_users()
        assert len(users) == 0

    def test_list_users_multiple(self, service: UserService) -> None:
        """Test listing multiple users."""
        service.create_user("user1", "user1@example.com", "password123")
        service.create_user("user2", "user2@example.com", "password123")
        service.create_user("user3", "user3@example.com", "password123")

        users = service.list_users()
        assert len(users) == 3

    def test_list_users_pagination(self, service: UserService) -> None:
        """Test pagination."""
        for i in range(5):
            service.create_user(f"user{i}", f"user{i}@example.com", "password123")

        users_page1 = service.list_users(skip=0, limit=2)
        users_page2 = service.list_users(skip=2, limit=2)

        assert len(users_page1) == 2
        assert len(users_page2) == 2
        assert users_page1[0].username != users_page2[0].username


class TestUserServiceUpdate:
    """Tests for updating users."""

    def test_update_user_success(self, service: UserService) -> None:
        """Test updating user fields."""
        user = service.create_user("testuser", "test@example.com", "password123")
        updated = service.update_user(user.id, full_name="Updated Name")

        assert updated is not None
        assert updated.full_name == "Updated Name"

    def test_update_user_not_found(self, service: UserService) -> None:
        """Test updating non-existent user."""
        result = service.update_user(999, full_name="Updated Name")
        assert result is None


class TestUserServiceDelete:
    """Tests for deleting users."""

    def test_delete_user_success(self, service: UserService) -> None:
        """Test deleting a user."""
        user = service.create_user("testuser", "test@example.com", "password123")
        result = service.delete_user(user.id)

        assert result is True
        assert service.get_user_by_id(user.id) is None

    def test_delete_user_not_found(self, service: UserService) -> None:
        """Test deleting non-existent user."""
        result = service.delete_user(999)
        assert result is False


class TestUserServiceAuthentication:
    """Tests for user authentication."""

    def test_authenticate_user_success(self, service: UserService) -> None:
        """Test successful authentication."""
        service.create_user("testuser", "test@example.com", "password123")
        user = service.authenticate_user("testuser", "password123")

        assert user.username == "testuser"

    def test_authenticate_user_wrong_password(self, service: UserService) -> None:
        """Test authentication with wrong password."""
        service.create_user("testuser", "test@example.com", "password123")

        with pytest.raises(UserAuthenticationError, match="Invalid username or password"):
            service.authenticate_user("testuser", "wrongpassword")

    def test_authenticate_user_not_found(self, service: UserService) -> None:
        """Test authentication for non-existent user."""
        with pytest.raises(UserAuthenticationError, match="Invalid username or password"):
            service.authenticate_user("nonexistent", "password123")


class TestUserServiceRegistration:
    """Tests for user registration."""

    def test_register_user_success(self, service: UserService) -> None:
        """Test successful registration."""
        user = service.register_user("newuser", "new@example.com", "password123", "New User")

        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.full_name == "New User"

    def test_register_user_duplicate_username(self, service: UserService) -> None:
        """Test registration with duplicate username."""
        service.create_user("testuser", "test@example.com", "password123")

        with pytest.raises(UserAlreadyExistsError, match="Username 'testuser' already exists"):
            service.register_user("testuser", "different@example.com", "password123")

    def test_register_user_duplicate_email(self, service: UserService) -> None:
        """Test registration with duplicate email."""
        service.create_user("testuser", "test@example.com", "password123")

        with pytest.raises(UserAlreadyExistsError, match="Email 'test@example.com' already exists"):
            service.register_user("differentuser", "test@example.com", "password123")


class TestUserServiceDefaultUser:
    """Tests for default user creation."""

    def test_get_or_create_default_user_creates_new(self, service: UserService) -> None:
        """Test creating default user when it doesn't exist."""
        user = service.get_or_create_default_user()

        assert user.username == "demo_user"
        assert user.email == "demo@insighthub.local"
        assert user.full_name == "Demo User"

    def test_get_or_create_default_user_returns_existing(self, service: UserService) -> None:
        """Test getting existing default user."""
        user1 = service.get_or_create_default_user()
        user2 = service.get_or_create_default_user()

        assert user1.id == user2.id
        assert user1.username == user2.username
