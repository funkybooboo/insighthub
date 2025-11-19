"""Mappers for converting between chat models and DTOs."""

import json

from shared.models import ChatMessage, ChatSession

from .dtos import MessageResponse, SessionResponse


class ChatMapper:
    """Handles conversions between chat domain models and DTOs."""

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
            title=session.title or "Untitled Session",
            rag_type=session.rag_type,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    @staticmethod
    def sessions_to_dtos(sessions: list[ChatSession]) -> list[SessionResponse]:
        """
        Convert a list of ChatSession models to SessionResponse DTOs.

        Args:
            sessions: List of ChatSession model instances

        Returns:
            List of SessionResponse DTOs
        """
        return [ChatMapper.session_to_dto(session) for session in sessions]

    @staticmethod
    def message_to_dto(message: ChatMessage) -> MessageResponse:
        """
        Convert a ChatMessage model to MessageResponse DTO.

        Args:
            message: ChatMessage model instance

        Returns:
            MessageResponse DTO
        """
        metadata = json.loads(message.extra_metadata) if message.extra_metadata else None
        return MessageResponse(
            id=message.id,
            role=message.role,
            content=message.content,
            metadata=metadata,
            created_at=message.created_at,
        )

    @staticmethod
    def messages_to_dtos(messages: list[ChatMessage]) -> list[MessageResponse]:
        """
        Convert a list of ChatMessage models to MessageResponse DTOs.

        Args:
            messages: List of ChatMessage model instances

        Returns:
            List of MessageResponse DTOs
        """
        return [ChatMapper.message_to_dto(message) for message in messages]
