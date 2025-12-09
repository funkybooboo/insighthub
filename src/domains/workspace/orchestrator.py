"""Workspace domain orchestrator.

Eliminates duplication between commands.py and routes.py by providing
a single interface for: Request DTO -> Validation -> Service -> Response DTO
"""

from typing import Any, Optional

from returns.result import Failure, Result, Success

from src.domains.workspace.dtos import (
    CreateWorkspaceRequest,
    DeleteWorkspaceRequest,
    SelectWorkspaceRequest,
    ShowWorkspaceRequest,
    UpdateWorkspaceRequest,
    WorkspaceResponse,
)
from src.domains.workspace.mappers import WorkspaceMapper
from src.domains.workspace.models import GraphRagConfig, VectorRagConfig
from src.domains.workspace.repositories import WorkspaceRepository
from src.domains.workspace.service import WorkspaceService
from src.domains.workspace.validation import (
    validate_create_workspace,
    validate_delete_workspace,
    validate_select_workspace,
    validate_show_workspace,
    validate_update_workspace,
)
from src.infrastructure.types import DatabaseError, NotFoundError, ValidationError, WorkflowError


class WorkspaceOrchestrator:
    """Orchestrates workspace operations: validation -> service -> response."""

    def __init__(self, service: WorkspaceService, repository: WorkspaceRepository):
        """Initialize orchestrator with service and repository."""
        self.service = service
        self.repository = repository

    def list_workspaces(self) -> Result[list[WorkspaceResponse], DatabaseError]:
        """Orchestrate workspace listing.

        Returns:
            Result with list of WorkspaceResponse or error
        """
        # Call service
        workspaces = self.service.list_workspaces()

        # Map to responses
        return Success([WorkspaceMapper.to_response(ws) for ws in workspaces])

    def create_workspace(
        self,
        request: CreateWorkspaceRequest,
        default_rag_type: str = "vector",
    ) -> Result[WorkspaceResponse, ValidationError | WorkflowError | DatabaseError]:
        """Orchestrate workspace creation.

        Args:
            request: Create workspace request DTO
            default_rag_type: Default RAG type if not specified

        Returns:
            Result with WorkspaceResponse or error
        """
        # Validate
        validation_result = validate_create_workspace(request, default_rag_type)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Validation guarantees rag_type is not None
        assert validated_request.rag_type is not None

        # Call service
        service_result = self.service.create_workspace(
            name=validated_request.name,
            description=validated_request.description,
            rag_type=validated_request.rag_type,
        )

        if isinstance(service_result, Failure):
            return Failure(service_result.failure())

        # Map to response
        workspace = service_result.unwrap()
        return Success(WorkspaceMapper.to_response(workspace))

    def show_workspace(
        self,
        request: ShowWorkspaceRequest,
    ) -> Result[WorkspaceResponse, ValidationError | NotFoundError]:
        """Orchestrate show workspace.

        Args:
            request: Show workspace request DTO

        Returns:
            Result with WorkspaceResponse or error
        """
        # Validate
        validation_result = validate_show_workspace(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call service
        workspace = self.service.get_workspace(validated_request.workspace_id)
        if not workspace:
            return Failure(NotFoundError("workspace", validated_request.workspace_id))

        # Map to response
        return Success(WorkspaceMapper.to_response(workspace))

    def update_workspace(
        self,
        request: UpdateWorkspaceRequest,
    ) -> Result[WorkspaceResponse, ValidationError | NotFoundError]:
        """Orchestrate workspace update.

        Args:
            request: Update workspace request DTO

        Returns:
            Result with WorkspaceResponse or error
        """
        # Validate
        validation_result = validate_update_workspace(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call service
        service_result = self.service.update_workspace(
            workspace_id=validated_request.workspace_id,
            name=validated_request.name,
            description=validated_request.description,
        )

        if isinstance(service_result, Failure):
            return Failure(service_result.failure())

        # Map to response
        workspace = service_result.unwrap()
        return Success(WorkspaceMapper.to_response(workspace))

    def delete_workspace(
        self,
        request: DeleteWorkspaceRequest,
    ) -> Result[bool, ValidationError]:
        """Orchestrate workspace deletion.

        Args:
            request: Delete workspace request DTO

        Returns:
            Result with boolean success or error
        """
        # Validate
        validation_result = validate_delete_workspace(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call service
        deleted = self.service.delete_workspace(validated_request.workspace_id)
        return Success(deleted)

    def select_workspace(
        self,
        request: SelectWorkspaceRequest,
        state_repo: Any,  # StateRepository
    ) -> Result[WorkspaceResponse, ValidationError | NotFoundError]:
        """Orchestrate workspace selection.

        Args:
            request: Select workspace request DTO
            state_repo: State repository for setting current workspace

        Returns:
            Result with WorkspaceResponse or error
        """
        # Validate
        validation_result = validate_select_workspace(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call repository
        workspace = self.repository.get_by_id(validated_request.workspace_id)
        if not workspace:
            return Failure(NotFoundError("workspace", validated_request.workspace_id))

        # Update state
        state_repo.set_current_workspace(workspace.id)

        # Map to response
        return Success(WorkspaceMapper.to_response(workspace))

    def get_workspace_rag_config(self, workspace_id: int) -> Result[tuple[Any, Any], NotFoundError]:
        """Get workspace and its RAG configuration.

        Args:
            workspace_id: ID of workspace

        Returns:
            Result with tuple of (Workspace, RAG config) or error
        """
        # Get workspace
        workspace = self.service.get_workspace(workspace_id)
        if not workspace:
            return Failure(NotFoundError("workspace", workspace_id))

        # Get RAG config based on type
        config: Optional[VectorRagConfig | GraphRagConfig]
        if workspace.rag_type == "vector":
            config = self.repository.get_vector_rag_config(workspace.id)
        elif workspace.rag_type == "graph":
            config = self.repository.get_graph_rag_config(workspace.id)
        else:
            config = None

        return Success((workspace, config))

    def get_workspace_model(self, workspace_id: int) -> Result[Any, NotFoundError]:
        """Get workspace model (for CLI input gathering).

        Args:
            workspace_id: ID of workspace

        Returns:
            Result with Workspace model or error
        """
        workspace = self.service.get_workspace(workspace_id)
        if not workspace:
            return Failure(NotFoundError("workspace", workspace_id))
        return Success(workspace)
