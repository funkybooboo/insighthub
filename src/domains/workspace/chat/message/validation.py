"""Chat message input validation."""

from returns.result import Failure, Result, Success

from src.domains.workspace.chat.message.dtos import ListMessagesRequest, SendMessageRequest
from src.infrastructure.types import ValidationError
from src.infrastructure.validation import validate_pagination, validate_positive_id


def validate_send_message(
    request: SendMessageRequest,
) -> Result[SendMessageRequest, ValidationError]:
    """Validate send message input.

    Returns:
        Result with cleaned SendMessageRequest or ValidationError
    """
    # Use infrastructure utility for ID validation
    session_id_result = validate_positive_id(request.session_id, "session_id")
    if isinstance(session_id_result, Failure):
        return Failure(session_id_result.failure())

    if not request.content or not request.content.strip():
        return Failure(ValidationError("Message content cannot be empty", field="content"))

    content = request.content.strip()
    if len(content) > 10000:
        return Failure(
            ValidationError("Message content too long (max 10000 characters)", field="content")
        )

    return Success(
        SendMessageRequest(
            session_id=request.session_id,
            content=content,
            stream_callback=request.stream_callback,
        )
    )


def validate_list_messages(
    request: ListMessagesRequest,
) -> Result[ListMessagesRequest, ValidationError]:
    """Validate list messages input.

    Returns:
        Result with ListMessagesRequest or ValidationError
    """
    # Use infrastructure utility for ID validation
    session_id_result = validate_positive_id(request.session_id, "session_id")
    if isinstance(session_id_result, Failure):
        return Failure(session_id_result.failure())

    # Use infrastructure utility for pagination validation
    pagination_result = validate_pagination(request.skip, request.limit)
    if isinstance(pagination_result, Failure):
        return Failure(pagination_result.failure())

    return Success(request)
