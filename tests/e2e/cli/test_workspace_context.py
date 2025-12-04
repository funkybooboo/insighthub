"""E2E tests for workspace context switching and state management."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
class TestWorkspaceContext:
    """Test workspace context awareness and switching behavior."""

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

    # ==================== WORKSPACE SELECTION ====================

    def test_select_and_verify_current_workspace(self):
        """Test selecting workspace and verifying it's current."""
        ws_id = self.create_workspace("Select Test")

        result = self.run_cli("workspace", "select", ws_id)
        assert result.returncode == 0
        assert "selected" in result.stdout.lower()

    def test_switch_between_multiple_workspaces(self):
        """Test switching between multiple workspaces."""
        ws1_id = self.create_workspace("Workspace 1")
        ws2_id = self.create_workspace("Workspace 2")
        ws3_id = self.create_workspace("Workspace 3")

        # Select each workspace in sequence
        for ws_id in [ws1_id, ws2_id, ws3_id, ws1_id]:
            result = self.run_cli("workspace", "select", ws_id)
            assert result.returncode == 0
            assert "selected" in result.stdout.lower()

    def test_select_workspace_multiple_times(self):
        """Test selecting the same workspace multiple times."""
        ws_id = self.create_workspace("Multi Select Test")

        for _ in range(3):
            result = self.run_cli("workspace", "select", ws_id)
            assert result.returncode == 0

    # ==================== DOCUMENT OPERATIONS WITH CONTEXT ====================

    def test_document_list_changes_with_workspace_switch(self):
        """Test that document list changes when switching workspaces."""
        # Create two workspaces
        ws1_id = self.create_workspace("WS1 Docs")
        ws2_id = self.create_workspace("WS2 Docs")

        # Select first workspace and upload document
        select1 = self.run_cli("workspace", "select", ws1_id)
        assert select1.returncode == 0

        with tempfile.NamedTemporaryFile(mode="w", suffix="_ws1.txt", delete=False) as f:
            f.write("Document in workspace 1\n")
            doc1_file = Path(f.name)

        try:
            upload1 = self.run_cli("document", "upload", str(doc1_file))
            assert upload1.returncode == 0

            # List documents in first workspace
            list1 = self.run_cli("document", "list")
            assert list1.returncode == 0
            assert doc1_file.name in list1.stdout

            # Select second workspace and upload different document
            select2 = self.run_cli("workspace", "select", ws2_id)
            assert select2.returncode == 0

            with tempfile.NamedTemporaryFile(mode="w", suffix="_ws2.txt", delete=False) as f:
                f.write("Document in workspace 2\n")
                doc2_file = Path(f.name)

            try:
                upload2 = self.run_cli("document", "upload", str(doc2_file))
                assert upload2.returncode == 0

                # List documents in second workspace
                list2 = self.run_cli("document", "list")
                assert list2.returncode == 0
                assert doc2_file.name in list2.stdout
                assert doc1_file.name not in list2.stdout

                # Switch back to first workspace
                select1_again = self.run_cli("workspace", "select", ws1_id)
                assert select1_again.returncode == 0

                # List documents should show first workspace docs again
                list1_again = self.run_cli("document", "list")
                assert list1_again.returncode == 0
                assert doc1_file.name in list1_again.stdout
                assert doc2_file.name not in list1_again.stdout

            finally:
                if doc2_file.exists():
                    doc2_file.unlink()

        finally:
            if doc1_file.exists():
                doc1_file.unlink()

    def test_document_upload_to_different_workspaces(self):
        """Test uploading same filename to different workspaces."""
        ws1_id = self.create_workspace("WS1 Upload")
        ws2_id = self.create_workspace("WS2 Upload")

        # Create test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content\n")
            test_file = Path(f.name)

        try:
            # Upload to first workspace
            select1 = self.run_cli("workspace", "select", ws1_id)
            assert select1.returncode == 0

            upload1 = self.run_cli("document", "upload", str(test_file))
            assert upload1.returncode == 0

            list1 = self.run_cli("document", "list")
            assert list1.returncode == 0
            assert test_file.name in list1.stdout

            # Upload same file to second workspace
            select2 = self.run_cli("workspace", "select", ws2_id)
            assert select2.returncode == 0

            upload2 = self.run_cli("document", "upload", str(test_file))
            assert upload2.returncode == 0

            list2 = self.run_cli("document", "list")
            assert list2.returncode == 0
            assert test_file.name in list2.stdout

        finally:
            if test_file.exists():
                test_file.unlink()

    def test_document_operations_without_workspace_selected(self):
        """Test document operations when no workspace is selected."""
        # Note: This depends on whether there's a previously selected workspace
        # The test verifies the command handles the case appropriately

        # Try to upload document (may succeed if workspace selected, or fail gracefully)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test\n")
            test_file = Path(f.name)

        try:
            # Create a new CLI session by not selecting any workspace
            # (In practice, this is hard to test in isolation due to state persistence)
            result = self.run_cli("document", "list")
            # Should either succeed (if workspace selected) or fail gracefully
            assert result.returncode in [0, 1]

        finally:
            if test_file.exists():
                test_file.unlink()

    # ==================== CHAT OPERATIONS WITH CONTEXT ====================

    def test_chat_sessions_isolated_per_workspace(self):
        """Test that chat sessions are isolated per workspace."""
        # Create two workspaces
        ws1_id = self.create_workspace("WS1 Chat")
        ws2_id = self.create_workspace("WS2 Chat")

        # Create chat in first workspace
        chat1 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws1_id],
            input="Chat 1\n",
            capture_output=True,
            text=True,
        )
        assert chat1.returncode == 0

        # Create chat in second workspace
        chat2 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws2_id],
            input="Chat 2\n",
            capture_output=True,
            text=True,
        )
        assert chat2.returncode == 0

        # List chats for first workspace
        list1 = self.run_cli("chat", "list", ws1_id)
        assert list1.returncode == 0
        assert "Chat 1" in list1.stdout
        assert "Chat 2" not in list1.stdout

        # List chats for second workspace
        list2 = self.run_cli("chat", "list", ws2_id)
        assert list2.returncode == 0
        assert "Chat 2" in list2.stdout
        assert "Chat 1" not in list2.stdout

    def test_chat_context_preserved_after_workspace_switch(self):
        """Test chat context is preserved when switching workspaces."""
        # Create two workspaces with chats
        ws1_id = self.create_workspace("Context WS1")
        ws2_id = self.create_workspace("Context WS2")

        # Create chats in both workspaces
        chat1 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws1_id],
            input="WS1 Chat\n",
            capture_output=True,
            text=True,
        )
        assert chat1.returncode == 0
        chat1_id = self.extract_id(chat1.stdout, r"Created chat session \[(\d+)\]")

        chat2 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws2_id],
            input="WS2 Chat\n",
            capture_output=True,
            text=True,
        )
        assert chat2.returncode == 0
        chat2_id = self.extract_id(chat2.stdout, r"Created chat session \[(\d+)\]")

        # Select first chat
        select1 = self.run_cli("chat", "select", chat1_id)
        assert select1.returncode == 0

        # Switch workspace
        ws_select = self.run_cli("workspace", "select", ws2_id)
        assert ws_select.returncode == 0

        # Select second chat
        select2 = self.run_cli("chat", "select", chat2_id)
        assert select2.returncode == 0

        # Verify can view history
        history = self.run_cli("chat", "history")
        assert history.returncode == 0

    # ==================== WORKSPACE UPDATE WITH CONTEXT ====================

    def test_update_current_workspace(self):
        """Test updating the currently selected workspace."""
        ws_id = self.create_workspace("Original", "Original description")

        # Select workspace
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Update workspace
        update = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "update", ws_id],
            input="Updated Name\nUpdated Description\n",
            capture_output=True,
            text=True,
        )
        assert update.returncode == 0

        # Show workspace to verify update
        show = self.run_cli("workspace", "show", ws_id)
        assert show.returncode == 0
        assert "Updated Name" in show.stdout

    def test_update_non_selected_workspace(self):
        """Test updating a workspace that is not currently selected."""
        ws1_id = self.create_workspace("Workspace 1")
        ws2_id = self.create_workspace("Workspace 2")

        # Select first workspace
        select1 = self.run_cli("workspace", "select", ws1_id)
        assert select1.returncode == 0

        # Update second workspace (not selected)
        update = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "update", ws2_id],
            input="Updated WS2\nUpdated description\n",
            capture_output=True,
            text=True,
        )
        assert update.returncode == 0

        # Show second workspace to verify update
        show = self.run_cli("workspace", "show", ws2_id)
        assert show.returncode == 0
        assert "Updated WS2" in show.stdout

    def test_delete_non_selected_workspace(self):
        """Test deleting a workspace that is not currently selected."""
        ws1_id = self.create_workspace("Keep This")
        ws2_id = self.create_workspace("Delete This")

        # Select first workspace
        select = self.run_cli("workspace", "select", ws1_id)
        assert select.returncode == 0

        # Delete second workspace
        delete = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "delete", ws2_id],
            input="yes\n",
            capture_output=True,
            text=True,
        )
        assert delete.returncode == 0

        # Verify deleted
        show = self.run_cli("workspace", "show", ws2_id)
        assert show.returncode != 0

    # ==================== COMPLEX CONTEXT WORKFLOWS ====================

    def test_full_workspace_lifecycle_with_context(self):
        """Test complete workflow: create, select, use, switch, delete."""
        # Create multiple workspaces
        ws1_id = self.create_workspace("Lifecycle WS1")
        ws2_id = self.create_workspace("Lifecycle WS2")

        # Select first workspace
        select1 = self.run_cli("workspace", "select", ws1_id)
        assert select1.returncode == 0

        # Upload document to first workspace
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("WS1 document\n")
            doc1 = Path(f.name)

        try:
            upload1 = self.run_cli("document", "upload", str(doc1))
            assert upload1.returncode == 0

            # Create chat in first workspace
            chat1 = subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "new", ws1_id],
                input="WS1 Chat\n",
                capture_output=True,
                text=True,
            )
            assert chat1.returncode == 0

            # Switch to second workspace
            select2 = self.run_cli("workspace", "select", ws2_id)
            assert select2.returncode == 0

            # Upload document to second workspace
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                f.write("WS2 document\n")
                doc2 = Path(f.name)

            try:
                upload2 = self.run_cli("document", "upload", str(doc2))
                assert upload2.returncode == 0

                # Verify documents are workspace-specific
                list2 = self.run_cli("document", "list")
                assert list2.returncode == 0
                assert doc2.name in list2.stdout
                assert doc1.name not in list2.stdout

                # Switch back to first workspace
                select1_again = self.run_cli("workspace", "select", ws1_id)
                assert select1_again.returncode == 0

                # Verify first workspace documents
                list1 = self.run_cli("document", "list")
                assert list1.returncode == 0
                assert doc1.name in list1.stdout
                assert doc2.name not in list1.stdout

            finally:
                if doc2.exists():
                    doc2.unlink()

        finally:
            if doc1.exists():
                doc1.unlink()

    def test_workspace_show_all_workspaces(self):
        """Test showing details for multiple workspaces."""
        # Create workspaces with different names
        workspace_names = ["Alpha", "Beta", "Gamma", "Delta"]
        workspace_ids = []

        for name in workspace_names:
            ws_id = self.create_workspace(name, f"{name} description")
            workspace_ids.append(ws_id)

        # Show details for each workspace
        for ws_id, name in zip(workspace_ids, workspace_names):
            show = self.run_cli("workspace", "show", ws_id)
            assert show.returncode == 0
            assert name in show.stdout

    def test_workspace_list_shows_all(self):
        """Test that workspace list shows all created workspaces."""
        # Create several workspaces
        names = ["List Test 1", "List Test 2", "List Test 3"]
        for name in names:
            self.create_workspace(name)

        # List all workspaces
        result = self.run_cli("workspace", "list")
        assert result.returncode == 0

        # Verify all appear in list
        for name in names:
            assert name in result.stdout

    def test_operations_across_workspace_boundaries(self):
        """Test that operations respect workspace boundaries."""
        # Create two workspaces
        ws1_id = self.create_workspace("Boundary WS1")
        ws2_id = self.create_workspace("Boundary WS2")

        # Select workspace 1 and add resources
        select1 = self.run_cli("workspace", "select", ws1_id)
        assert select1.returncode == 0

        # Create chat in workspace 1
        chat1 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws1_id],
            input="Boundary Chat 1\n",
            capture_output=True,
            text=True,
        )
        assert chat1.returncode == 0

        # Upload document to workspace 1
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Workspace 1 content\n")
            doc1 = Path(f.name)

        try:
            upload1 = self.run_cli("document", "upload", str(doc1))
            assert upload1.returncode == 0

            # Switch to workspace 2
            select2 = self.run_cli("workspace", "select", ws2_id)
            assert select2.returncode == 0

            # Verify workspace 2 has no documents
            list2 = self.run_cli("document", "list")
            assert list2.returncode == 0
            assert "no documents found" in list2.stdout.lower()

            # Verify workspace 2 has no chats
            chat_list2 = self.run_cli("chat", "list", ws2_id)
            assert chat_list2.returncode == 0
            assert "no chat sessions found" in chat_list2.stdout.lower()

        finally:
            if doc1.exists():
                doc1.unlink()
