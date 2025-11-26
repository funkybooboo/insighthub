"""Mappers for chats message models and DTOs."""

from src.infrastructure.models import ChatMessage

from .dtos import MessageResponse


class MessageMapper:
    """Handles conversions between ChatMessage models and DTOs."""

    @staticmethod
    def message_to_dto(message: ChatMessage) -> MessageResponse:
        """
        Convert a ChatMessage model to MessageResponse DTO.

        Args:
            message: ChatMessage model instance

        Returns:
            MessageResponse DTO
        """
        return MessageResponse(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            extra_metadata=message.extra_metadata,
            created_at=message.created_at,
            updated_at=message.updated_at,
        )
