"""Factory for creating ChatService instances."""

from enum import Enum

from sqlalchemy.orm import Session

from src import config
from src.repositories import (
    create_chat_message_repository,
    create_chat_session_repository,
)

from .chat_service import ChatService
from .default_chat_service import DefaultChatService


class ChatServiceType(Enum):
    """Enum for chat service implementation types."""

    DEFAULT = "default"


def create_chat_service(db: Session, service_type: ChatServiceType | None = None) -> ChatService:
    """
    Create a ChatService instance with dependencies.

    Args:
        db: Database session
        service_type: Type of chat service implementation to use.
                     If None, reads from config.CHAT_SERVICE_TYPE.

    Returns:
        ChatService: Service instance with injected dependencies

    Raises:
        ValueError: If service_type is not supported
    """
    if service_type is None:
        service_type = ChatServiceType(config.CHAT_SERVICE_TYPE)

    session_repository = create_chat_session_repository(db)
    message_repository = create_chat_message_repository(db)

    if service_type == ChatServiceType.DEFAULT:
        return DefaultChatService(
            session_repository=session_repository, message_repository=message_repository
        )
    else:
        raise ValueError(f"Unsupported chat service type: {service_type}")
