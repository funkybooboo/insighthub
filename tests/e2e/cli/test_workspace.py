"""E2E tests for workspace CLI commands."""

import subprocess
import sys

import pytest


@pytest.mark.integration
class TestWorkspaceCLI:
    """End-to-end tests for workspace CLI commands."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    def test_workspace_list(self):
        """Test workspace list command."""
        result = self.run_cli("workspace", "list")
        assert result.returncode == 0
        # Should either show workspaces or "No workspace found"
        assert "workspace" in result.stdout.lower() or "no workspace found" in result.stdout.lower()

    def test_workspace_new_interactive(self):
        """Test workspace new command with interactive input."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="E2E Test Workspace\nTest description\nvector\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "created workspace" in result.stdout.lower()

    def test_workspace_show(self):
        """Test workspace show command."""
        # First create a workspace to show
        create_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Show Test Workspace\nShow description\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_result.returncode == 0

        # Extract workspace ID from output (format: "Created workspace [ID] Name")
        output_lines = create_result.stdout.strip().split("\n")
        created_line = [line for line in output_lines if "created workspace" in line.lower()][0]
        # Find the workspace ID by looking for pattern "Created workspace [ID]"
        import re

        match = re.search(r"Created workspace \[(\d+)\]", created_line)
        workspace_id = match.group(1) if match else None
        assert workspace_id is not None, f"Could not extract workspace ID from: {created_line}"

        # Show the workspace
        result = self.run_cli("workspace", "show", workspace_id)
        assert result.returncode == 0
        assert "Show Test Workspace" in result.stdout
        assert "vector" in result.stdout.lower()
        # Should display RAG configuration
        assert (
            "rag configuration" in result.stdout.lower()
            or "chunking algorithm" in result.stdout.lower()
        )

    def test_workspace_update_interactive(self):
        """Test workspace update command."""
        # First create a workspace
        create_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Update Test Workspace\nOriginal description\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_result.returncode == 0

        # Extract workspace ID
        output_lines = create_result.stdout.strip().split("\n")
        created_line = [line for line in output_lines if "created workspace" in line.lower()][0]
        import re

        match = re.search(r"Created workspace \[(\d+)\]", created_line)
        workspace_id = match.group(1) if match else None
        assert workspace_id is not None, f"Could not extract workspace ID from: {created_line}"

        # Update the workspace
        update_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "update", workspace_id],
            input="Updated Name\nUpdated description\n",
            capture_output=True,
            text=True,
        )
        assert update_result.returncode == 0
        assert "updated" in update_result.stdout.lower()

    def test_workspace_select(self):
        """Test workspace select command."""
        # First create a workspace
        create_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Select Test Workspace\nSelect description\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_result.returncode == 0

        # Extract workspace ID
        output_lines = create_result.stdout.strip().split("\n")
        created_line = [line for line in output_lines if "created workspace" in line.lower()][0]
        import re

        match = re.search(r"Created workspace \[(\d+)\]", created_line)
        workspace_id = match.group(1) if match else None
        assert workspace_id is not None, f"Could not extract workspace ID from: {created_line}"

        # Select the workspace
        result = self.run_cli("workspace", "select", workspace_id)
        assert result.returncode == 0
        assert "selected" in result.stdout.lower()

    def test_workspace_delete(self):
        """Test workspace delete command."""
        # First create a workspace
        create_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Delete Test Workspace\nDelete description\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_result.returncode == 0

        # Extract workspace ID
        output_lines = create_result.stdout.strip().split("\n")
        created_line = [line for line in output_lines if "created workspace" in line.lower()][0]
        import re

        match = re.search(r"Created workspace \[(\d+)\]", created_line)
        workspace_id = match.group(1) if match else None
        assert workspace_id is not None, f"Could not extract workspace ID from: {created_line}"

        # Delete the workspace (confirm with "yes")
        delete_result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "delete", workspace_id],
            input="yes\n",
            capture_output=True,
            text=True,
        )
        assert delete_result.returncode == 0
        assert "deleted" in delete_result.stdout.lower()

    def test_workspace_show_nonexistent(self):
        """Test workspace show with non-existent ID."""
        result = self.run_cli("workspace", "show", "999999")
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_workspace_help(self):
        """Test workspace help command."""
        result = self.run_cli("workspace", "--help")
        assert result.returncode == 0
        assert "workspace" in result.stdout.lower()
        assert "list" in result.stdout.lower()
        assert "new" in result.stdout.lower()
