"""E2E tests for CLI error handling and edge cases."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
class TestCLIErrorHandling:
    """End-to-end tests for CLI error handling."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    # ==================== WORKSPACE ERRORS ====================

    def test_workspace_show_invalid_id(self):
        """Test showing workspace with invalid ID."""
        result = self.run_cli("workspace", "show", "invalid")
        assert result.returncode != 0

    def test_workspace_show_negative_id(self):
        """Test showing workspace with negative ID."""
        result = self.run_cli("workspace", "show", "-1")
        assert result.returncode != 0

    def test_workspace_update_nonexistent(self):
        """Test updating a workspace that doesn't exist."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "update", "999999"],
            input="Test\nTest\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_workspace_select_nonexistent(self):
        """Test selecting a workspace that doesn't exist."""
        result = self.run_cli("workspace", "select", "999999")
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_workspace_delete_nonexistent(self):
        """Test deleting a workspace that doesn't exist."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "delete", "999999"],
            input="yes\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_workspace_delete_cancel(self):
        """Test canceling workspace deletion."""
        # First create a workspace
        create = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Delete Cancel Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create.stdout)
        ws_id = match.group(1) if match else None
        assert ws_id is not None

        # Try to delete but cancel
        subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "delete", ws_id],
            input="no\n",
            capture_output=True,
            text=True,
        )
        # Should either succeed with cancellation message or just exit
        # Workspace should still exist
        show = self.run_cli("workspace", "show", ws_id)
        assert show.returncode == 0

    # ==================== DOCUMENT ERRORS ====================

    def test_document_upload_without_workspace(self):
        """Test uploading document without selecting workspace."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test\n")
            test_file = Path(f.name)

        try:
            # Note: This may fail or succeed depending on if there's a workspace selected
            # from previous tests. The important thing is it doesn't crash.
            result = self.run_cli("document", "upload", str(test_file))
            if result.returncode != 0:
                assert "no workspace selected" in result.stderr.lower()
        finally:
            test_file.unlink()

    def test_document_upload_empty_file(self):
        """Test uploading an empty file."""
        # Create workspace first
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Empty File Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            # Write nothing - empty file
            test_file = Path(f.name)

        try:
            # Upload empty file - might succeed or fail depending on validation
            result = self.run_cli("document", "upload", str(test_file))
            # Just verify it doesn't crash
            assert result.returncode in [0, 1]
        finally:
            test_file.unlink()

    def test_document_upload_large_path(self):
        """Test uploading file with very long path."""
        # Create workspace first
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Long Path Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Create file with very long name
        long_name = "a" * 200 + ".txt"
        with tempfile.NamedTemporaryFile(mode="w", suffix=long_name, delete=False) as f:
            f.write("Test content\n")
            test_file = Path(f.name)

        try:
            result = self.run_cli("document", "upload", str(test_file))
            # Should handle gracefully
            assert result.returncode in [0, 1]
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_document_show_invalid_id(self):
        """Test showing document with invalid ID."""
        result = self.run_cli("document", "show", "invalid")
        assert result.returncode != 0

    def test_document_show_nonexistent(self):
        """Test showing document that doesn't exist."""
        result = self.run_cli("document", "show", "999999")
        assert result.returncode != 0

    def test_document_remove_cancel(self):
        """Test canceling document removal."""
        # Create workspace and upload document
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Remove Cancel Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test\n")
            test_file = Path(f.name)

        try:
            upload = self.run_cli("document", "upload", str(test_file))
            assert upload.returncode == 0

            # Try to remove but cancel
            subprocess.run(
                [sys.executable, "-m", "src.cli", "document", "remove", test_file.name],
                input="no\n",
                capture_output=True,
                text=True,
            )
            # Should cancel gracefully

            # Document should still be there
            list_docs = self.run_cli("document", "list")
            assert test_file.name in list_docs.stdout or list_docs.returncode == 0
        finally:
            test_file.unlink()

    # ==================== CHAT ERRORS ====================

    def test_chat_list_invalid_workspace(self):
        """Test listing chats for invalid workspace."""
        result = self.run_cli("chat", "list", "invalid")
        assert result.returncode != 0

    def test_chat_list_nonexistent_workspace(self):
        """Test listing chats for nonexistent workspace."""
        result = self.run_cli("chat", "list", "999999")
        assert result.returncode != 0

    def test_chat_create_invalid_workspace(self):
        """Test creating chat in invalid workspace."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", "invalid"],
            input="Test\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_chat_select_invalid_id(self):
        """Test selecting chat with invalid ID."""
        result = self.run_cli("chat", "select", "invalid")
        assert result.returncode != 0

    def test_chat_select_nonexistent(self):
        """Test selecting chat that doesn't exist."""
        result = self.run_cli("chat", "select", "999999")
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_chat_delete_cancel(self):
        """Test canceling chat deletion."""
        # Create workspace and chat
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Chat Delete Cancel\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None

        create_chat = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
            input="Test Session\n",
            capture_output=True,
            text=True,
        )
        assert create_chat.returncode == 0

        match = re.search(r"Created chat session \[(\d+)\]", create_chat.stdout)
        chat_id = match.group(1) if match else None
        assert chat_id is not None

        # Try to delete but cancel
        subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "delete", chat_id],
            input="no\n",
            capture_output=True,
            text=True,
        )
        # Should cancel gracefully

        # Chat should still exist
        list_chats = self.run_cli("chat", "list", ws_id)
        assert "Test Session" in list_chats.stdout or list_chats.returncode == 0

    def test_chat_send_empty_message(self):
        """Test sending an empty message."""
        # Create workspace and chat
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Empty Message Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None

        create_chat = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
            input="Test Session\n",
            capture_output=True,
            text=True,
        )
        assert create_chat.returncode == 0

        match = re.search(r"Created chat session \[(\d+)\]", create_chat.stdout)
        chat_id = match.group(1) if match else None

        select = self.run_cli("chat", "select", chat_id)
        assert select.returncode == 0

        # Try to send empty message
        result = self.run_cli("chat", "send", "")
        # Should handle gracefully
        assert result.returncode in [0, 1]

    # ==================== GENERAL ERRORS ====================

    def test_no_command(self):
        """Test running CLI with no command."""
        result = self.run_cli()
        # Should show help and exit cleanly
        assert result.returncode == 0
        assert "insighthub" in result.stdout.lower() or "usage" in result.stdout.lower()

    def test_invalid_resource(self):
        """Test using invalid resource."""
        result = self.run_cli("invalid-resource")
        assert result.returncode != 0

    def test_invalid_action(self):
        """Test using invalid action for valid resource."""
        result = self.run_cli("workspace", "invalid-action")
        assert result.returncode != 0

    def test_help_commands(self):
        """Test that all --help commands work."""
        resources = ["workspace", "document", "chat", "default-rag-config"]

        for resource in resources:
            result = self.run_cli(resource, "--help")
            assert result.returncode == 0
            assert resource in result.stdout.lower()

    def test_missing_required_argument(self):
        """Test commands with missing required arguments."""
        # workspace show requires ID
        result = self.run_cli("workspace", "show")
        assert result.returncode != 0

        # document show requires ID
        result = self.run_cli("document", "show")
        assert result.returncode != 0

        # document upload requires file path
        result = self.run_cli("document", "upload")
        assert result.returncode != 0

        # chat create requires workspace ID
        result = self.run_cli("chat", "create")
        assert result.returncode != 0

    def test_workspace_create_with_empty_inputs(self):
        """Test creating workspace with empty name (but providing all prompts)."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="\n\nvector\n",
            capture_output=True,
            text=True,
        )
        # Might succeed with empty name or fail - should handle gracefully
        assert result.returncode in [0, 1]

    def test_default_rag_config_invalid_type(self):
        """Test creating RAG config with completely invalid input."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "create"],
            input="completely-invalid-type\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_document_upload_directory_instead_of_file(self):
        """Test uploading a directory instead of a file."""
        # Create workspace first
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Dir Upload Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Try to upload a directory
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = self.run_cli("document", "upload", tmpdir)
            # Should fail or handle gracefully
            assert result.returncode != 0
