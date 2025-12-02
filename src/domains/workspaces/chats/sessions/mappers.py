"""Mappers for chats session models and DTOs."""

from src.infrastructure.models import ChatSession

from .dtos import SessionResponse


class SessionMapper:
    """Handles conversions between ChatSession models and DTOs."""

    @staticmethod
    def session_to_dto(session: ChatSession) -> SessionResponse:
        """
        Convert a ChatSession model to SessionResponse DTO (single-user system).

        Args:
            session: ChatSession model instance

        Returns:
            SessionResponse DTO
        """
        return SessionResponse(
            id=session.id,
            workspace_id=session.workspace_id,
            title=session.title,
            rag_type=session.rag_type,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
