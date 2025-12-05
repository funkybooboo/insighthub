"""E2E tests for state CLI commands."""

import subprocess
import sys

import pytest


@pytest.mark.integration
class TestStateCLI:
    """End-to-end tests for state CLI commands."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    def extract_id(self, output, pattern):
        """Extract ID from command output."""
        import re

        match = re.search(pattern, output)
        return match.group(1) if match else None

    def create_workspace(self, name, description="Test workspace"):
        """Helper to create a workspace."""
        create = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input=f"{name}\n{description}\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create.returncode == 0
        return self.extract_id(create.stdout, r"Created workspace \[(\d+)\]")

    def test_state_show_command_exists(self):
        """Test that state show command exists and runs."""
        result = self.run_cli("state", "show")
        assert result.returncode == 0
        assert "current state" in result.stdout.lower()

    def test_state_show_displays_workspace(self):
        """Test that state show displays the selected workspace."""
        # Create and select a workspace
        ws_id = self.create_workspace("State Test Workspace")
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Check state shows the workspace
        result = self.run_cli("state", "show")
        assert result.returncode == 0
        assert "workspace" in result.stdout.lower()
        assert ws_id in result.stdout

    def test_state_show_displays_session(self):
        """Test that state show displays the selected session."""
        # Create workspace and chat session
        ws_id = self.create_workspace("State Session Test")
        chat = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
            input="Test Chat\n",
            capture_output=True,
            text=True,
        )
        assert chat.returncode == 0
        chat_id = self.extract_id(chat.stdout, r"Created chat session \[(\d+)\]")

        # Select the chat session
        select = self.run_cli("chat", "select", chat_id)
        assert select.returncode == 0

        # Check state shows both workspace and session
        result = self.run_cli("state", "show")
        assert result.returncode == 0
        assert "workspace" in result.stdout.lower()
        assert "session" in result.stdout.lower()
        assert chat_id in result.stdout

    def test_state_show_after_workspace_switch(self):
        """Test that state updates after switching workspaces."""
        # Create two workspaces
        ws1_id = self.create_workspace("State WS1")
        ws2_id = self.create_workspace("State WS2")

        # Select first workspace
        select1 = self.run_cli("workspace", "select", ws1_id)
        assert select1.returncode == 0

        # Check state shows first workspace
        state1 = self.run_cli("state", "show")
        assert state1.returncode == 0
        assert ws1_id in state1.stdout

        # Select second workspace
        select2 = self.run_cli("workspace", "select", ws2_id)
        assert select2.returncode == 0

        # Check state shows second workspace
        state2 = self.run_cli("state", "show")
        assert state2.returncode == 0
        assert ws2_id in state2.stdout

    def test_state_help_command(self):
        """Test state help command."""
        result = self.run_cli("state", "--help")
        assert result.returncode == 0
        assert "state" in result.stdout.lower()
        assert "show" in result.stdout.lower()

    def test_state_show_format(self):
        """Test that state show output is well-formatted."""
        result = self.run_cli("state", "show")
        assert result.returncode == 0

        # Check for expected format elements
        lines = result.stdout.split("\n")
        assert any("current state" in line.lower() for line in lines)
        assert any("workspace" in line.lower() for line in lines)
