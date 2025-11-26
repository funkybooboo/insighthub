"""Database factory for creating database instances."""

import threading

from src.infrastructure.database.postgres_sql_database import PostgresSqlDatabase
from src.infrastructure.database.sql_database import SqlDatabase


def create_database(db_url: str) -> SqlDatabase:
    """Create or return a singleton database instance for the given URL.

    Args:
        db_url: Database connection URL

    Returns:
        SqlDatabase instance (singleton per URL)

    Raises:
        ValueError: If database type is not supported
    """
    global _database_instances

    if db_url not in _database_instances:
        with _database_lock:
            # Double-check pattern for thread safety
            if db_url not in _database_instances:
                if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
                    _database_instances[db_url] = PostgresSqlDatabase(db_url)
                elif db_url.startswith("sqlite://"):
                    # For now, we'll use PostgreSQL implementation as a placeholder
                    # In a real implementation, this would create a SQLite database
                    raise NotImplementedError("SQLite database not yet implemented")
                else:
                    raise ValueError(f"Unsupported database URL scheme: {db_url}")

    return _database_instances[db_url]


# Database singleton instances and locks
_database_instances: dict[str, SqlDatabase] = {}
_database_lock = threading.Lock()


def create_database_from_config() -> SqlDatabase:
    """Create or return the singleton database instance using the current configuration.

    Returns:
        SqlDatabase instance (singleton)
    """
    from src.infrastructure import config

    db_url = getattr(config, "DATABASE_URL", getattr(config, "database_url", "sqlite:///insighthub.db"))
    return create_database(db_url)


def close_database(url: str | None = None) -> None:
    """Close database connection(s).

    Args:
        url: Specific database URL to close. If None, closes all database connections.

    This should be called when the application is shutting down.
    """
    global _database_instances

    with _database_lock:
        if url is not None:
            # Close specific database instance
            if url in _database_instances:
                _database_instances[url].close()
                del _database_instances[url]
        else:
            # Close all database instances
            for db_url, db_instance in _database_instances.items():
                db_instance.close()
            _database_instances.clear()
