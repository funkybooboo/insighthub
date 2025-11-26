"""Integration tests for database infrastructure."""

import pytest

from src.infrastructure.database.factory import create_database


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test cases for database operations."""

    def test_sqlite_database_basic_operations(self):
        """Test basic SQLite database operations."""
        # Create in-memory SQLite database for testing
        db = create_database("sqlite:///:memory:")

        # Create a test table
        db.execute("""
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """)

        # Insert test data
        rows_affected = db.execute(
            "INSERT INTO test_users (name, email) VALUES (?, ?)",
            ("John Doe", "john@example.com")
        )
        assert rows_affected == 1

        # Fetch the inserted data
        user = db.fetch_one("SELECT * FROM test_users WHERE id = ?", (1,))
        assert user is not None
        assert user["name"] == "John Doe"
        assert user["email"] == "john@example.com"

        # Insert another user
        db.execute(
            "INSERT INTO test_users (name, email) VALUES (?, ?)",
            ("Jane Smith", "jane@example.com")
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