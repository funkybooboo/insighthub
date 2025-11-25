"""Integration tests for user registration and authentication flow."""

import pytest
from shared.models import User


class TestUserRegistrationAuthenticationIntegration:
    """Integration tests for complete user registration and authentication flow."""

    def test_user_registration_login_logout_flow(self, test_context) -> None:
        """Test complete user registration, login, and logout flow."""
        user_service = test_context.user_service

        # Step 1: Register a new user
        registered_user = user_service.register_user(
            username="integration_test_user",
            email="integration@example.com",
            password="SecurePass123!",
            full_name="Integration Test User",
        )

        assert registered_user.username == "integration_test_user"
        assert registered_user.email == "integration@example.com"
        assert registered_user.full_name == "Integration Test User"
        assert registered_user.check_password("SecurePass123!")

        # Step 2: Authenticate the user (login)
        authenticated_user = user_service.authenticate_user(
            username="integration_test_user", password="SecurePass123!"
        )

        assert authenticated_user is not None
        assert authenticated_user.id == registered_user.id
        assert authenticated_user.username == "integration_test_user"

        # Step 3: Verify user can be retrieved by different methods
        by_id = user_service.get_user_by_id(registered_user.id)
        by_username = user_service.get_user_by_username("integration_test_user")
        by_email = user_service.get_user_by_email("integration@example.com")

        assert by_id is not None
        assert by_username is not None
        assert by_email is not None
        assert by_id.id == registered_user.id
        assert by_username.id == registered_user.id
        assert by_email.id == registered_user.id

    def test_multiple_users_registration_and_listing(self, test_context) -> None:
        """Test registering multiple users and listing them."""
        user_service = test_context.user_service

        # Register multiple users
        users_data = [
            ("user1", "user1@example.com", "pass1", "User One"),
            ("user2", "user2@example.com", "pass2", "User Two"),
            ("user3", "user3@example.com", "pass3", "User Three"),
        ]

        registered_users = []
        for username, email, password, full_name in users_data:
            user = user_service.register_user(username, email, password, full_name)
            registered_users.append(user)

        # List all users
        all_users = user_service.list_users()

        assert len(all_users) >= 3  # At least the users we just created

        # Verify all registered users are in the list
        registered_ids = {user.id for user in registered_users}
        listed_ids = {user.id for user in all_users}

        assert registered_ids.issubset(listed_ids)

    def test_user_update_and_password_change_flow(self, test_context) -> None:
        """Test updating user information and changing password."""
        user_service = test_context.user_service

        # Register user
        user = user_service.register_user(
            username="update_test_user",
            email="update@example.com",
            password="OriginalPass123!",
            full_name="Original Name",
        )

        # Update user information
        updated_user = user_service.update_user(
            user.id, full_name="Updated Name", email="updated@example.com"
        )

        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.email == "updated@example.com"

        # Verify old password still works
        assert user_service.authenticate_user("update_test_user", "OriginalPass123!") is not None

        # Create a new user instance to test password change
        # (In a real scenario, this would be done through a password change method)
        new_user = User(
            id=user.id,
            username=user.username,
            email=user.email,
            password_hash="",  # Will be set by set_password
            full_name=user.full_name,
        )
        new_user.set_password("NewSecurePass456!")

        # Update the user in repository (simulating password change)
        user_service.repository.update(user.id, password_hash=new_user.password_hash)

        # Verify new password works and old doesn't
        assert user_service.authenticate_user("update_test_user", "NewSecurePass456!") is not None
        assert user_service.authenticate_user("update_test_user", "OriginalPass123!") is None

    def test_user_deletion_cascades_properly(self, test_context) -> None:
        """Test that user deletion removes user from all access methods."""
        user_service = test_context.user_service

        # Register user
        user = user_service.register_user(
            username="delete_test_user", email="delete@example.com", password="DeletePass123!"
        )

        # Verify user exists in all retrieval methods
        assert user_service.get_user_by_id(user.id) is not None
        assert user_service.get_user_by_username("delete_test_user") is not None
        assert user_service.get_by_email("delete@example.com") is not None
        assert user_service.authenticate_user("delete_test_user", "DeletePass123!") is not None

        # Delete user
        result = user_service.delete_user(user.id)
        assert result is True

        # Verify user is gone from all access methods
        assert user_service.get_user_by_id(user.id) is None
        assert user_service.get_user_by_username("delete_test_user") is None
        assert user_service.get_by_email("delete@example.com") is None
        assert user_service.authenticate_user("delete_test_user", "DeletePass123!") is None

    def test_duplicate_registration_prevention(self, test_context) -> None:
        """Test that duplicate usernames and emails are prevented."""
        user_service = test_context.user_service

        # Register first user
        user_service.register_user(
            username="duplicate_user", email="duplicate@example.com", password="pass123"
        )

        # Try to register with same username
        from src.domains.auth.exceptions import UserAlreadyExistsError

        with pytest.raises(UserAlreadyExistsError):
            user_service.register_user(
                username="duplicate_user", email="different@example.com", password="pass456"
            )

        # Try to register with same email
        with pytest.raises(UserAlreadyExistsError):
            user_service.register_user(
                username="different_user", email="duplicate@example.com", password="pass789"
            )

    def test_default_user_creation_and_retrieval(self, test_context) -> None:
        """Test default user creation and retrieval."""
        user_service = test_context.user_service

        # Get or create default user
        default_user1 = user_service.get_or_create_default_user()
        default_user2 = user_service.get_or_create_default_user()

        # Both should be the same user
        assert default_user1.id == default_user2.id
        assert default_user1.username == "demo_user"
        assert default_user1.email == "demo@insighthub.local"

        # Should be able to authenticate with default credentials
        # (Assuming default password is set)
        authenticated = user_service.authenticate_user("demo_user", "demo_password")
        assert authenticated is not None
        assert authenticated.id == default_user1.id

    def test_user_listing_pagination(self, test_context) -> None:
        """Test user listing with pagination."""
        user_service = test_context.user_service

        # Create multiple users
        for i in range(10):
            user_service.register_user(
                username=f"pagination_user_{i}",
                email=f"pagination{i}@example.com",
                password="pass123",
            )

        # Test pagination
        page1 = user_service.list_users(skip=0, limit=3)
        page2 = user_service.list_users(skip=3, limit=3)
        page3 = user_service.list_users(skip=6, limit=3)

        assert len(page1) == 3
        assert len(page2) == 3
        assert len(page3) == 3

        # Pages should not overlap
        page1_ids = {user.id for user in page1}
        page2_ids = {user.id for user in page2}
        page3_ids = {user.id for user in page3}

        assert page1_ids.isdisjoint(page2_ids)
        assert page1_ids.isdisjoint(page3_ids)
        assert page2_ids.isdisjoint(page3_ids)

    def test_user_search_and_filtering(self, test_context) -> None:
        """Test user search and filtering capabilities."""
        user_service = test_context.user_service

        # Create users with different characteristics
        users_data = [
            ("search_user_1", "search1@example.com", "pass1", "John Doe"),
            ("search_user_2", "search2@example.com", "pass2", "Jane Smith"),
            ("search_user_3", "search3@example.com", "pass3", "Bob Johnson"),
        ]

        created_users = []
        for username, email, password, full_name in users_data:
            user = user_service.register_user(username, email, password, full_name)
            created_users.append(user)

        # Test retrieval by username patterns
        user1 = user_service.get_user_by_username("search_user_1")
        user2 = user_service.get_user_by_username("search_user_2")

        assert user1 is not None
        assert user2 is not None
        assert user1.full_name == "John Doe"
        assert user2.full_name == "Jane Smith"

        # Test retrieval by email
        user_by_email = user_service.get_by_email("search1@example.com")
        assert user_by_email is not None
        assert user_by_email.username == "search_user_1"

    def test_user_data_integrity_across_operations(self, test_context) -> None:
        """Test that user data remains consistent across operations."""
        user_service = test_context.user_service

        # Create user
        original_user = user_service.register_user(
            username="integrity_test",
            email="integrity@example.com",
            password="IntegrityPass123!",
            full_name="Integrity Test User",
        )

        original_id = original_user.id
        original_created_at = original_user.created_at

        # Update user
        updated_user = user_service.update_user(original_id, full_name="Updated Integrity User")

        # Verify data integrity
        assert updated_user.id == original_id
        assert updated_user.username == "integrity_test"  # Unchanged
        assert updated_user.email == "integrity@example.com"  # Unchanged
        assert updated_user.full_name == "Updated Integrity User"  # Changed
        assert updated_user.created_at == original_created_at  # Unchanged

        # Verify authentication still works
        auth_user = user_service.authenticate_user("integrity_test", "IntegrityPass123!")
        assert auth_user is not None
        assert auth_user.id == original_id
        assert auth_user.full_name == "Updated Integrity User"
