"""Integration tests for SqlDatabase with a real PostgreSQL instance."""

import pytest

from src.infrastructure.sql_database import SqlDatabase


@pytest.mark.integration
class TestSqlDatabaseIntegration:
    """PostgreSQL integration tests for the SqlDatabase component."""

    def test_database_connection_and_health_check(self, db_instance: SqlDatabase):
        """Test that the database connection is established and the health check passes."""
        assert db_instance.conn is not None
        assert db_instance.health_check() is True

    def test_execute_and_fetch_operations(self, db_instance: SqlDatabase):
        """Test that we can execute queries and fetch results from the database."""
        # Arrange: Create a test table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS test_users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL
        );
        """
        rows_affected = db_instance.execute(create_table_query)
        assert rows_affected >= -1  # Should be 0 if table exists, or -1 on some systems

        # Act: Insert data
        insert_query = "INSERT INTO test_users (name, email) VALUES (%s, %s);"
        rows_affected = db_instance.execute(insert_query, ("Test User", "test@example.com"))
        assert rows_affected == 1

        # Assert: Fetch one record
        fetch_one_query = "SELECT * FROM test_users WHERE email = %s;"
        user = db_instance.fetch_one(fetch_one_query, ("test@example.com",))
        assert user is not None
        assert user["name"] == "Test User"

        # Act: Insert another user
        db_instance.execute(insert_query, ("Another User", "another@example.com"))

        # Assert: Fetch all records
        fetch_all_query = "SELECT * FROM test_users ORDER BY id;"
        users = db_instance.fetch_all(fetch_all_query)
        assert len(users) == 2
        assert users[0]["name"] == "Test User"
        assert users[1]["name"] == "Another User"

    def test_execute_with_no_results(self, db_instance: SqlDatabase):
        """Test an execute operation that affects no rows."""
        rows_affected = db_instance.execute("DELETE FROM test_users WHERE 1=0;")
        assert rows_affected == 0

    def test_fetch_one_with_no_results(self, db_instance: SqlDatabase):
        """Test fetching one record when no records match."""
        # Arrange: Create table and ensure it's empty
        db_instance.execute("CREATE TABLE IF NOT EXISTS no_data (id INT);")
        db_instance.execute("DELETE FROM no_data;")

        # Act & Assert
        result = db_instance.fetch_one("SELECT * FROM no_data WHERE id = 1;")
        assert result is None

    def test_fetch_all_with_no_results(self, db_instance: SqlDatabase):
        """Test fetching all records from an empty table."""
        # Arrange: Create table and ensure it's empty
        db_instance.execute("CREATE TABLE IF NOT EXISTS empty_table (id INT);")
        db_instance.execute("DELETE FROM empty_table;")

        # Act & Assert
        results = db_instance.fetch_all("SELECT * FROM empty_table;")
        assert results == []
