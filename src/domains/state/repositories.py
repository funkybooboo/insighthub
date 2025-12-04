"""SQL implementation of StateRepository."""

from typing import Optional

from src.domains.state.models import State
from src.infrastructure.sql_database import SqlDatabase


class StateRepository:
    """SQL implementation of state repository."""

    def __init__(self, db: SqlDatabase):
        self.db = db

    def get(self) -> Optional[State]:
        """Get the current application state (single row)."""
        query = """
            SELECT id, current_workspace_id, current_session_id, updated_at
            FROM cli_state WHERE id = 1
        """
        result = self.db.fetch_one(query)
        if result:
            return State(**result)
        return None

    def set_current_workspace(self, workspace_id: int | None) -> None:
        """Set the current workspace ID."""
        query = "UPDATE cli_state SET current_workspace_id = %s WHERE id = 1"
        self.db.execute(query, (workspace_id,))

    def set_current_session(self, session_id: int | None) -> None:
        """Set the current session ID."""
        query = "UPDATE cli_state SET current_session_id = %s WHERE id = 1"
        self.db.execute(query, (session_id,))
