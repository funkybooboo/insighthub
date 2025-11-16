"""Tests for CLI document commands."""

import argparse
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.domains.documents import commands


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock AppContext."""
    context = Mock()
    context.user_service = Mock()
    context.document_service = Mock()
    return cast(MagicMock, context)


@pytest.fixture
def mock_user() -> Mock:
    """Create a mock user."""
    user = Mock()
    user.id = 1
    user.username = "testuser"
    return user


class TestUploadDocument:
    """Tests for upload_document function."""

    def test_upload_document_success(self, mock_context: MagicMock, mock_user: Mock, tmp_path: Path) -> None:
        """Test successful document upload."""
        # Create a temporary PDF file
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")

        # Mock services
        mock_context.user_service.get_or_create_default_user.return_value = mock_user

        mock_result = Mock()
        mock_result.document = Mock(id=1, filename="test.pdf", file_size=100)
        mock_result.text_length = 50
        mock_result.is_duplicate = False
        mock_context.document_service.process_document_upload.return_value = mock_result

        # Execute
        result = commands.upload_document(mock_context, test_file)

        # Verify
        assert result["id"] == 1
        assert result["filename"] == "test.pdf"
        assert result["file_size"] == 100
        assert result["text_length"] == 50
        assert result["status"] == "uploaded"
        mock_context.document_service.process_document_upload.assert_called_once()

    def test_upload_document_duplicate(self, mock_context: MagicMock, mock_user: Mock, tmp_path: Path) -> None:
        """Test uploading a duplicate document."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")

        mock_context.user_service.get_or_create_default_user.return_value = mock_user

        mock_result = Mock()
        mock_result.document = Mock(id=1, filename="test.pdf", file_size=100)
        mock_result.text_length = 50
        mock_result.is_duplicate = True
        mock_context.document_service.process_document_upload.return_value = mock_result

        result = commands.upload_document(mock_context, test_file)

        assert result["status"] == "already_exists"

    def test_upload_document_file_not_found(self, mock_context: MagicMock) -> None:
        """Test upload with non-existent file."""
        non_existent_file = Path("/fake/path/test.pdf")

        with pytest.raises(FileNotFoundError, match="File not found"):
            commands.upload_document(mock_context, non_existent_file)

    def test_upload_document_unsupported_file_type(self, mock_context: MagicMock, tmp_path: Path) -> None:
        """Test upload with unsupported file type."""
        test_file = tmp_path / "test.exe"
        test_file.write_bytes(b"fake executable")

        with pytest.raises(ValueError, match="Unsupported file type"):
            commands.upload_document(mock_context, test_file)

    def test_upload_document_accepts_txt_files(self, mock_context: MagicMock, mock_user: Mock, tmp_path: Path) -> None:
        """Test that TXT files are accepted."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        mock_context.user_service.get_or_create_default_user.return_value = mock_user

        mock_result = Mock()
        mock_result.document = Mock(id=1, filename="test.txt", file_size=12)
        mock_result.text_length = 12
        mock_result.is_duplicate = False
        mock_context.document_service.process_document_upload.return_value = mock_result

        result = commands.upload_document(mock_context, test_file)

        assert result["filename"] == "test.txt"


class TestListDocuments:
    """Tests for list_documents function."""

    def test_list_documents_success(self, mock_context: MagicMock, mock_user: Mock) -> None:
        """Test successful document listing."""
        mock_context.user_service.get_or_create_default_user.return_value = mock_user

        mock_doc1 = Mock()
        mock_doc1.id = 1
        mock_doc1.filename = "doc1.pdf"
        mock_doc1.file_size = 100
        mock_doc1.mime_type = "application/pdf"
        mock_doc1.chunk_count = 5
        mock_doc1.created_at.isoformat.return_value = "2024-01-01T00:00:00"

        mock_doc2 = Mock()
        mock_doc2.id = 2
        mock_doc2.filename = "doc2.txt"
        mock_doc2.file_size = 50
        mock_doc2.mime_type = "text/plain"
        mock_doc2.chunk_count = 2
        mock_doc2.created_at.isoformat.return_value = "2024-01-02T00:00:00"

        mock_context.document_service.list_user_documents.return_value = [mock_doc1, mock_doc2]

        result = commands.list_documents(mock_context)

        assert result["count"] == 2
        documents = result["documents"]
        assert isinstance(documents, list)
        assert len(documents) == 2
        assert documents[0]["id"] == 1
        assert documents[0]["filename"] == "doc1.pdf"
        assert documents[1]["id"] == 2
        assert documents[1]["filename"] == "doc2.txt"

    def test_list_documents_empty(self, mock_context: MagicMock, mock_user: Mock) -> None:
        """Test listing when no documents exist."""
        mock_context.user_service.get_or_create_default_user.return_value = mock_user
        mock_context.document_service.list_user_documents.return_value = []

        result = commands.list_documents(mock_context)

        assert result["count"] == 0
        assert result["documents"] == []


class TestDeleteDocument:
    """Tests for delete_document function."""

    def test_delete_document_success(self, mock_context: MagicMock) -> None:
        """Test successful document deletion."""
        mock_doc = Mock()
        mock_doc.id = 1
        mock_doc.filename = "test.pdf"

        mock_context.document_service.get_document_by_id.return_value = mock_doc

        result = commands.delete_document(mock_context, 1)

        assert "deleted successfully" in result["message"]
        mock_context.document_service.delete_document.assert_called_once_with(1, delete_from_storage=True)

    def test_delete_document_not_found(self, mock_context: MagicMock) -> None:
        """Test deleting non-existent document."""
        mock_context.document_service.get_document_by_id.return_value = None

        with pytest.raises(ValueError, match="not found"):
            commands.delete_document(mock_context, 999)


class TestCmdUpload:
    """Tests for cmd_upload CLI handler."""

    @patch("src.domains.documents.commands.upload_document")
    @patch("builtins.print")
    def test_cmd_upload_success(self, mock_print: MagicMock, mock_upload_doc: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_upload with successful upload."""
        args = argparse.Namespace(file="test.pdf")
        mock_upload_doc.return_value = {
            "id": 1,
            "filename": "test.pdf",
            "file_size": 100,
            "text_length": 50,
            "status": "uploaded",
        }

        commands.cmd_upload(mock_context, args)

        mock_upload_doc.assert_called_once()
        assert mock_print.call_count >= 1
        # Check that success message was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("successfully" in str(call) for call in print_calls)

    @patch("src.domains.documents.commands.upload_document")
    @patch("builtins.print")
    def test_cmd_upload_duplicate(self, mock_print: MagicMock, mock_upload_doc: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_upload with duplicate document."""
        args = argparse.Namespace(file="test.pdf")
        mock_upload_doc.return_value = {
            "id": 1,
            "filename": "test.pdf",
            "file_size": 100,
            "status": "already_exists",
        }

        commands.cmd_upload(mock_context, args)

        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("already exists" in str(call) for call in print_calls)

    @patch("src.domains.documents.commands.upload_document")
    @patch("builtins.print")
    def test_cmd_upload_file_not_found(self, mock_print: MagicMock, mock_upload_doc: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_upload with non-existent file."""
        args = argparse.Namespace(file="nonexistent.pdf")
        mock_upload_doc.side_effect = FileNotFoundError("File not found")

        with pytest.raises(SystemExit) as exc_info:
            commands.cmd_upload(mock_context, args)

        assert exc_info.value.code == 1


class TestCmdList:
    """Tests for cmd_list CLI handler."""

    @patch("src.domains.documents.commands.list_documents")
    @patch("builtins.print")
    def test_cmd_list_with_documents(self, mock_print: MagicMock, mock_list_docs: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_list with documents."""
        args = argparse.Namespace()
        mock_list_docs.return_value = {
            "documents": [
                {
                    "id": 1,
                    "filename": "test.pdf",
                    "file_size": 100,
                    "mime_type": "application/pdf",
                    "chunk_count": 5,
                    "created_at": "2024-01-01T00:00:00",
                }
            ],
            "count": 1,
        }

        commands.cmd_list(mock_context, args)

        mock_list_docs.assert_called_once_with(mock_context)
        assert mock_print.call_count >= 1

    @patch("src.domains.documents.commands.list_documents")
    @patch("builtins.print")
    def test_cmd_list_no_documents(self, mock_print: MagicMock, mock_list_docs: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_list with no documents."""
        args = argparse.Namespace()
        mock_list_docs.return_value = {"documents": [], "count": 0}

        commands.cmd_list(mock_context, args)

        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("No documents" in str(call) for call in print_calls)


class TestCmdDelete:
    """Tests for cmd_delete CLI handler."""

    @patch("src.domains.documents.commands.delete_document")
    @patch("builtins.print")
    def test_cmd_delete_success(self, mock_print: MagicMock, mock_delete_doc: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_delete with successful deletion."""
        args = argparse.Namespace(doc_id=1)
        mock_delete_doc.return_value = {"message": "Document 1 deleted successfully"}

        commands.cmd_delete(mock_context, args)

        mock_delete_doc.assert_called_once_with(mock_context, 1)
        assert mock_print.call_count >= 1

    @patch("src.domains.documents.commands.delete_document")
    @patch("builtins.print")
    def test_cmd_delete_not_found(self, mock_print: MagicMock, mock_delete_doc: MagicMock, mock_context: MagicMock) -> None:
        """Test cmd_delete with non-existent document."""
        args = argparse.Namespace(doc_id=999)
        mock_delete_doc.side_effect = ValueError("Document not found")

        with pytest.raises(SystemExit) as exc_info:
            commands.cmd_delete(mock_context, args)

        assert exc_info.value.code == 1
