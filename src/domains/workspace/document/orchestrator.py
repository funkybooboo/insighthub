"""Document domain orchestrator.

Eliminates duplication between commands.py and routes.py by providing
a single interface for: Request DTO → Validation → Service → Response DTO
"""

from typing import List

from returns.result import Failure, Result, Success

from src.domains.workspace.document.dtos import (
    DeleteDocumentRequest,
    DocumentResponse,
    ShowDocumentRequest,
    UploadDocumentRequest,
)
from src.domains.workspace.document.mappers import DocumentMapper
from src.domains.workspace.document.service import DocumentService
from src.domains.workspace.document.validation import (
    validate_delete_document,
    validate_show_document,
    validate_upload_document,
)
from src.infrastructure.types import (
    DatabaseError,
    NotFoundError,
    StorageError,
    ValidationError,
    WorkflowError,
)


class DocumentOrchestrator:
    """Orchestrates document operations: validation → service → response."""

    def __init__(self, service: DocumentService):
        """Initialize orchestrator with service."""
        self.service = service

    def upload_document(
        self,
        request: UploadDocumentRequest,
    ) -> Result[
        DocumentResponse,
        ValidationError | NotFoundError | StorageError | WorkflowError | DatabaseError,
    ]:
        """Orchestrate document upload.

        Args:
            request: Upload document request DTO

        Returns:
            Result with DocumentResponse or error
        """
        # Validate
        validation_result = validate_upload_document(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Read file content
        with open(validated_request.file_path, "rb") as f:
            file_content = f.read()

        # Call service
        service_result = self.service.upload_and_process_document(
            workspace_id=validated_request.workspace_id,
            filename=validated_request.filename,
            file_content=file_content,
        )

        if isinstance(service_result, Failure):
            return Failure(service_result.failure())

        # Map to response
        document = service_result.unwrap()
        return Success(DocumentMapper.to_response(document))

    def show_document(
        self,
        request: ShowDocumentRequest,
    ) -> Result[DocumentResponse, ValidationError | NotFoundError]:
        """Orchestrate show document.

        Args:
            request: Show document request DTO

        Returns:
            Result with DocumentResponse or error
        """
        # Validate
        validation_result = validate_show_document(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call service
        document = self.service.get_document_by_id(validated_request.document_id)
        if not document:
            return Failure(NotFoundError("document", validated_request.document_id))

        # Verify document belongs to workspace
        if document.workspace_id != validated_request.workspace_id:
            return Failure(
                ValidationError(
                    f"Document {validated_request.document_id} not in workspace {validated_request.workspace_id}",
                    field="document_id",
                )
            )

        # Map to response
        return Success(DocumentMapper.to_response(document))

    def delete_document(
        self,
        request: DeleteDocumentRequest,
    ) -> Result[bool, ValidationError]:
        """Orchestrate document deletion.

        Args:
            request: Delete document request DTO

        Returns:
            Result with boolean success or error
        """
        # Validate
        validation_result = validate_delete_document(request)
        if isinstance(validation_result, Failure):
            return Failure(validation_result.failure())

        validated_request = validation_result.unwrap()

        # Call service
        deleted = self.service.remove_document(validated_request.document_id)
        return Success(deleted)

    def list_documents(
        self,
        workspace_id: int,
    ) -> Result[List[DocumentResponse], None]:
        """List documents in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Result with list of DocumentResponse
        """
        # Call service
        documents = self.service.list_documents_by_workspace(workspace_id)

        # Map to responses
        responses = [DocumentMapper.to_response(doc) for doc in documents]
        return Success(responses)
