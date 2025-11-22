import os
from typing import Any

import psycopg2
import psycopg2.extras

from .sql_database import SqlDatabase


class PostgresSQLDatabase(SqlDatabase):
    """Concrete PostgreSQL database using direct SQL queries."""

    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        self._conn: psycopg2.extensions.connection | None = None

    def _connect(self) -> None:
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(
                self.database_url, cursor_factory=psycopg2.extras.RealDictCursor
            )

    def execute(self, query: str, params: dict[str, Any] | None = None) -> None:
        self._connect()
        assert self._conn is not None
        with self._conn.cursor() as cur:
            cur.execute(query, params)
        self._conn.commit()

    def fetchone(self, query: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        self._connect()
        assert self._conn is not None
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def fetchall(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        self._connect()
        assert self._conn is not None
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute_many(self, query: str, params_list: list[dict[str, Any]]) -> None:
        self._connect()
        assert self._conn is not None
        with self._conn.cursor() as cur:
            cur.executemany(query, params_list)
        self._conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
