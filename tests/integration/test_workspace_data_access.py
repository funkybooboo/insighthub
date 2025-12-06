"""Integration tests for the WorkspaceDataAccess component."""

import pytest
from returns.result import Success

from src.domains.workspace.data_access import WorkspaceDataAccess
from src.domains.workspace.repositories import WorkspaceRepository
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.sql_database import SqlDatabase


@pytest.mark.integration
class TestWorkspaceDataAccessIntegration:
    """Integration tests for the WorkspaceDataAccess component."""

    @pytest.fixture(scope="function")
    def workspace_repository(self, db_session: SqlDatabase) -> WorkspaceRepository:
        """Fixture to create a WorkspaceRepository."""
        return WorkspaceRepository(db_session)

    @pytest.fixture(scope="function")
    def data_access_without_cache(
        self, workspace_repository: WorkspaceRepository
    ) -> WorkspaceDataAccess:
        """Fixture for WorkspaceDataAccess without a cache."""
        return WorkspaceDataAccess(repository=workspace_repository, cache=None)

    @pytest.fixture(scope="function")
    def data_access_with_cache(
        self, workspace_repository: WorkspaceRepository, cache_instance: RedisCache
    ) -> WorkspaceDataAccess:
        """Fixture for WorkspaceDataAccess with a Redis cache."""
        return WorkspaceDataAccess(repository=workspace_repository, cache=cache_instance)

    def test_create_and_get_workspace_no_cache_returns_expected_workspace(
        self, data_access_without_cache: WorkspaceDataAccess
    ):
        """Test creating and retrieving a workspace without caching."""
        # Arrange
        name = "Test Workspace (No Cache)"
        description = "A test workspace for integration tests."
        rag_type = "vector"

        # Act
        create_result = data_access_without_cache.create(name, description, rag_type)
        assert isinstance(create_result, Success)

        created_workspace = create_result.unwrap()
        retrieved_workspace = data_access_without_cache.get_by_id(created_workspace.id)

        # Assert
        assert retrieved_workspace is not None
        assert retrieved_workspace.id == created_workspace.id
        assert retrieved_workspace.name == name
        assert retrieved_workspace.description == description
        assert retrieved_workspace.rag_type == rag_type

    def test_create_workspace_returns_success_and_workspace(
        self, data_access_with_cache: WorkspaceDataAccess
    ):
        """Test that creating a workspace returns a Success result with the created workspace."""
        # Arrange
        name = "Test Workspace (Create Success)"
        description = "A test for successful workspace creation."
        rag_type = "graph"

        # Act
        create_result = data_access_with_cache.create(name, description, rag_type)
        assert isinstance(create_result, Success)
        created_workspace = create_result.unwrap()

        # Assert
        assert created_workspace.name == name
        assert created_workspace.description == description
        assert created_workspace.rag_type == rag_type
        assert created_workspace.id is not None

    def test_update_workspace_returns_success_and_updates_data(
        self, data_access_with_cache: WorkspaceDataAccess
    ):
        """Test that updating a workspace returns True and the data is updated."""
        # Arrange
        create_result = data_access_with_cache.create("Initial Name", "Initial Desc", "vector")
        assert isinstance(create_result, Success)
        created_workspace = create_result.unwrap()
        workspace_id = created_workspace.id

        # Act
        updated = data_access_with_cache.update(
            workspace_id, name="Updated Name", status="processing"
        )

        # Assert
        assert updated is True

        # Verify the database was updated by fetching again
        retrieved_workspace = data_access_with_cache.get_by_id(workspace_id)
        assert retrieved_workspace is not None
        assert retrieved_workspace.name == "Updated Name"
        assert retrieved_workspace.status == "processing"

    def test_delete_workspace_returns_success_and_removes_data(
        self, data_access_with_cache: WorkspaceDataAccess
    ):
        """Test that deleting a workspace returns True and the data is removed."""
        # Arrange
        create_result = data_access_with_cache.create("To Be Deleted", "Delete me", "vector")
        assert isinstance(create_result, Success)
        created_workspace = create_result.unwrap()
        workspace_id = created_workspace.id

        # Act
        deleted = data_access_with_cache.delete(workspace_id)

        # Assert
        assert deleted is True
        assert data_access_with_cache.get_by_id(workspace_id) is None

    def test_get_all_workspaces_returns_all_created_workspaces(
        self, data_access_with_cache: WorkspaceDataAccess
    ):
        """Test that get_all returns all created workspaces."""
        # Arrange
        ws1_result = data_access_with_cache.create("WS 1", "", "vector")
        assert isinstance(ws1_result, Success)
        ws2_result = data_access_with_cache.create("WS 2", "", "graph")
        assert isinstance(ws2_result, Success)

        # Act
        workspaces = data_access_with_cache.get_all()

        # Assert
        # The exact count might vary if other tests also create workspaces and don't clean up
        # We assert that our created workspaces are present.
        assert any(ws.name == "WS 1" for ws in workspaces)
        assert any(ws.name == "WS 2" for ws in workspaces)
        assert len(workspaces) >= 2
