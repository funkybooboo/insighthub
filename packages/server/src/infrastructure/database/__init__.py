"""Database infrastructure."""

from .factory import close_database, create_database, create_database_from_config

# Import concrete implementations after SqlDatabase is available
from .postgres_sql_database import PostgresSqlDatabase
from .sql_database import SqlDatabase

__all__ = [
    "SqlDatabase",
    "PostgresSqlDatabase",
    "create_database",
    "create_database_from_config",
    "close_database",
]


def get_db():
    """Get database connection as a context manager."""
    # For context manager usage, create a new connection each time
    # This is separate from the singleton used for persistent connections
    db = create_database_from_config()  # This will return the singleton
    try:
        yield db
    finally:
        # Don't close the singleton connection
        pass
