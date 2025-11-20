"""
Behavior tests for StatusService.

These tests verify WHAT the service does (outputs, side effects),
not HOW it does it (implementation details).
"""

import pytest
from unittest.mock import Mock

from shared.services.status_service import StatusService
from shared.types.status import DocumentProcessingStatus, WorkspaceStatus
from shared.types.option import Some, Nothing


class TestStatusServiceBehavior:
    """Test what StatusService does, not how it does it."""

    def test_update_document_status_returns_ok_result_when_document_exists(self):
        """Test: updating existing document returns Ok result with document."""
        # Setup: repository that returns a document wrapped in Option
        repo = Mock()
        mock_doc = Mock()
        mock_doc.id = 1
        mock_doc.user_id = 10
        mock_doc.workspace_id = 20
        mock_doc.filename = "test.pdf"
        repo.update_document_status.return_value = Some(mock_doc)

        service = StatusService(status_repository=repo)

        # Execute
        result = service.update_document_status(1, DocumentProcessingStatus.READY)

        # Verify: returns Ok with the document
        assert result.is_ok()
        doc = result.unwrap()
        assert doc.id == 1

    def test_update_document_status_returns_err_result_when_document_not_found(self):
        """Test: updating non-existent document returns Err result."""
        # Setup: repository returns Nothing (not found)
        repo = Mock()
        repo.update_document_status.return_value = Nothing()

        service = StatusService(status_repository=repo)

        # Execute
        result = service.update_document_status(999, DocumentProcessingStatus.READY)

        # Verify: returns Err with error message
        assert result.is_err()
        assert "not found" in result.error.lower()

    def test_update_document_status_publishes_event_when_publisher_provided(self):
        """Test: service publishes event when publisher is available."""
        # Setup
        repo = Mock()
        mock_doc = Mock()
        mock_doc.id = 1
        mock_doc.user_id = 10
        mock_doc.workspace_id = 20
        mock_doc.filename = "test.pdf"
        repo.update_document_status.return_value = Some(mock_doc)

        publisher = Mock()
        service = StatusService(status_repository=repo, message_publisher=publisher)

        # Execute
        service.update_document_status(1, DocumentProcessingStatus.READY, chunk_count=5)

        # Verify: publisher.publish was called
        assert publisher.publish.called
        # Verify: event has correct routing key
        call_args = publisher.publish.call_args
        assert call_args[1]["routing_key"] == "document.status.updated"

    def test_update_document_status_does_not_publish_when_no_publisher(self):
        """Test: service doesn't crash when no publisher provided."""
        # Setup
        repo = Mock()
        mock_doc = Mock()
        repo.update_document_status.return_value = Some(mock_doc)

        service = StatusService(status_repository=repo, message_publisher=None)

        # Execute
        result = service.update_document_status(1, DocumentProcessingStatus.READY)

        # Verify: still works, returns Ok
        assert result.is_ok()

    def test_update_workspace_status_returns_ok_result_when_workspace_exists(self):
        """Test: updating existing workspace returns Ok result."""
        # Setup
        repo = Mock()
        mock_ws = Mock()
        mock_ws.id = 1
        mock_ws.user_id = 10
        mock_ws.name = "Test Workspace"
        repo.update_workspace_status.return_value = Some(mock_ws)

        service = StatusService(status_repository=repo)

        # Execute
        result = service.update_workspace_status(1, WorkspaceStatus.READY)

        # Verify
        assert result.is_ok()
        ws = result.unwrap()
        assert ws.id == 1

    def test_update_workspace_status_returns_err_when_workspace_not_found(self):
        """Test: updating non-existent workspace returns Err."""
        # Setup
        repo = Mock()
        repo.update_workspace_status.return_value = Nothing()

        service = StatusService(status_repository=repo)

        # Execute
        result = service.update_workspace_status(999, WorkspaceStatus.READY)

        # Verify
        assert result.is_err()
        assert "not found" in result.error.lower()

    def test_update_workspace_status_publishes_event_when_publisher_provided(self):
        """Test: workspace update publishes event when publisher available."""
        # Setup
        repo = Mock()
        mock_ws = Mock()
        mock_ws.id = 1
        mock_ws.user_id = 10
        mock_ws.name = "Test"
        repo.update_workspace_status.return_value = Some(mock_ws)

        publisher = Mock()
        service = StatusService(status_repository=repo, message_publisher=publisher)

        # Execute
        service.update_workspace_status(1, WorkspaceStatus.PROVISIONING)

        # Verify
        assert publisher.publish.called
        call_args = publisher.publish.call_args
        assert call_args[1]["routing_key"] == "workspace.status.updated"

    def test_published_document_event_contains_required_fields(self):
        """Test: published document event has all required fields."""
        # Setup
        repo = Mock()
        mock_doc = Mock()
        mock_doc.id = 1
        mock_doc.user_id = 10
        mock_doc.workspace_id = 20
        mock_doc.filename = "test.pdf"
        repo.update_document_status.return_value = Some(mock_doc)

        publisher = Mock()
        service = StatusService(status_repository=repo, message_publisher=publisher)

        # Execute
        service.update_document_status(
            1, 
            DocumentProcessingStatus.READY, 
            chunk_count=5,
            metadata={"model": "nomic"}
        )

        # Verify event has required fields
        call_args = publisher.publish.call_args
        event_data = call_args[1]["message"]
        
        assert "document_id" in event_data
        assert "user_id" in event_data
        assert "workspace_id" in event_data
        assert "status" in event_data
        assert "filename" in event_data
        assert event_data["chunk_count"] == 5
        assert event_data["metadata"]["model"] == "nomic"

    def test_published_workspace_event_contains_required_fields(self):
        """Test: published workspace event has all required fields."""
        # Setup
        repo = Mock()
        mock_ws = Mock()
        mock_ws.id = 1
        mock_ws.user_id = 10
        mock_ws.name = "Test"
        repo.update_workspace_status.return_value = Some(mock_ws)

        publisher = Mock()
        service = StatusService(status_repository=repo, message_publisher=publisher)

        # Execute
        service.update_workspace_status(
            1, 
            WorkspaceStatus.ERROR, 
            message="Setup failed"
        )

        # Verify event has required fields
        call_args = publisher.publish.call_args
        event_data = call_args[1]["message"]
        
        assert "workspace_id" in event_data
        assert "user_id" in event_data
        assert "status" in event_data
        assert "name" in event_data
        assert event_data["message"] == "Setup failed"
