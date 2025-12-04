"""Mappers for chat message models and DTOs."""

from src.domains.workspace.chat.message.dtos import MessageResponse
from src.domains.workspace.chat.message.models import ChatMessage
from src.infrastructure.mappers import map_timestamps


class MessageMapper:
    """Handles conversions between ChatMessage models and Response DTOs."""

    @staticmethod
    def to_response(message: ChatMessage) -> MessageResponse:
        """
        Convert a ChatMessage model to MessageResponse DTO.

        Args:
            message: ChatMessage model instance

        Returns:
            MessageResponse DTO
        """
        created_at_str, updated_at_str = map_timestamps(message.created_at, message.updated_at)
        return MessageResponse(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            extra_metadata=message.extra_metadata,
            created_at=created_at_str,
            updated_at=updated_at_str,
        )
