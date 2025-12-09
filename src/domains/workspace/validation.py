"""Workspace input validation.

With Pydantic, most validation is handled automatically by the request models.
This layer now focuses on business logic validation and applying defaults.
"""

from pydantic import ValidationError as PydanticValidationError
from returns.result import Failure, Result, Success

from src.domains.workspace.dtos import (
    CreateWorkspaceRequest,
    DeleteWorkspaceRequest,
    SelectWorkspaceRequest,
    ShowWorkspaceRequest,
    UpdateWorkspaceRequest,
)
from src.infrastructure.types import ValidationError


def validate_create_workspace(
    request: CreateWorkspaceRequest,
    default_rag_type: str = "vector",
) -> Result[CreateWorkspaceRequest, ValidationError]:
    """Validate workspace creation input using Pydantic.

    Args:
        request: Request DTO (already validated by Pydantic)
        default_rag_type: Default RAG type if not specified

    Returns:
        Result with validated request (with defaults applied) or ValidationError
    """
    try:
        # Apply default rag_type if not provided (business logic)
        if request.rag_type is None:
            # Create new request with default applied, preserving RAG config parameters
            request = CreateWorkspaceRequest(
                name=request.name,
                description=request.description,
                rag_type=default_rag_type,
                # Vector RAG config
                chunking_algorithm=request.chunking_algorithm,
                chunk_size=request.chunk_size,
                chunk_overlap=request.chunk_overlap,
                embedding_algorithm=request.embedding_algorithm,
                top_k=request.top_k,
                rerank_algorithm=request.rerank_algorithm,
                # Graph RAG config
                entity_extraction_algorithm=request.entity_extraction_algorithm,
                relationship_extraction_algorithm=request.relationship_extraction_algorithm,
                clustering_algorithm=request.clustering_algorithm,
            )

        # Pydantic has already validated structure and types
        return Success(request)

    except PydanticValidationError as e:
        # Convert Pydantic errors to our ValidationError type
        errors = e.errors()
        first_error = errors[0]
        field = ".".join(str(loc) for loc in first_error["loc"])
        message = first_error["msg"]
        return Failure(ValidationError(message, field=field))


def validate_update_workspace(
    request: UpdateWorkspaceRequest,
) -> Result[UpdateWorkspaceRequest, ValidationError]:
    """Validate workspace update input using Pydantic.

    Args:
        request: Request DTO (already validated by Pydantic)

    Returns:
        Result with validated request or ValidationError
    """
    try:
        # Check business logic: at least one field must be provided for update
        if request.name is None and request.description is None:
            return Failure(
                ValidationError(
                    "At least one field (name or description) must be provided for update",
                    field="general",
                )
            )

        # Pydantic has already validated structure and types
        return Success(request)

    except PydanticValidationError as e:
        # Convert Pydantic errors to our ValidationError type
        errors = e.errors()
        first_error = errors[0]
        field = ".".join(str(loc) for loc in first_error["loc"])
        message = first_error["msg"]
        return Failure(ValidationError(message, field=field))


def validate_delete_workspace(
    request: DeleteWorkspaceRequest,
) -> Result[DeleteWorkspaceRequest, ValidationError]:
    """Validate workspace deletion input.

    Args:
        request: Request DTO (already validated by Pydantic)

    Returns:
        Result with DeleteWorkspaceRequest or ValidationError
    """
    # Pydantic Field(gt=0) already validates workspace_id > 0
    return Success(request)


def validate_show_workspace(
    request: ShowWorkspaceRequest,
) -> Result[ShowWorkspaceRequest, ValidationError]:
    """Validate show workspace input.

    Args:
        request: Request DTO (already validated by Pydantic)

    Returns:
        Result with ShowWorkspaceRequest or ValidationError
    """
    # Pydantic Field(gt=0) already validates workspace_id > 0
    return Success(request)


def validate_select_workspace(
    request: SelectWorkspaceRequest,
) -> Result[SelectWorkspaceRequest, ValidationError]:
    """Validate select workspace input.

    Args:
        request: Request DTO (already validated by Pydantic)

    Returns:
        Result with SelectWorkspaceRequest or ValidationError
    """
    # Pydantic Field(gt=0) already validates workspace_id > 0
    return Success(request)
