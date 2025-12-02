"""Integration tests for database infrastructure."""

import pytest

from src.infrastructure.sql_database.factory import create_database
from src.infrastructure.models import User
from src.infrastructure.repositories.users.sql_user_repository import SqlUserRepository
from src.infrastructure.repositories.workspaces.sql_workspace_repository import (
    SqlWorkspaceRepository,
)


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test cases for database operations."""

    def test_sqlite_database_basic_operations(self):
        """Test basic SQLite database operations."""
        # Create in-memory SQLite database for testing
        db = create_database("sqlite:///:memory:")

        # Create a test table
        db.execute(
            """
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """
        )

        # Insert test data
        rows_affected = db.execute(
            "INSERT INTO test_users (name, email) VALUES (?, ?)", ("John Doe", "john@example.com")
        )
        assert rows_affected == 1

        # Fetch the inserted data
        user = db.fetch_one("SELECT * FROM test_users WHERE id = ?", (1,))
        assert user is not None
        assert user["name"] == "John Doe"
        assert user["email"] == "john@example.com"

        # Insert another user
        db.execute(
            "INSERT INTO test_users (name, email) VALUES (?, ?)", ("Jane Smith", "jane@example.com")
        )

        # Fetch all users
        users = db.fetch_all("SELECT * FROM test_users ORDER BY id")
        assert len(users) == 2
        assert users[0]["name"] == "John Doe"
        assert users[1]["name"] == "Jane Smith"

        # Clean up
        db.close()

    def test_database_singleton_behavior(self):
        """Test that database factory returns singleton instances."""
        db1 = create_database("sqlite:///:memory:")
        db2 = create_database("sqlite:///:memory:")

        # Should be the same instance
        assert db1 is db2

        # Clean up
        db1.close()

    def test_sql_user_repository_operations(self):
        """Test SQL user repository with SQLite."""
        # Create unique in-memory database for this test
        import uuid

        db_url = f"sqlite:///{uuid.uuid4()}.db"
        db = create_database(db_url)

        # Create tables
        db.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                theme_preference TEXT DEFAULT 'dark',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create repository
        repo = SqlUserRepository(db)

        # Test user creation
        user = User("testuser", "test@example.com", User.hash_password("password123"), "Test User")
        created_user = repo.create(user)

        assert created_user.id is not None
        assert created_user.username == "testuser"
        assert created_user.email == "test@example.com"
        assert created_user.check_password("password123")

        # Test user retrieval
        retrieved = repo.get_by_id(created_user.id)
        assert retrieved is not None
        assert retrieved.username == "testuser"

        retrieved_by_username = repo.get_by_username("testuser")
        assert retrieved_by_username is not None
        assert retrieved_by_username.email == "test@example.com"

        retrieved_by_email = repo.get_by_email("test@example.com")
        assert retrieved_by_email is not None
        assert retrieved_by_email.username == "testuser"

        # Test user update
        updated = repo.update(created_user.id, full_name="Updated Name")
        assert updated is not None
        assert updated.full_name == "Updated Name"

        # Test user listing
        users = repo.list_all()
        assert len(users) == 1
        assert users[0].username == "testuser"

        # Test user count
        count = repo.count_all()
        assert count == 1

        # Test user deletion
        result = repo.delete(created_user.id)
        assert result is True

        # Verify user is gone
        deleted_user = repo.get_by_id(created_user.id)
        assert deleted_user is None

        # Clean up
        db.close()

    def test_sql_workspace_repository_operations(self):
        """Test SQL workspace repository with SQLite."""
        # Create unique in-memory database for this test
        import uuid

        db_url = f"sqlite:///{uuid.uuid4()}.db"
        db = create_database(db_url)

        # Create tables
        db.execute(
            """
            CREATE TABLE workspaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                rag_type TEXT NOT NULL DEFAULT 'vector',
                status TEXT NOT NULL DEFAULT 'ready',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create repository
        repo = SqlWorkspaceRepository(db)

        # Test workspace creation
        workspace = repo.create(
            user_id=1, name="Test Workspace", description="A test workspace", rag_type="vector"
        )
        assert workspace.id is not None
        assert workspace.user_id == 1
        assert workspace.name == "Test Workspace"
        assert workspace.description == "A test workspace"
        assert workspace.rag_type == "vector"
        assert workspace.status == "ready"

        # Test workspace retrieval
        retrieved = repo.get_by_id(workspace.id)
        assert retrieved is not None
        assert retrieved.name == "Test Workspace"

        # Test getting workspaces by user
        user_workspaces = repo.get_by_user(1)
        assert len(user_workspaces) == 1
        assert user_workspaces[0].name == "Test Workspace"

        # Test workspace update
        updated = repo.update(workspace.id, name="Updated Name", status="provisioning")
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.status == "provisioning"

        # Test workspace deletion
        result = repo.delete(workspace.id)
        assert result is True

        # Verify workspace is gone
        deleted_workspace = repo.get_by_id(workspace.id)
        assert deleted_workspace is None

        # Clean up
        db.close()

    def test_database_transaction_rollback(self):
        """Test database transaction rollback on error."""
        import uuid

        db_url = f"sqlite:///{uuid.uuid4()}.db"
        db = create_database(db_url)

        # Create table
        db.execute(
            """
            CREATE TABLE test_data (
                id INTEGER PRIMARY KEY,
                value TEXT NOT NULL
            )
        """
        )

        # Insert initial data
        db.execute("INSERT INTO test_data (value) VALUES (?)", ("initial",))

        # Verify data exists
        result = db.fetch_one("SELECT * FROM test_data WHERE id = ?", (1,))
        assert result is not None
        assert result["value"] == "initial"

        # Test transaction rollback by attempting invalid operation
        # SQLite doesn't support explicit transactions in this abstraction layer,
        # so we'll test that invalid data is rejected
        try:
            # This should fail due to NOT NULL constraint
            db.execute("INSERT INTO test_data (value) VALUES (?)", (None,))
        except Exception:
            pass

        # Check that the invalid insert was not committed
        results = db.fetch_all("SELECT * FROM test_data")
        assert len(results) == 1  # Only the initial row should exist
        assert results[0]["value"] == "initial"

        # Clean up
        db.close()

    def test_database_connection_reuse(self):
        """Test that database connections are properly reused."""
        import uuid

        db_url = f"sqlite:///{uuid.uuid4()}.db"
        db1 = create_database(db_url)
        db2 = create_database(db_url)

        # Should be the same instance
        assert db1 is db2

        # Both should work
        db1.execute("CREATE TABLE test (id INTEGER)")
        db2.execute("INSERT INTO test VALUES (1)")

        result = db1.fetch_one("SELECT * FROM test")
        assert result is not None
        assert result["id"] == 1

        # Clean up
        db1.close()
