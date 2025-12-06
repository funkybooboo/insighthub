"""Integration tests for the ChatSessionDataAccess component."""

import pytest
from returns.result import Success

from src.domains.workspace.chat.session.data_access import ChatSessionDataAccess
from src.domains.workspace.chat.session.repositories import ChatSessionRepository
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.sql_database import SqlDatabase


@pytest.mark.integration
class TestChatSessionDataAccessIntegration:
    """Integration tests for the ChatSessionDataAccess component."""

    @pytest.fixture(scope="function")
    def chat_session_repository(self, db_session: SqlDatabase) -> ChatSessionRepository:
        """Fixture to create a ChatSessionRepository."""
        return ChatSessionRepository(db_session)

    @pytest.fixture(scope="function")
    def data_access_without_cache(
        self, chat_session_repository: ChatSessionRepository
    ) -> ChatSessionDataAccess:
        """Fixture for ChatSessionDataAccess without a cache."""
        return ChatSessionDataAccess(repository=chat_session_repository, cache=None)

    @pytest.fixture(scope="function")
    def data_access_with_cache(
        self, chat_session_repository: ChatSessionRepository, cache_instance: RedisCache
    ) -> ChatSessionDataAccess:
        """Fixture for ChatSessionDataAccess with a Redis cache."""
        return ChatSessionDataAccess(repository=chat_session_repository, cache=cache_instance)

    def test_create_and_get_session(
        self, data_access_with_cache: ChatSessionDataAccess, setup_workspace
    ):
        """Test creating and retrieving a chat session."""
        # Arrange
        workspace_id = setup_workspace.id

        # Act
        create_result = data_access_with_cache.create(
            workspace_id=workspace_id, title="Test Session"
        )
        assert isinstance(create_result, Success)
        created_session = create_result.unwrap()

        retrieved_session = data_access_with_cache.get_by_id(created_session.id)

        # Assert
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
        assert retrieved_session.title == "Test Session"
        assert data_access_with_cache.cache is not None
        assert data_access_with_cache.cache.exists(f"chat_session:{created_session.id}")

    def test_get_sessions_by_workspace(
        self, data_access_with_cache: ChatSessionDataAccess, setup_workspace
    ):
        """Test retrieving all chat sessions for a workspace."""
        # Arrange
        workspace_id = setup_workspace.id
        data_access_with_cache.create(workspace_id=workspace_id, title="Session 1")
        data_access_with_cache.create(workspace_id=workspace_id, title="Session 2")

        # Act
        sessions = data_access_with_cache.get_by_workspace(workspace_id)

        # Assert
        assert len(sessions) == 2
        assert data_access_with_cache.cache is not None
        assert data_access_with_cache.cache.exists(f"workspace:{workspace_id}:chat_sessions")

    def test_update_session(self, data_access_with_cache: ChatSessionDataAccess, setup_workspace):
        """Test updating a chat session."""
        # Arrange
        workspace_id = setup_workspace.id
        create_result = data_access_with_cache.create(
            workspace_id=workspace_id, title="Initial Title"
        )
        created_session = create_result.unwrap()

        # Act
        updated = data_access_with_cache.update(created_session.id, title="Updated Title")

        # Assert
        assert updated is not None
        retrieved_session = data_access_with_cache.get_by_id(created_session.id)
        assert retrieved_session is not None
        assert retrieved_session.title == "Updated Title"

    def test_delete_session(self, data_access_with_cache: ChatSessionDataAccess, setup_workspace):
        """Test deleting a chat session."""
        # Arrange
        workspace_id = setup_workspace.id
        create_result = data_access_with_cache.create(
            workspace_id=workspace_id, title="To Be Deleted"
        )
        created_session = create_result.unwrap()
        _ = data_access_with_cache.get_by_id(created_session.id)
        assert data_access_with_cache.cache is not None
        assert data_access_with_cache.cache.exists(f"chat_session:{created_session.id}")

        # Act
        deleted = data_access_with_cache.delete(created_session.id)

        # Assert
        assert deleted is True
        assert data_access_with_cache.cache is not None
        assert not data_access_with_cache.cache.exists(f"chat_session:{created_session.id}")
        assert data_access_with_cache.get_by_id(created_session.id) is None
