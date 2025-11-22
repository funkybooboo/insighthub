import os
from typing import Any, Dict, List, Optional
import psycopg
from psycopg.rows import dict_row

from .sql_database import SqlDatabase

class PostgresSQLDatabase(SqlDatabase):
    """Concrete PostgreSQL database using direct SQL queries."""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        self._conn: Optional[psycopg.Connection] = None

    def _connect(self):
        if self._conn is None or self._conn.closed:
            self._conn = psycopg.connect(self.database_url, row_factory=dict_row)

    def execute(self, query: str, params: Optional[dict] = None) -> None:
        self._connect()
        with self._conn.cursor() as cur:
            cur.execute(query, params)
        self._conn.commit()

    def fetchone(self, query: str, params: Optional[dict] = None) -> Optional[Dict[str, Any]]:
        self._connect()
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def fetchall(self, query: str, params: Optional[dict] = None) -> List[Dict[str, Any]]:
        self._connect()
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute_many(self, query: str, params_list: List[dict]) -> None:
        self._connect()
        with self._conn.cursor() as cur:
            cur.executemany(query, params_list)
        self._conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
