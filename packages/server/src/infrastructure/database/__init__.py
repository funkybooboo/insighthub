"""Database infrastructure for InsightHub server."""

from collections.abc import Generator
from pathlib import Path

import psycopg2
import psycopg2.extras
from shared.database.sql import PostgresSQLDatabase, SqlDatabase

from src import config

# Global database instance (lazy initialized)
_db: PostgresSQLDatabase | None = None


def get_db() -> Generator[SqlDatabase, None, None]:
    """Get a database connection."""
    global _db
    if _db is None:
        _db = PostgresSQLDatabase(config.DATABASE_URL)
    yield _db


def init_db(db_url: str | None = None) -> None:
    """Initialize the database by running migration SQL files."""
    url = db_url or config.DATABASE_URL
    migrations_dir = Path(__file__).parent.parent.parent.parent / "migrations"

    # Get all migration files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))

    conn = psycopg2.connect(url)
    try:
        with conn.cursor() as cur:
            for migration_file in migration_files:
                sql = migration_file.read_text()
                cur.execute(sql)
        conn.commit()
    finally:
        conn.close()


def run_sql(sql: str, db_url: str | None = None) -> None:
    """Run arbitrary SQL against the database."""
    url = db_url or config.DATABASE_URL

    conn = psycopg2.connect(url)
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    finally:
        conn.close()
