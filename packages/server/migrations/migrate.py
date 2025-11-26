#!/usr/bin/env python3
"""Simple migration runner for PostgreSQL."""

import os
import sys
from pathlib import Path

import psycopg2


def run_migrations(database_url: str, migrations_dir: str = "migrations"):
    """
    Run all migration files in order.

    Args:
        database_url: PostgreSQL connection string
        migrations_dir: Directory containing migration SQL files
    """
    migrations_path = Path(__file__).parent / migrations_dir

    if not migrations_path.exists():
        print(f"Migrations directory not found: {migrations_path}")
        return

    # Get all SQL files sorted by name
    migration_files = sorted(migrations_path.glob("*.sql"))

    if not migration_files:
        print("No migration files found")
        return

    print(f"Found {len(migration_files)} migration(s)")

    # Connect to database
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print(f"Connected to database: {database_url.split('@')[1] if '@' in database_url else 'database'}")

        # Run each migration
        for migration_file in migration_files:
            print(f"\nRunning migration: {migration_file.name}")

            with open(migration_file, "r") as f:
                sql = f.read()

            try:
                cursor.execute(sql)
                print(f"  ✓ {migration_file.name} completed successfully")
            except Exception as e:
                print(f"  ✗ {migration_file.name} failed: {e}")
                sys.exit(1)

        cursor.close()
        conn.close()

        print("\n✓ All migrations completed successfully!")

    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://insighthub:insighthub_dev@localhost:5432/insighthub",
    )

    print("InsightHub Migration Runner")
    print("===========================\n")
    print(f"Database URL: {database_url.split('@')[1] if '@' in database_url else database_url}\n")

    run_migrations(database_url)
