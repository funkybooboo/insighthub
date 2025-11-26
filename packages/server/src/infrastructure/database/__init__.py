"""Database infrastructure - minimal stubs."""

from .sql_database import PostgresSqlDatabase, SqlDatabase

__all__ = ["SqlDatabase", "PostgresSqlDatabase"]


def get_db():
    """Get database connection - stub for now."""
    from src.infrastructure.context import create_database

    db = create_database()
    try:
        yield db
    finally:
        db.close()
