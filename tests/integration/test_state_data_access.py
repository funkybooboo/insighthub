"""Integration tests for the StateDataAccess component."""

import pytest

from src.domains.state.data_access import StateDataAccess
from src.domains.state.repositories import StateRepository
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.sql_database import SqlDatabase


@pytest.mark.integration
class TestStateDataAccessIntegration:
    """Integration tests for the StateDataAccess component."""

    @pytest.fixture(scope="function")
    def state_repository(self, db_session: SqlDatabase) -> StateRepository:
        """Fixture to create a StateRepository."""
        return StateRepository(db_session)

    @pytest.fixture(scope="function")
    def data_access_without_cache(self, state_repository: StateRepository) -> StateDataAccess:
        """Fixture for StateDataAccess without a cache."""
        return StateDataAccess(repository=state_repository, cache=None)

    @pytest.fixture(scope="function")
    def data_access_with_cache(
        self, state_repository: StateRepository, cache_instance: RedisCache
    ) -> StateDataAccess:
        """Fixture for StateDataAccess with a Redis cache."""
        return StateDataAccess(repository=state_repository, cache=cache_instance)

    @pytest.fixture(scope="function")
    def setup_session(self, db_session: SqlDatabase, setup_workspace):
        """Fixture to set up a chat session for testing."""
        # Create a chat session
        cs_result = db_session.fetch_one(
            "INSERT INTO chat_sessions (workspace_id, title) VALUES (%s, %s) RETURNING id",
            (setup_workspace.id, "test-cs"),
        )
        assert cs_result is not None
        session_id = cs_result["id"]

        return session_id

    def test_get_initial_state(self, data_access_without_cache: StateDataAccess):
        """Test getting the initial state."""
        # Act
        state = data_access_without_cache.get()

        # Assert
        assert state is not None
        assert isinstance(state, dict) or hasattr(state, "id")
        assert state.id == 1
        assert state.current_workspace_id is None
        assert state.current_session_id is None

    def test_set_and_get_workspace(
        self,
        data_access_with_cache: StateDataAccess,
        setup_workspace,
    ):
        """Test setting and getting the current workspace."""
        # Arrange
        workspace_id = setup_workspace.id

        # Act
        data_access_with_cache.set_current_workspace(workspace_id)
        state = data_access_with_cache.get()

        # Assert
        assert state is not None
        assert state.current_workspace_id == workspace_id
        assert data_access_with_cache.cache is not None
        assert data_access_with_cache.cache.exists("cli_state:1")

    def test_set_and_get_session(
        self,
        data_access_with_cache: StateDataAccess,
        setup_session,
    ):
        """Test setting and getting the current session."""
        # Arrange
        session_id = setup_session

        # Act
        data_access_with_cache.set_current_session(session_id)
        state = data_access_with_cache.get()

        # Assert
        assert state is not None
        assert state.current_session_id == session_id
        assert data_access_with_cache.cache is not None
        assert data_access_with_cache.cache.exists("cli_state:1")

    def test_cache_invalidation_on_set(
        self,
        data_access_with_cache: StateDataAccess,
        setup_workspace,
    ):
        """Test that the cache is invalidated when setting state."""
        # Arrange
        workspace_id = setup_workspace.id
        _ = data_access_with_cache.get()  # Populate cache
        assert data_access_with_cache.cache is not None
        assert data_access_with_cache.cache.exists("cli_state:1")

        # Act
        data_access_with_cache.set_current_workspace(workspace_id)

        # Assert
        assert data_access_with_cache.cache is not None
        assert not data_access_with_cache.cache.exists("cli_state:1")
        state = data_access_with_cache.get()
        assert state is not None
        assert state.current_workspace_id == workspace_id
