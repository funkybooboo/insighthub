"""Chat message domain orchestrator.

Eliminates duplication between commands.py and routes.py by providing
a single interface for: Request DTO → Validation → Service → Response DTO
"""

from typing import List, Tuple

from returns.result import Failure, Result, Success

from src.domains.workspace.chat.message.dtos import (
    ListMessagesRequest,
    MessageResponse,
    SendMessageRequest,
)
from src.domains.workspace.chat.message.mappers import MessageMapper
from src.domains.workspace.chat.message.service import ChatMessageService
from src.domains.workspace.chat.message.validation import (
    validate_list_messages,
    validate_send_message,
)
from src.infrastructure.types import ValidationError


class MessageOrchestrator:
    """Orchestrates message operations: validation → service → response."""

    def __init__(self, service: ChatMessageService):
        """Initialize orchestrator with service."""
        self.service = service

    def send_message(
        self,
        request: SendMessageRequest,
    ) -> Result[None, ValidationError]:
        """Orchestrate sending a message.

        Args:
            request: Send message request DTO

        Returns:
            Result with None or error
        """
        # Validate
        validation_result = validate_send_message(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call service
        service_result = self.service.send_message_with_rag(
            session_id=validated_request.session_id,
            message_content=validated_request.content,
            stream_callback=validated_request.stream_callback,
        )

        if isinstance(service_result, Failure):
            return Failure(service_result.failure())

        return Success(None)

    def list_messages(
        self,
        request: ListMessagesRequest,
    ) -> Result[Tuple[List[MessageResponse], int], ValidationError]:
        """Orchestrate list messages.

        Args:
            request: List messages request DTO

        Returns:
            Result with tuple of (list of MessageResponse, total count) or error
        """
        # Validate
        validation_result = validate_list_messages(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call service
        messages, total = self.service.get_session_messages(
            session_id=validated_request.session_id,
            skip=validated_request.skip,
            limit=validated_request.limit,
        )

        # Map to responses
        responses = [MessageMapper.to_response(message) for message in messages]
        return Success((responses, total))
