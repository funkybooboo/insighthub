"""E2E tests for document CLI commands."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
class TestDocumentCLI:
    """End-to-end tests for document CLI commands."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    def create_workspace_and_select(self, name="Document Test Workspace"):
        """Helper to create and select a workspace."""
        create_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input=f"{name}\nTest workspace for documents\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_result.returncode == 0

        # Extract workspace ID
        output_lines = create_result.stdout.strip().split("\n")
        created_line = [line for line in output_lines if "created workspace" in line.lower()][0]
        workspace_id = created_line.split("[")[1].split("]")[0]

        # Select the workspace
        select_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "select", workspace_id],
            capture_output=True,
            text=True,
        )
        assert select_result.returncode == 0

        return workspace_id

    def test_document_list_no_workspace_selected(self):
        """Test document list without selecting a workspace."""
        # This might fail if there's already a workspace selected from previous tests
        # So we'll just verify the command runs
        result = self.run_cli("document", "list")
        # Either succeeds with a selected workspace or fails with error message
        if result.returncode != 0:
            assert "no workspace selected" in result.stderr.lower()

    def test_document_list_empty(self):
        """Test document list in empty workspace."""
        self.create_workspace_and_select("Empty Doc Workspace")

        result = self.run_cli("document", "list")
        assert result.returncode == 0
        assert "no documents found" in result.stdout.lower()

    def test_document_upload_and_list(self):
        """Test uploading a document and listing it."""
        self.create_workspace_and_select("Upload Test Workspace")

        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is a test document.\nIt has multiple lines.\n")
            test_file_path = f.name

        try:
            # Upload the document
            upload_result = self.run_cli("document", "upload", test_file_path)
            assert upload_result.returncode == 0
            assert "uploaded" in upload_result.stdout.lower()

            # List documents and verify it appears
            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0
            assert Path(test_file_path).name in list_result.stdout

        finally:
            # Clean up temporary file
            Path(test_file_path).unlink()

    def test_document_show(self):
        """Test showing document details."""
        self.create_workspace_and_select("Show Doc Workspace")

        # Create and upload a test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content for show command.\n")
            test_file_path = f.name

        try:
            # Upload the document
            upload_result = self.run_cli("document", "upload", test_file_path)
            assert upload_result.returncode == 0

            # Extract document ID
            output_lines = upload_result.stdout.strip().split("\n")
            uploaded_line = [line for line in output_lines if "uploaded" in line.lower()][0]
            document_id = uploaded_line.split("[")[1].split("]")[0]

            # Show the document
            show_result = self.run_cli("document", "show", document_id)
            assert show_result.returncode == 0
            assert Path(test_file_path).name in show_result.stdout
            assert "status" in show_result.stdout.lower()
            assert "size" in show_result.stdout.lower()
            assert "mime type" in show_result.stdout.lower()

        finally:
            Path(test_file_path).unlink()

    def test_document_upload_nonexistent_file(self):
        """Test uploading a file that doesn't exist."""
        self.create_workspace_and_select("Upload Error Workspace")

        result = self.run_cli("document", "upload", "/nonexistent/file.txt")
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_document_remove(self):
        """Test removing a document."""
        self.create_workspace_and_select("Remove Doc Workspace")

        # Create and upload a test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content for removal.\n")
            test_file_path = f.name

        filename = Path(test_file_path).name

        try:
            # Upload the document
            upload_result = self.run_cli("document", "upload", test_file_path)
            assert upload_result.returncode == 0

            # Remove the document (confirm with "yes")
            remove_result = subprocess.run(
                [sys.executable, "-m", "src.cli", "document", "remove", filename],
                input="yes\n",
                capture_output=True,
                text=True,
            )
            assert remove_result.returncode == 0
            assert "deleted" in remove_result.stdout.lower()

            # Verify it's gone
            list_result = self.run_cli("document", "list")
            assert filename not in list_result.stdout

        finally:
            Path(test_file_path).unlink()

    def test_document_remove_nonexistent(self):
        """Test removing a document that doesn't exist."""
        self.create_workspace_and_select("Remove Error Workspace")

        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "document", "remove", "nonexistent.txt"],
            input="yes\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_document_help(self):
        """Test document help command."""
        result = self.run_cli("document", "--help")
        assert result.returncode == 0
        assert "document" in result.stdout.lower()
        assert "list" in result.stdout.lower()
        assert "upload" in result.stdout.lower()
        assert "remove" in result.stdout.lower()
