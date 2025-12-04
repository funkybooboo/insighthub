"""State domain orchestrator."""

from returns.result import Result, Success

from src.domains.state.dtos import StateResponse
from src.domains.state.service import StateService


class StateOrchestrator:
    """Orchestrates state operations."""

    def __init__(self, service: StateService):
        """Initialize orchestrator with service."""
        self.service = service

    def get_current_state(self) -> Result[StateResponse, None]:
        """Get current application state.

        Returns:
            Result with StateResponse
        """
        workspace_id, workspace_name, session_id, session_title = self.service.get_current_state()

        response = StateResponse(
            current_workspace_id=workspace_id,
            current_workspace_name=workspace_name,
            current_session_id=session_id,
            current_session_title=session_title,
        )

        return Success(response)
