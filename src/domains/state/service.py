"""State domain service."""

from typing import Optional

from src.domains.state.models import State
from src.domains.state.repositories import StateRepository
from src.domains.workspace.chat.session.repositories import ChatSessionRepository
from src.domains.workspace.repositories import WorkspaceRepository
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


class StateService:
    """Service for state-related business logic."""

    def __init__(
        self,
        state_repository: StateRepository,
        workspace_repository: WorkspaceRepository,
        session_repository: ChatSessionRepository,
    ):
        """Initialize state service with dependencies."""
        self.state_repository = state_repository
        self.workspace_repository = workspace_repository
        self.session_repository = session_repository

    def get_current_state(
        self,
    ) -> tuple[Optional[int], Optional[str], Optional[int], Optional[str]]:
        """Get current state with resolved names.

        Returns:
            Tuple of (workspace_id, workspace_name, session_id, session_title)
        """
        state = self.state_repository.get()

        if not state:
            return (None, None, None, None)

        # Resolve workspace name
        workspace_name = None
        if state.current_workspace_id:
            workspace = self.workspace_repository.get_by_id(state.current_workspace_id)
            if workspace:
                workspace_name = workspace.name

        # Resolve session title
        session_title = None
        if state.current_session_id:
            session = self.session_repository.get_by_id(state.current_session_id)
            if session:
                session_title = session.title

        return (
            state.current_workspace_id,
            workspace_name,
            state.current_session_id,
            session_title,
        )
