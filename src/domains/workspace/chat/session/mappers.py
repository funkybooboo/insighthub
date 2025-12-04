"""Mappers for chat session models and DTOs."""

from src.domains.workspace.chat.session.dtos import SessionResponse
from src.domains.workspace.chat.session.models import ChatSession
from src.infrastructure.mappers import map_timestamps


class SessionMapper:
    """Handles conversions between ChatSession models and Response DTOs."""

    @staticmethod
    def to_response(session: ChatSession) -> SessionResponse:
        """
        Convert a ChatSession model to SessionResponse DTO.

        Args:
            session: ChatSession model instance

        Returns:
            SessionResponse DTO
        """
        created_at_str, updated_at_str = map_timestamps(session.created_at, session.updated_at)
        return SessionResponse(
            id=session.id,
            workspace_id=session.workspace_id,
            title=session.title,
            rag_type=session.rag_type,
            created_at=created_at_str,
            updated_at=updated_at_str,
        )
