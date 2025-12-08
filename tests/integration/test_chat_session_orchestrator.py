"""Integration tests for the SessionOrchestrator component."""

import pytest
from returns.result import Failure, Success

from src.domains.state.data_access import StateDataAccess
from src.domains.state.repositories import StateRepository
from src.domains.workspace.chat.session.data_access import ChatSessionDataAccess
from src.domains.workspace.chat.session.dtos import (
    CreateSessionRequest,
    DeleteSessionRequest,
    ListSessionsRequest,
    SelectSessionRequest,
)
from src.domains.workspace.chat.session.orchestrator import SessionOrchestrator
from src.domains.workspace.chat.session.repositories import ChatSessionRepository
from src.domains.workspace.chat.session.service import ChatSessionService
from src.domains.workspace.data_access import WorkspaceDataAccess
from src.domains.workspace.repositories import WorkspaceRepository
from src.infrastructure.cache.redis_cache import RedisCache
from src.infrastructure.sql_database import SqlDatabase
from src.infrastructure.types import NotFoundError, ValidationError


@pytest.mark.integration
class TestSessionOrchestratorIntegration:
    """Integration tests for the SessionOrchestrator component."""

    @pytest.fixture(scope="function")
    def workspace_repository(self, db_session: SqlDatabase) -> WorkspaceRepository:
        """Fixture to create a WorkspaceRepository."""
        return WorkspaceRepository(db_session)

    @pytest.fixture(scope="function")
    def workspace_data_access(
        self, workspace_repository: WorkspaceRepository, cache_instance: RedisCache
    ) -> WorkspaceDataAccess:
        """Fixture for WorkspaceDataAccess with a Redis cache."""
        return WorkspaceDataAccess(repository=workspace_repository, cache=cache_instance)

    @pytest.fixture(scope="function")
    def chat_session_repository(self, db_session: SqlDatabase) -> ChatSessionRepository:
        """Fixture to create a ChatSessionRepository."""
        return ChatSessionRepository(db_session)

    @pytest.fixture(scope="function")
    def chat_session_data_access(
        self, chat_session_repository: ChatSessionRepository, cache_instance: RedisCache
    ) -> ChatSessionDataAccess:
        """Fixture to create a ChatSessionDataAccess."""
        return ChatSessionDataAccess(repository=chat_session_repository, cache=cache_instance)

    @pytest.fixture(scope="function")
    def state_repository(self, db_session: SqlDatabase) -> StateRepository:
        """Fixture to create a StateRepository."""
        return StateRepository(db_session)

    @pytest.fixture(scope="function")
    def state_data_access(
        self, state_repository: StateRepository, cache_instance: RedisCache
    ) -> StateDataAccess:
        """Fixture to create a StateDataAccess."""
        return StateDataAccess(repository=state_repository, cache=cache_instance)

    @pytest.fixture(scope="function")
    def chat_session_service(
        self,
        chat_session_data_access: ChatSessionDataAccess,
    ) -> ChatSessionService:
        """Fixture to create a ChatSessionService."""
        return ChatSessionService(
            data_access=chat_session_data_access,
        )

    @pytest.fixture(scope="function")
    def session_orchestrator(self, chat_session_service: ChatSessionService) -> SessionOrchestrator:
        """Fixture to create a SessionOrchestrator."""
        return SessionOrchestrator(service=chat_session_service)

    def test_create_session_success(
        self, session_orchestrator: SessionOrchestrator, setup_workspace
    ):
        """Test successful creation of a chat session."""
        # Arrange
        workspace_id = setup_workspace.id
        request = CreateSessionRequest(
            workspace_id=workspace_id, title="New Session", rag_type="vector"
        )

        # Act
        result = session_orchestrator.create_session(request)

        # Assert
        assert isinstance(result, Success)
        session_response = result.unwrap()
        assert session_response.title == "New Session"
        assert session_response.workspace_id == workspace_id
        assert session_response.rag_type == "vector"
        assert session_orchestrator.service.get_session(session_response.id) is not None

    def test_create_session_validation_failure(
        self, session_orchestrator: SessionOrchestrator, setup_workspace
    ):
        """Test creation of a chat session with invalid data."""
        # Arrange
        workspace_id = setup_workspace.id  # Use a valid workspace_id
        request = CreateSessionRequest(
            workspace_id=workspace_id, title="", rag_type="vector"
        )  # Empty title

        # Act
        result = session_orchestrator.create_session(request)

        # Assert
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, ValidationError)
        assert "title" in error.message

    def test_list_sessions_success(
        self, session_orchestrator: SessionOrchestrator, setup_workspace
    ):
        """Test successful listing of chat sessions for a workspace."""
        # Arrange
        workspace_id = setup_workspace.id
        session1_request = CreateSessionRequest(
            workspace_id=workspace_id, title="Session 1", rag_type="vector"
        )
        session2_request = CreateSessionRequest(
            workspace_id=workspace_id, title="Session 2", rag_type="vector"
        )

        session_orchestrator.create_session(session1_request)
        session_orchestrator.create_session(session2_request)

        list_request = ListSessionsRequest(workspace_id=workspace_id, skip=0, limit=10)

        # Act
        result = session_orchestrator.list_sessions(list_request)

        # Assert
        assert isinstance(result, Success)
        paginated_response = result.unwrap()
        assert paginated_response.total_count == 2
        assert len(paginated_response.items) == 2
        assert any(s.title == "Session 1" for s in paginated_response.items)
        assert any(s.title == "Session 2" for s in paginated_response.items)

    def test_list_sessions_validation_failure(self, session_orchestrator: SessionOrchestrator):
        """Test listing chat sessions with invalid data."""
        # Arrange
        request = ListSessionsRequest(workspace_id=1, skip=-1, limit=10)  # Invalid skip

        # Act
        result = session_orchestrator.list_sessions(request)

        # Assert
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, ValidationError)
        assert "Skip" in error.message  # Corrected assertion

    def test_select_session_success(
        self,
        session_orchestrator: SessionOrchestrator,
        setup_workspace,
        state_repository: StateRepository,
    ):
        """Test successful selection of a chat session."""
        # Arrange
        workspace_id = setup_workspace.id
        create_request = CreateSessionRequest(
            workspace_id=workspace_id, title="Selectable Session", rag_type="vector"
        )
        create_result = session_orchestrator.create_session(create_request)
        created_session_id = create_result.unwrap().id

        select_request = SelectSessionRequest(session_id=created_session_id)

        # Act
        result = session_orchestrator.select_session(select_request, state_repo=state_repository)

        # Assert
        assert isinstance(result, Success)
        session_response = result.unwrap()
        assert session_response.id == created_session_id
        state = state_repository.get()
        assert state is not None
        assert state.current_session_id == created_session_id

    def test_select_session_not_found(
        self, session_orchestrator: SessionOrchestrator, state_repository: StateRepository
    ):
        """Test selection of a non-existent chat session."""
        # Arrange
        select_request = SelectSessionRequest(session_id=999)  # Non-existent session

        # Act
        result = session_orchestrator.select_session(select_request, state_repo=state_repository)

        # Assert
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, NotFoundError)
        assert error.resource == "session"
        assert error.id == 999

    def test_delete_session_success(
        self, session_orchestrator: SessionOrchestrator, setup_workspace
    ):
        """Test successful deletion of a chat session."""
        # Arrange
        workspace_id = setup_workspace.id
        create_request = CreateSessionRequest(
            workspace_id=workspace_id, title="Deletable Session", rag_type="vector"
        )
        create_result = session_orchestrator.create_session(create_request)
        created_session_id = create_result.unwrap().id

        delete_request = DeleteSessionRequest(session_id=created_session_id)

        # Act
        result = session_orchestrator.delete_session(delete_request)

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() is True
        assert session_orchestrator.service.get_session(created_session_id) is None

    def test_delete_session_not_found(self, session_orchestrator: SessionOrchestrator):
        """Test deletion of a non-existent chat session."""
        # Arrange
        delete_request = DeleteSessionRequest(session_id=999)  # Non-existent session

        # Act
        result = session_orchestrator.delete_session(delete_request)

        # Assert
        assert isinstance(result, Success)
        assert result.unwrap() is False
