"""State domain service."""

from typing import Optional

from src.domains.state.data_access import StateDataAccess
from src.domains.state.models import State
from src.domains.workspace.chat.session.data_access import ChatSessionDataAccess
from src.domains.workspace.data_access import WorkspaceDataAccess
from src.infrastructure.logger import create_logger

logger = create_logger(__name__)


class StateService:
    """Service for state-related business logic."""

    def __init__(
        self,
        state_data_access: StateDataAccess,
        workspace_data_access: WorkspaceDataAccess,
        session_data_access: ChatSessionDataAccess,
    ):
        """Initialize state service with dependencies."""
        self.state_data_access = state_data_access
        self.workspace_data_access = workspace_data_access
        self.session_data_access = session_data_access

    def get_current_state(
        self,
    ) -> tuple[Optional[int], Optional[str], Optional[int], Optional[str]]:
        """Get current state with resolved names.

        Returns:
            Tuple of (workspace_id, workspace_name, session_id, session_title)
        """
        state = self.state_data_access.get()

        if not state:
            return (None, None, None, None)

        # Resolve workspace name
        workspace_name = None
        if state.current_workspace_id:
            workspace = self.workspace_data_access.get_by_id(state.current_workspace_id)
            if workspace:
                workspace_name = workspace.name

        # Resolve session title
        session_title = None
        if state.current_session_id:
            session = self.session_data_access.get_by_id(state.current_session_id)
            if session:
                session_title = session.title

        return (
            state.current_workspace_id,
            workspace_name,
            state.current_session_id,
            session_title,
        )
