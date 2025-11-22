#!/usr/bin/env python3
"""Database migration runner for InsightHub.

This script manages database migrations using raw SQL files.
No ORM is used - just plain PostgreSQL.

Usage:
    python migrations/migrate.py                    # Run pending migrations
    python migrations/migrate.py --status           # Show migration status
    python migrations/migrate.py --rollback         # Rollback last migration
    python migrations/migrate.py --create NAME      # Create new migration file
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import psycopg2


def get_connection_params() -> dict[str, str]:
    """Get database connection parameters from environment."""
    database_url = os.getenv("DATABASE_URL", "")

    if database_url:
        # Parse DATABASE_URL format: postgresql://user:password@host:port/dbname
        pattern = r"postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)"
        match = re.match(pattern, database_url)
        if match:
            return {
                "user": match.group(1),
                "password": match.group(2),
                "host": match.group(3),
                "port": match.group(4),
                "dbname": match.group(5),
            }

    # Fall back to individual env vars
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "dbname": os.getenv("POSTGRES_DB", "insighthub"),
    }


def get_connection() -> psycopg2.extensions.connection:
    """Get a database connection."""
    params = get_connection_params()
    conn = psycopg2.connect(**params)
    return conn


def ensure_migrations_table(conn: psycopg2.extensions.connection) -> None:
    """Ensure the migrations tracking table exists."""
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
        """
        )
    conn.commit()


def get_applied_migrations(conn: psycopg2.extensions.connection) -> set[str]:
    """Get set of already applied migration versions."""
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations ORDER BY version")
        return {row[0] for row in cur.fetchall()}


def get_migration_files(migrations_dir: Path) -> list[tuple[str, str, Path]]:
    """Get list of migration files sorted by version.

    Returns list of tuples: (version, name, path)
    """
    migrations = []
    for file in migrations_dir.glob("*.sql"):
        # Parse filename: 001_initial_schema.sql -> ("001", "initial_schema")
        match = re.match(r"(\d+)_(.+)\.sql", file.name)
        if match:
            version = match.group(1)
            name = match.group(2)
            migrations.append((version, name, file))

    return sorted(migrations, key=lambda x: x[0])


def run_migration(
    conn: psycopg2.extensions.connection, version: str, name: str, path: Path
) -> None:
    """Run a single migration file."""
    print(f"Running migration {version}_{name}...")

    sql = path.read_text()

    with conn.cursor() as cur:
        cur.execute(sql)
        cur.execute(
            "INSERT INTO schema_migrations (version, name) VALUES (%s, %s)",
            (version, name),
        )
    conn.commit()
    print(f"  Migration {version}_{name} applied successfully")


def migrate(migrations_dir: Path) -> int:
    """Run all pending migrations."""
    conn = get_connection()

    try:
        ensure_migrations_table(conn)
        applied = get_applied_migrations(conn)
        migrations = get_migration_files(migrations_dir)

        pending = [(v, n, p) for v, n, p in migrations if v not in applied]

        if not pending:
            print("No pending migrations")
            return 0

        print(f"Found {len(pending)} pending migration(s)")

        for version, name, path in pending:
            run_migration(conn, version, name, path)

        print(f"All {len(pending)} migration(s) completed successfully")
        return 0

    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        conn.rollback()
        return 1

    finally:
        conn.close()


def show_status(migrations_dir: Path) -> int:
    """Show migration status."""
    conn = get_connection()

    try:
        ensure_migrations_table(conn)
        applied = get_applied_migrations(conn)
        migrations = get_migration_files(migrations_dir)

        print("Migration Status:")
        print("-" * 60)

        for version, name, _ in migrations:
            status = "APPLIED" if version in applied else "PENDING"
            print(f"  [{status:7}] {version}_{name}")

        if not migrations:
            print("  No migration files found")

        return 0

    finally:
        conn.close()


def rollback(migrations_dir: Path) -> int:
    """Rollback the last applied migration."""
    print("Rollback not implemented - please manually revert changes")
    return 1


def create_migration(migrations_dir: Path, name: str) -> int:
    """Create a new migration file."""
    migrations = get_migration_files(migrations_dir)

    if migrations:
        last_version = int(migrations[-1][0])
        new_version = f"{last_version + 1:03d}"
    else:
        new_version = "001"

    # Sanitize name
    safe_name = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    filename = f"{new_version}_{safe_name}.sql"
    filepath = migrations_dir / filename

    template = f"""-- Migration: {new_version}_{safe_name}
-- Description: {name}
-- Created: {datetime.now().strftime('%Y-%m-%d')}

-- Add your SQL here

"""
    filepath.write_text(template)
    print(f"Created migration: {filepath}")
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument("--status", action="store_true", help="Show migration status")
    parser.add_argument("--rollback", action="store_true", help="Rollback last migration")
    parser.add_argument("--create", metavar="NAME", help="Create new migration")
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path(__file__).parent,
        help="Migrations directory",
    )

    args = parser.parse_args()

    if args.status:
        return show_status(args.dir)
    elif args.rollback:
        return rollback(args.dir)
    elif args.create:
        return create_migration(args.dir, args.create)
    else:
        return migrate(args.dir)


if __name__ == "__main__":
    sys.exit(main())
