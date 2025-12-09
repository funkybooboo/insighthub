"""Integration tests for SqlDatabase error handling with a real PostgreSQL instance."""

import pytest

from src.infrastructure.sql_database import DatabaseException, SqlDatabase


@pytest.mark.integration
class TestSqlDatabaseErrorHandlingIntegration:
    """PostgreSQL integration tests for SqlDatabase error handling."""

    def test_init_raises_database_exception_on_connection_failure(self, postgres_container):
        """Test that SqlDatabase.__init__ raises DatabaseException on connection failure."""
        # Arrange - use the postgres container but with wrong credentials
        connection_url = postgres_container.get_connection_url().replace("+psycopg2", "")
        # Replace valid credentials with invalid ones
        invalid_db_url = connection_url.replace("test", "invalid_user").replace(
            "test", "invalid_password", 1
        )

        # Act & Assert
        with pytest.raises(DatabaseException) as excinfo:
            SqlDatabase(invalid_db_url)
        assert "connect" in str(excinfo.value.operation)
        assert "password authentication failed" in str(excinfo.value.message)

    def test_execute_raises_database_exception_on_invalid_query(self, db_instance: SqlDatabase):
        """Test that execute raises DatabaseException for an invalid query."""
        # Act & Assert
        with pytest.raises(DatabaseException) as excinfo:
            db_instance.execute("INSERT INTO nonexistent_table (id) VALUES (1);")
        assert "execute" in str(excinfo.value.operation)
        assert 'relation "nonexistent_table" does not exist' in str(excinfo.value.message)

    def test_fetch_one_raises_database_exception_on_invalid_query(self, db_instance: SqlDatabase):
        """Test that fetch_one raises DatabaseException for an invalid query."""
        # Act & Assert
        with pytest.raises(DatabaseException) as excinfo:
            db_instance.fetch_one("SELECT * FROM another_nonexistent_table;")
        assert "fetch_one" in str(excinfo.value.operation)
        assert 'relation "another_nonexistent_table" does not exist' in str(excinfo.value.message)

    def test_fetch_all_raises_database_exception_on_invalid_query(self, db_instance: SqlDatabase):
        """Test that fetch_all raises DatabaseException for an invalid query."""
        # Act & Assert
        with pytest.raises(DatabaseException) as excinfo:
            db_instance.fetch_all("SELECT * FROM yet_another_nonexistent_table;")
        assert "fetch_all" in str(excinfo.value.operation)
        assert 'relation "yet_another_nonexistent_table" does not exist' in str(
            excinfo.value.message
        )

    def test_execute_raises_database_exception_on_constraint_violation(
        self, db_instance: SqlDatabase
    ):
        """Test that execute raises DatabaseException on constraint violation."""
        # Arrange: Create a table with a unique constraint
        db_instance.execute(
            """
            CREATE TABLE IF NOT EXISTS unique_test (
                id SERIAL PRIMARY KEY,
                value VARCHAR(255) UNIQUE NOT NULL
            );
        """
        )
        db_instance.execute("INSERT INTO unique_test (value) VALUES (%s);", ("duplicate",))

        # Act & Assert
        with pytest.raises(DatabaseException) as excinfo:
            db_instance.execute("INSERT INTO unique_test (value) VALUES (%s);", ("duplicate",))
        assert "execute" in str(excinfo.value.operation)
        assert "duplicate key value violates unique constraint" in str(excinfo.value.message)
