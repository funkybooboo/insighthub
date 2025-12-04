"""State domain DTOs."""

from typing import Optional

from pydantic import BaseModel


class StateResponse(BaseModel):
    """Response DTO for state queries."""

    current_workspace_id: Optional[int]
    current_workspace_name: Optional[str]
    current_session_id: Optional[int]
    current_session_title: Optional[str]
