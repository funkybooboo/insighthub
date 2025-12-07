"""Chat session domain orchestrator.

Eliminates duplication between commands.py and routes.py by providing
a single interface for: Request DTO → Validation → Service → Response DTO
"""

from typing import Any

from returns.result import Failure, Result, Success

from src.domains.workspace.chat.session.dtos import (
    CreateSessionRequest,
    DeleteSessionRequest,
    ListSessionsRequest,
    SelectSessionRequest,
    SessionResponse,
)
from src.domains.workspace.chat.session.mappers import SessionMapper
from src.domains.workspace.chat.session.service import ChatSessionService
from src.domains.workspace.chat.session.validation import (
    validate_create_session,
    validate_delete_session,
    validate_list_sessions,
    validate_select_session,
)
from src.infrastructure.types import NotFoundError, PaginatedResult, Pagination, ValidationError


class SessionOrchestrator:
    """Orchestrates session operations: validation → service → response."""

    def __init__(self, service: ChatSessionService):
        """Initialize orchestrator with service."""
        self.service = service

    def create_session(
        self,
        request: CreateSessionRequest,
    ) -> Result[SessionResponse, ValidationError]:
        """Orchestrate session creation.

        Args:
            request: Create session request DTO

        Returns:
            Result with SessionResponse or error
        """
        # Validate
        validation_result = validate_create_session(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call service
        if validated_request.rag_type is not None:
            service_result = self.service.create_session(
                title=validated_request.title,
                workspace_id=validated_request.workspace_id,
                rag_type=validated_request.rag_type,
            )
        else:
            service_result = self.service.create_session(
                title=validated_request.title,
                workspace_id=validated_request.workspace_id,
            )

        if isinstance(service_result, Failure):
            return Failure(service_result.failure())

        # Map to response
        session = service_result.unwrap()
        return Success(SessionMapper.to_response(session))

    def list_sessions(
        self,
        request: ListSessionsRequest,
    ) -> Result[PaginatedResult[SessionResponse], ValidationError]:
        """Orchestrate list sessions.

        Args:
            request: List sessions request DTO

        Returns:
            Result with PaginatedResult of SessionResponse or error
        """
        # Validate
        validation_result = validate_list_sessions(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Create pagination
        pagination_result = Pagination.create(
            skip=validated_request.skip, limit=validated_request.limit
        )
        if isinstance(pagination_result, Failure):
            return Failure(ValidationError(pagination_result.failure().message))

        pagination = pagination_result.unwrap()

        # Call service
        result = self.service.list_workspace_sessions(
            workspace_id=validated_request.workspace_id,
            pagination=pagination,
        )

        # Map to responses
        responses = [SessionMapper.to_response(session) for session in result.items]
        return Success(
            PaginatedResult(
                items=responses,
                total_count=result.total_count,
                skip=result.skip,
                limit=result.limit,
            )
        )

    def select_session(
        self,
        request: SelectSessionRequest,
        state_repo: Any,  # StateRepository
    ) -> Result[SessionResponse, ValidationError | NotFoundError]:
        """Orchestrate session selection.

        Args:
            request: Select session request DTO
            state_repo: State repository for setting current session

        Returns:
            Result with SessionResponse or error
        """
        # Validate
        validation_result = validate_select_session(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call service
        session = self.service.get_session(validated_request.session_id)
        if not session:
            return Failure(NotFoundError("session", validated_request.session_id))

        # Update state
        state_repo.set_current_session(session.id)

        # Map to response
        return Success(SessionMapper.to_response(session))

    def delete_session(
        self,
        request: DeleteSessionRequest,
    ) -> Result[bool, ValidationError]:
        """Orchestrate session deletion.

        Args:
            request: Delete session request DTO

        Returns:
            Result with boolean success or error
        """
        # Validate
        validation_result = validate_delete_session(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call service
        deleted = self.service.delete_session(validated_request.session_id)
        return Success(deleted)
