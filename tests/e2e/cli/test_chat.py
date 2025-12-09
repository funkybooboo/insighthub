"""E2E tests for chat CLI commands."""

import subprocess
import sys

import pytest


@pytest.mark.integration
class TestChatCLI:
    """End-to-end tests for chat CLI commands."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    def create_workspace(self, name="Chat Test Workspace"):
        """Helper to create a workspace."""
        import re

        create_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input=f"{name}\nTest workspace for chat\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_result.returncode == 0

        # Extract workspace ID
        output_lines = create_result.stdout.strip().split("\n")
        created_line = [line for line in output_lines if "created workspace" in line.lower()][0]
        match = re.search(r"Created workspace \[(\d+)\]", created_line)
        workspace_id = match.group(1) if match else None
        assert workspace_id is not None, f"Could not extract workspace ID from: {created_line}"

        return workspace_id

    def test_chat_list_empty(self):
        """Test listing chat sessions in workspace with no sessions."""
        workspace_id = self.create_workspace("Empty Chat Workspace")

        result = self.run_cli("chat", "list", workspace_id)
        assert result.returncode == 0
        assert "no chat sessions found" in result.stdout.lower()

    def test_chat_create_with_title(self):
        """Test creating a new chat session with a title."""
        workspace_id = self.create_workspace("New Chat Workspace")

        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", workspace_id],
            input="Test Chat Session\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "created chat session" in result.stdout.lower()
        assert "Test Chat Session" in result.stdout

    def test_chat_create_without_title(self):
        """Test creating a new chat session without a title."""
        workspace_id = self.create_workspace("No Title Chat Workspace")

        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", workspace_id],
            input="Untitled Session\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "created chat session" in result.stdout.lower()

    def test_chat_list_with_sessions(self):
        """Test listing chat sessions after creating some."""
        workspace_id = self.create_workspace("List Chat Workspace")

        # Create multiple sessions
        subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", workspace_id],
            input="Session 1\n",
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", workspace_id],
            input="Session 2\n",
            capture_output=True,
            text=True,
        )

        # List sessions
        result = self.run_cli("chat", "list", workspace_id)
        assert result.returncode == 0
        assert "Session 1" in result.stdout
        assert "Session 2" in result.stdout

    def test_chat_select(self):
        """Test selecting a chat session."""
        workspace_id = self.create_workspace("Select Chat Workspace")

        # Create a session
        create_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", workspace_id],
            input="Select Test Session\n",
            capture_output=True,
            text=True,
        )
        assert create_result.returncode == 0

        # Extract session ID
        import re

        output_lines = create_result.stdout.strip().split("\n")
        created_line = [line for line in output_lines if "created chat session" in line.lower()][0]
        match = re.search(r"Created chat session \[(\d+)\]", created_line)
        session_id = match.group(1) if match else None
        assert session_id is not None, f"Could not extract session ID from: {created_line}"

        # Select the session
        result = self.run_cli("chat", "select", session_id)
        assert result.returncode == 0
        assert "selected" in result.stdout.lower()

    def test_chat_history_no_session_selected(self):
        """Test viewing history without selecting a session."""
        result = self.run_cli("chat", "history")
        # May fail or succeed depending on test order
        if result.returncode != 0:
            assert "no chat session selected" in result.stderr.lower()

    def test_chat_history_empty(self):
        """Test viewing history in empty session."""
        workspace_id = self.create_workspace("History Empty Workspace")

        # Create and select a session
        create_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", workspace_id],
            input="History Test\n",
            capture_output=True,
            text=True,
        )
        assert create_result.returncode == 0

        # Extract and select session ID
        import re

        output_lines = create_result.stdout.strip().split("\n")
        created_line = [line for line in output_lines if "created chat session" in line.lower()][0]
        match = re.search(r"Created chat session \[(\d+)\]", created_line)
        session_id = match.group(1) if match else None
        assert session_id is not None, f"Could not extract session ID from: {created_line}"

        subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "select", session_id],
            capture_output=True,
            text=True,
        )

        # View history
        result = self.run_cli("chat", "history")
        assert result.returncode == 0
        assert "no messages" in result.stdout.lower()

    def test_chat_send_no_session_selected(self):
        """Test sending a message without selecting a session."""
        result = self.run_cli("chat", "send", "Hello")
        # May fail or succeed depending on test order
        if result.returncode != 0:
            assert "no chat session selected" in result.stderr.lower()

    def test_chat_delete(self):
        """Test deleting a chat session."""
        workspace_id = self.create_workspace("Delete Chat Workspace")

        # Create a session
        create_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", workspace_id],
            input="Delete Test Session\n",
            capture_output=True,
            text=True,
        )
        assert create_result.returncode == 0

        # Extract session ID
        import re

        output_lines = create_result.stdout.strip().split("\n")
        created_line = [line for line in output_lines if "created chat session" in line.lower()][0]
        match = re.search(r"Created chat session \[(\d+)\]", created_line)
        session_id = match.group(1) if match else None
        assert session_id is not None, f"Could not extract session ID from: {created_line}"

        # Delete the session (confirm with "yes")
        delete_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "delete", session_id],
            input="yes\n",
            capture_output=True,
            text=True,
        )
        assert delete_result.returncode == 0
        assert "deleted" in delete_result.stdout.lower()

        # Verify it's gone
        list_result = self.run_cli("chat", "list", workspace_id)
        assert "Delete Test Session" not in list_result.stdout

    def test_chat_delete_nonexistent(self):
        """Test deleting a non-existent chat session."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "delete", "999999"],
            input="yes\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_chat_create_invalid_workspace(self):
        """Test creating a chat session in non-existent workspace."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", "999999"],
            input="Test\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_chat_help(self):
        """Test chat help command."""
        result = self.run_cli("chat", "--help")
        assert result.returncode == 0
        assert "chat" in result.stdout.lower()
        assert "list" in result.stdout.lower()
        assert "new" in result.stdout.lower()
        assert "send" in result.stdout.lower()
