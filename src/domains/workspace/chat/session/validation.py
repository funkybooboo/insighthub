"""Chat session input validation."""

from returns.result import Failure, Result, Success

from src.domains.workspace.chat.session.dtos import (
    CreateSessionRequest,
    DeleteSessionRequest,
    ListSessionsRequest,
    SelectSessionRequest,
    UpdateSessionRequest,
)
from src.infrastructure.rag.options import get_valid_rag_types, is_valid_rag_type
from src.infrastructure.types import ValidationError
from src.infrastructure.validation import validate_pagination, validate_positive_id


def validate_create_session(
    request: CreateSessionRequest,
) -> Result[CreateSessionRequest, ValidationError]:
    """Validate session creation input.

    Returns:
        Result with cleaned CreateSessionRequest or ValidationError
    """
    # Use infrastructure utility for ID validation
    workspace_id_result = validate_positive_id(request.workspace_id, "workspace_id")
    if isinstance(workspace_id_result, Failure):
        return Failure(workspace_id_result.failure())

    # Validate title if provided
    title = None
    if request.title:
        title = request.title.strip()
        if title and len(title) > 255:
            return Failure(
                ValidationError("Session title too long (max 255 characters)", field="title")
            )
        if not title:
            title = None

    # Validate rag_type if provided
    if request.rag_type and not is_valid_rag_type(request.rag_type):
        valid_types = get_valid_rag_types()
        return Failure(
            ValidationError(
                f"Invalid rag_type. Must be one of: {', '.join(valid_types)}",
                field="rag_type",
            )
        )

    return Success(
        CreateSessionRequest(
            workspace_id=request.workspace_id,
            title=title,
            rag_type=request.rag_type,
        )
    )


def validate_update_session(
    request: UpdateSessionRequest,
) -> Result[UpdateSessionRequest, ValidationError]:
    """Validate session update input.

    Returns:
        Result with cleaned UpdateSessionRequest or ValidationError
    """
    # Use infrastructure utility for ID validation
    session_id_result = validate_positive_id(request.session_id, "session_id")
    if isinstance(session_id_result, Failure):
        return Failure(session_id_result.failure())

    # Validate title if provided
    title = None
    if request.title is not None:
        title = request.title.strip()
        if title and len(title) > 255:
            return Failure(
                ValidationError("Session title too long (max 255 characters)", field="title")
            )
        if not title:
            title = None

    if title is None:
        return Failure(
            ValidationError("At least one field must be provided for update", field="general")
        )

    return Success(UpdateSessionRequest(session_id=request.session_id, title=title))


def validate_delete_session(
    request: DeleteSessionRequest,
) -> Result[DeleteSessionRequest, ValidationError]:
    """Validate session deletion input.

    Returns:
        Result with DeleteSessionRequest or ValidationError
    """
    # Use infrastructure utility for ID validation
    session_id_result = validate_positive_id(request.session_id, "session_id")
    if isinstance(session_id_result, Failure):
        return Failure(session_id_result.failure())

    return Success(request)


def validate_select_session(
    request: SelectSessionRequest,
) -> Result[SelectSessionRequest, ValidationError]:
    """Validate session selection input.

    Returns:
        Result with SelectSessionRequest or ValidationError
    """
    # Use infrastructure utility for ID validation
    session_id_result = validate_positive_id(request.session_id, "session_id")
    if isinstance(session_id_result, Failure):
        return Failure(session_id_result.failure())

    return Success(request)


def validate_list_sessions(
    request: ListSessionsRequest,
) -> Result[ListSessionsRequest, ValidationError]:
    """Validate list sessions input.

    Returns:
        Result with ListSessionsRequest or ValidationError
    """
    # Use infrastructure utility for ID validation
    workspace_id_result = validate_positive_id(request.workspace_id, "workspace_id")
    if isinstance(workspace_id_result, Failure):
        return Failure(workspace_id_result.failure())

    # Use infrastructure utility for pagination validation
    pagination_result = validate_pagination(request.skip, request.limit)
    if isinstance(pagination_result, Failure):
        return Failure(pagination_result.failure())

    return Success(request)
