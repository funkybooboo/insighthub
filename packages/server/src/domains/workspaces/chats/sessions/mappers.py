"""Mappers for chats session models and DTOs."""

from .dtos import SessionResponse
from src.infrastructure.models import ChatSession


class SessionMapper:
    """Handles conversions between ChatSession models and DTOs."""

    @staticmethod
    def session_to_dto(session: ChatSession) -> SessionResponse:
        """
        Convert a ChatSession model to SessionResponse DTO.

        Args:
            session: ChatSession model instance

        Returns:
            SessionResponse DTO
        """
        return SessionResponse(
            id=session.id,
            user_id=session.user_id,
            workspace_id=session.workspace_id,
            title=session.title,
            rag_type=session.rag_type,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )