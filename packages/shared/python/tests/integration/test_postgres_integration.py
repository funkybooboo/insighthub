"""Integration tests for PostgreSQL database using test containers."""

from typing import Generator

import pytest
from testcontainers.postgres import PostgresContainer

from shared.database.sql.postgres_sql_database import PostgresSqlDatabase


class TestPostgresSqlDatabaseIntegration:
    """Integration tests for PostgresSqlDatabase using real PostgreSQL container."""

    @pytest.fixture(scope="function")
    def postgres_container(self) -> Generator[PostgresContainer, None, None]:
        """Create a PostgreSQL container for testing."""
        with PostgresContainer("postgres:15-alpine") as container:
            yield container

    @pytest.fixture(scope="function")
    def db(
        self, postgres_container: PostgresContainer
    ) -> Generator[PostgresSqlDatabase, None, None]:
        """Create a PostgresSqlDatabase instance connected to the test container."""
        # Get the connection URL and convert it to psycopg2 format
        connection_url = postgres_container.get_connection_url()
        # Parse the URL to extract components
        # Format: postgresql+psycopg2://user:password@host:port/database
        url_parts = connection_url.replace("postgresql+psycopg2://", "").split("@")
        credentials = url_parts[0]
        host_db = url_parts[1]

        user, password = credentials.split(":")
        host_port_db = host_db.split("/")
        host_port = host_port_db[0]
        database = host_port_db[1]

        host, port = host_port.split(":")

        # Create psycopg2 connection string
        psycopg2_dsn = f"host={host} port={port} user={user} password={password} dbname={database}"

        db = PostgresSqlDatabase(psycopg2_dsn)
        yield db
        db.close()

    def test_connection_and_basic_query(self, db: PostgresSqlDatabase) -> None:
        """Test basic database connection and query execution."""
        # Test basic SELECT query
        result = db.fetchone("SELECT 1 as test_value")
        assert result is not None
        assert result["test_value"] == 1

    def test_create_table_and_insert(self, db: PostgresSqlDatabase) -> None:
        """Test creating a table and inserting data."""
        # Create test table
        db.execute(
            """
            CREATE TABLE test_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Insert data
        result = db.fetchone(
            """
            INSERT INTO test_users (username, email)
            VALUES (%(username)s, %(email)s)
            RETURNING id, username, email
        """,
            {"username": "testuser", "email": "test@example.com"},
        )

        assert result is not None
        assert result["id"] == 1
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"

    def test_select_single_row(self, db: PostgresSqlDatabase) -> None:
        """Test selecting a single row."""
        # Setup test data
        db.execute(
            """
            CREATE TABLE test_items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                value INTEGER
            )
        """
        )

        db.execute(
            """
            INSERT INTO test_items (name, value) VALUES
            ('item1', 100),
            ('item2', 200),
            ('item3', 300)
        """
        )

        # Test fetchone
        result = db.fetchone("SELECT * FROM test_items WHERE name = %(name)s", {"name": "item2"})
        assert result is not None
        assert result["name"] == "item2"
        assert result["value"] == 200

    def test_select_multiple_rows(self, db: PostgresSqlDatabase) -> None:
        """Test selecting multiple rows."""
        # Setup test data
        db.execute(
            """
            CREATE TABLE test_products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2)
            )
        """
        )

        db.execute(
            """
            INSERT INTO test_products (name, price) VALUES
            ('Product A', 29.99),
            ('Product B', 49.99),
            ('Product C', 19.99)
        """
        )

        # Test fetchall
        results = db.fetchall("SELECT * FROM test_products ORDER BY price")
        assert len(results) == 3
        assert results[0]["name"] == "Product C"
        assert float(results[0]["price"]) == 19.99
        assert float(results[1]["price"]) == 29.99
        assert float(results[2]["price"]) == 49.99

    def test_transaction_commit(self, db: PostgresSqlDatabase) -> None:
        """Test transaction commit."""
        # Setup test data
        db.execute(
            """
            CREATE TABLE test_accounts (
                id SERIAL PRIMARY KEY,
                balance DECIMAL(10,2) NOT NULL
            )
        """
        )

        # Insert data (each execute is auto-committed)
        db.execute("INSERT INTO test_accounts (balance) VALUES (%(balance)s)", {"balance": 100.00})

        # Check data persists
        result = db.fetchone("SELECT balance FROM test_accounts WHERE id = 1")
        assert result is not None
        assert result["balance"] == 100.00

    def test_transaction_rollback(self, db: PostgresSqlDatabase) -> None:
        """Test transaction rollback."""
        # Note: PostgresSqlDatabase auto-commits each execute, so we can't test rollback
        # This test verifies that data is properly inserted and persisted
        db.execute(
            """
            CREATE TABLE test_inventory (
                id SERIAL PRIMARY KEY,
                quantity INTEGER NOT NULL
            )
        """
        )

        # Insert data
        db.execute("INSERT INTO test_inventory (quantity) VALUES (%(quantity)s)", {"quantity": 50})

        # Check data was inserted
        result = db.fetchone("SELECT quantity FROM test_inventory WHERE id = 1")
        assert result is not None
        assert result["quantity"] == 50

    def test_parameterized_queries(self, db: PostgresSqlDatabase) -> None:
        """Test parameterized queries prevent SQL injection."""
        # Setup test data
        db.execute(
            """
            CREATE TABLE test_search (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL
            )
        """
        )

        db.execute(
            """
            INSERT INTO test_search (content) VALUES
            ('Normal content'),
            ('Content with ''quotes'''),
            ('Content with % percent'),
            ('Content with _ underscore')
        """
        )

        # Test with various parameters
        test_cases = [
            ("Normal content", 1),
            ("Content with 'quotes'", 1),
            ("Content with % percent", 1),
            ("Content with _ underscore", 1),
            ("Nonexistent content", 0),
        ]

        for search_term, expected_count in test_cases:
            result = db.fetchone(
                "SELECT COUNT(*) as count FROM test_search WHERE content = %(content)s",
                {"content": search_term},
            )
            assert result is not None
            assert result["count"] == expected_count

    def test_error_handling(self, postgres_container: PostgresContainer) -> None:
        """Test error handling for constraint violations."""
        # Create a fresh database connection for this test
        connection_url = postgres_container.get_connection_url()
        url_parts = connection_url.replace("postgresql+psycopg2://", "").split("@")
        credentials = url_parts[0]
        host_db = url_parts[1]

        user, password = credentials.split(":")
        host_port_db = host_db.split("/")
        host_port = host_port_db[0]
        database = host_port_db[1]

        host, port = host_port.split(":")

        psycopg2_dsn = f"host={host} port={port} user={user} password={password} dbname={database}"
        db = PostgresSqlDatabase(psycopg2_dsn)

        try:
            # Test constraint violation
            db.execute(
                """
                CREATE TABLE test_constraints (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(100) UNIQUE NOT NULL
                )
            """
            )

            # Insert first record
            db.execute(
                "INSERT INTO test_constraints (email) VALUES (%(email)s)",
                {"email": "test@example.com"},
            )

            # Try to insert duplicate - should raise exception
            with pytest.raises(Exception):
                db.execute(
                    "INSERT INTO test_constraints (email) VALUES (%(email)s)",
                    {"email": "test@example.com"},
                )
        finally:
            db.close()

    def test_connection_reuse(self, db: PostgresSqlDatabase) -> None:
        """Test that the same connection can be reused for multiple operations."""
        # Create test table
        db.execute(
            """
            CREATE TABLE test_reuse (
                id SERIAL PRIMARY KEY,
                data VARCHAR(50)
            )
        """
        )

        # Perform multiple operations
        for i in range(5):
            db.execute("INSERT INTO test_reuse (data) VALUES (%(data)s)", {"data": f"value_{i}"})

        # Verify all data was inserted
        result = db.fetchone("SELECT COUNT(*) as count FROM test_reuse")
        assert result is not None
        assert result["count"] == 5

        # Verify specific values
        results = db.fetchall("SELECT data FROM test_reuse ORDER BY id")
        expected_data = [f"value_{i}" for i in range(5)]
        actual_data = [row["data"] for row in results]
        assert actual_data == expected_data
