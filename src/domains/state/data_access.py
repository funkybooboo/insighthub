"""State data access layer - coordinates cache and repository."""

import json
from datetime import datetime
from typing import Optional

from src.domains.state.models import State
from src.domains.state.repositories import StateRepository
from src.infrastructure.cache.cache import Cache
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


class StateDataAccess:
    """Data access layer for State - handles caching + persistence."""

    def __init__(self, repository: StateRepository, cache: Optional[Cache] = None):
        """Initialize data access layer.

        Args:
            repository: State repository for database operations
            cache: Optional cache for performance optimization
        """
        self.repository = repository  # Exposed for operations not handled by this layer
        self.cache = cache

    def get(self) -> Optional[State]:
        """Get the current application state with caching.

        Returns:
            State if found, None otherwise
        """
        # Try cache first
        cache_key = "cli_state:1"
        cached_json = self.cache.get(cache_key) if self.cache else None

        if cached_json:
            try:
                data = json.loads(cached_json)
                return State(
                    id=data["id"],
                    current_workspace_id=data.get("current_workspace_id"),
                    current_session_id=data.get("current_session_id"),
                    updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
                )
            except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                logger.warning(f"Cache deserialization error for state: {e}")

        # Cache miss - fetch from database
        state = self.repository.get()

        if state and self.cache:
            self._cache_state(state)

        return state

    def set_current_workspace(self, workspace_id: Optional[int]) -> None:
        """Set the current workspace ID.

        Args:
            workspace_id: Workspace ID or None
        """
        self.repository.set_current_workspace(workspace_id)
        self._invalidate_cache()

    def set_current_session(self, session_id: Optional[int]) -> None:
        """Set the current session ID.

        Args:
            session_id: Session ID or None
        """
        self.repository.set_current_session(session_id)
        self._invalidate_cache()

    def _cache_state(self, state: State) -> None:
        """Cache state data.

        Args:
            state: State to cache
        """
        if not self.cache:
            return

        cache_key = "cli_state:1"
        cache_value = json.dumps({
            "id": state.id,
            "current_workspace_id": state.current_workspace_id,
            "current_session_id": state.current_session_id,
            "updated_at": state.updated_at.isoformat() if state.updated_at else None,
        })
        self.cache.set(cache_key, cache_value, ttl=60)  # Cache for 1 minute (state changes frequently)

    def _invalidate_cache(self) -> None:
        """Invalidate state cache."""
        if self.cache:
            cache_key = "cli_state:1"
            self.cache.delete(cache_key)
