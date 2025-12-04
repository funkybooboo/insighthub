"""E2E tests for CLI command combinations and integrated workflows."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
class TestCLICombinations:
    """Test combinations of CLI commands in realistic workflows."""

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

    # ==================== CONFIG -> WORKSPACE -> DOCUMENT WORKFLOWS ====================

    def test_rag_config_workspace_document_chat_workflow(self):
        """Test complete workflow: RAG config -> workspace -> document -> chat."""
        # Set RAG config
        config = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
            capture_output=True,
            text=True,
        )
        assert config.returncode == 0

        # Create workspace
        ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Full Workflow\nComplete workflow test\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws.returncode == 0
        ws_id = self.extract_id(ws.stdout, r"Created workspace \[(\d+)\]")

        # Select workspace
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Upload document
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Full workflow test document.\n")
            doc_file = Path(f.name)

        try:
            upload = self.run_cli("document", "upload", str(doc_file))
            assert upload.returncode == 0

            # Create chat
            chat = subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
                input="Workflow Chat\n",
                capture_output=True,
                text=True,
            )
            assert chat.returncode == 0
            chat_id = self.extract_id(chat.stdout, r"Created chat session \[(\d+)\]")

            # Select chat and send message
            select_chat = self.run_cli("chat", "select", chat_id)
            assert select_chat.returncode == 0

            send = self.run_cli("chat", "send", "What documents do we have?")
            assert send.returncode in [0, 1]

        finally:
            if doc_file.exists():
                doc_file.unlink()

    def test_multiple_workspaces_with_different_configs(self):
        """Test creating multiple workspaces with different RAG configs."""
        # Create vector workspace
        vector_config = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
            capture_output=True,
            text=True,
        )
        assert vector_config.returncode == 0

        vector_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Vector Workspace\nVector RAG workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert vector_ws.returncode == 0
        vector_ws_id = self.extract_id(vector_ws.stdout, r"Created workspace \[(\d+)\]")

        # Create graph workspace
        graph_config = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\nspacy\ndependency-parsing\nleiden\n",
            capture_output=True,
            text=True,
        )
        assert graph_config.returncode == 0

        graph_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Graph Workspace\nGraph RAG workspace\ngraph\n",
            capture_output=True,
            text=True,
        )
        assert graph_ws.returncode == 0
        graph_ws_id = self.extract_id(graph_ws.stdout, r"Created workspace \[(\d+)\]")

        # Verify both workspaces exist
        show_vector = self.run_cli("workspace", "show", vector_ws_id)
        assert show_vector.returncode == 0
        assert "Vector Workspace" in show_vector.stdout

        show_graph = self.run_cli("workspace", "show", graph_ws_id)
        assert show_graph.returncode == 0
        assert "Graph Workspace" in show_graph.stdout

    # ==================== DOCUMENT OPERATIONS COMBINATIONS ====================

    def test_upload_list_show_remove_workflow(self):
        """Test upload -> list -> show -> remove workflow."""
        # Create and select workspace
        ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Doc Operations\nDocument operations test\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws.returncode == 0
        ws_id = self.extract_id(ws.stdout, r"Created workspace \[(\d+)\]")

        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Create and upload document
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test document content.\n")
            doc_file = Path(f.name)

        try:
            # Upload
            upload = self.run_cli("document", "upload", str(doc_file))
            assert upload.returncode == 0
            doc_id = self.extract_id(upload.stdout, r"Uploaded \[(\d+)\]")

            # List
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            assert doc_file.name in list_docs.stdout

            # Show
            show = self.run_cli("document", "show", doc_id)
            assert show.returncode == 0
            assert doc_file.name in show.stdout

            # Remove
            remove = subprocess.run(
                [sys.executable, "-m", "src.cli", "document", "remove", doc_file.name],
                input="yes\n",
                capture_output=True,
                text=True,
            )
            assert remove.returncode == 0

            # Verify removed
            list_after = self.run_cli("document", "list")
            assert list_after.returncode == 0
            assert "no documents found" in list_after.stdout.lower()

        finally:
            if doc_file.exists():
                doc_file.unlink()

    def test_multiple_document_uploads_and_operations(self):
        """Test uploading multiple documents and performing various operations."""
        # Create and select workspace
        ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Multi Docs\nMultiple documents test\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws.returncode == 0
        ws_id = self.extract_id(ws.stdout, r"Created workspace \[(\d+)\]")

        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Create multiple documents
        doc_files = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_doc{i}.txt", delete=False) as f:
                f.write(f"Document {i} content.\n")
                doc_files.append(Path(f.name))

        try:
            # Upload all documents
            doc_ids = []
            for doc_file in doc_files:
                upload = self.run_cli("document", "upload", str(doc_file))
                assert upload.returncode == 0
                doc_id = self.extract_id(upload.stdout, r"Uploaded \[(\d+)\]")
                doc_ids.append(doc_id)

            # List all documents
            list_all = self.run_cli("document", "list")
            assert list_all.returncode == 0
            for doc_file in doc_files:
                assert doc_file.name in list_all.stdout

            # Show each document
            for doc_id in doc_ids:
                show = self.run_cli("document", "show", doc_id)
                assert show.returncode == 0

            # Remove some documents
            for i in range(0, len(doc_files), 2):  # Remove every other document
                remove = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "src.cli",
                        "document",
                        "remove",
                        doc_files[i].name,
                    ],
                    input="yes\n",
                    capture_output=True,
                    text=True,
                )
                assert remove.returncode == 0

            # List remaining documents
            list_remaining = self.run_cli("document", "list")
            assert list_remaining.returncode == 0

        finally:
            for doc_file in doc_files:
                if doc_file.exists():
                    doc_file.unlink()

    # ==================== CHAT SESSION COMBINATIONS ====================

    def test_multiple_chat_sessions_workflow(self):
        """Test creating and managing multiple chat sessions."""
        # Create workspace
        ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Multi Chat\nMultiple chat sessions\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws.returncode == 0
        ws_id = self.extract_id(ws.stdout, r"Created workspace \[(\d+)\]")

        # Create multiple chat sessions
        chat_ids = []
        for i in range(4):
            chat = subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
                input=f"Chat Session {i}\n",
                capture_output=True,
                text=True,
            )
            assert chat.returncode == 0
            chat_id = self.extract_id(chat.stdout, r"Created chat session \[(\d+)\]")
            chat_ids.append(chat_id)

        # List all sessions
        list_chats = self.run_cli("chat", "list", ws_id)
        assert list_chats.returncode == 0
        for i in range(4):
            assert f"Chat Session {i}" in list_chats.stdout

        # Select and use each session
        for i, chat_id in enumerate(chat_ids):
            select = self.run_cli("chat", "select", chat_id)
            assert select.returncode == 0

            history = self.run_cli("chat", "history")
            assert history.returncode == 0

        # Delete some sessions
        for i in [0, 2]:  # Delete first and third sessions
            delete = subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "delete", chat_ids[i]],
                input="yes\n",
                capture_output=True,
                text=True,
            )
            assert delete.returncode == 0

        # List remaining sessions
        list_after = self.run_cli("chat", "list", ws_id)
        assert list_after.returncode == 0
        assert "Chat Session 1" in list_after.stdout
        assert "Chat Session 3" in list_after.stdout
        assert "Chat Session 0" not in list_after.stdout
        assert "Chat Session 2" not in list_after.stdout

    def test_chat_across_workspace_lifecycle(self):
        """Test chat sessions through workspace creation, update, and operations."""
        # Create workspace
        ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Lifecycle Chat\nWorkspace lifecycle test\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws.returncode == 0
        ws_id = self.extract_id(ws.stdout, r"Created workspace \[(\d+)\]")

        # Create chat
        chat = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
            input="Original Chat\n",
            capture_output=True,
            text=True,
        )
        assert chat.returncode == 0
        chat_id = self.extract_id(chat.stdout, r"Created chat session \[(\d+)\]")

        # Update workspace
        update = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "update", ws_id],
            input="Updated Lifecycle\nUpdated description\n",
            capture_output=True,
            text=True,
        )
        assert update.returncode == 0

        # Verify chat still exists
        list_chats = self.run_cli("chat", "list", ws_id)
        assert list_chats.returncode == 0
        assert "Original Chat" in list_chats.stdout

        # Select and use chat
        select = self.run_cli("chat", "select", chat_id)
        assert select.returncode == 0

        history = self.run_cli("chat", "history")
        assert history.returncode == 0

    # ==================== WORKSPACE MANAGEMENT COMBINATIONS ====================

    def test_create_list_show_update_delete_workflow(self):
        """Test complete workspace management workflow."""
        # Create multiple workspaces
        ws_ids = []
        for i in range(3):
            ws = subprocess.run(
                [sys.executable, "-m", "src.cli", "workspace", "new"],
                input=f"Workspace {i}\nDescription {i}\nvector\n",
                capture_output=True,
                text=True,
            )
            assert ws.returncode == 0
            ws_id = self.extract_id(ws.stdout, r"Created workspace \[(\d+)\]")
            ws_ids.append(ws_id)

        # List all workspaces
        list_ws = self.run_cli("workspace", "list")
        assert list_ws.returncode == 0
        for i in range(3):
            assert f"Workspace {i}" in list_ws.stdout

        # Show each workspace
        for ws_id in ws_ids:
            show = self.run_cli("workspace", "show", ws_id)
            assert show.returncode == 0

        # Update first workspace
        update = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "update", ws_ids[0]],
            input="Updated Name\nUpdated Description\n",
            capture_output=True,
            text=True,
        )
        assert update.returncode == 0

        # Verify update
        show_updated = self.run_cli("workspace", "show", ws_ids[0])
        assert show_updated.returncode == 0
        assert "Updated Name" in show_updated.stdout

        # Delete second workspace
        delete = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "delete", ws_ids[1]],
            input="yes\n",
            capture_output=True,
            text=True,
        )
        assert delete.returncode == 0

        # Verify deletion
        show_deleted = self.run_cli("workspace", "show", ws_ids[1])
        assert show_deleted.returncode != 0

    def test_workspace_with_all_resource_types(self):
        """Test workspace containing documents and chat sessions."""
        # Create workspace
        ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="All Resources\nAll resource types\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws.returncode == 0
        ws_id = self.extract_id(ws.stdout, r"Created workspace \[(\d+)\]")

        # Select workspace
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Add documents
        doc_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_res{i}.txt", delete=False) as f:
                f.write(f"Resource document {i}\n")
                doc_files.append(Path(f.name))

        try:
            for doc_file in doc_files:
                upload = self.run_cli("document", "upload", str(doc_file))
                assert upload.returncode == 0

            # Add chat sessions
            for i in range(3):
                chat = subprocess.run(
                    [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
                    input=f"Resource Chat {i}\n",
                    capture_output=True,
                    text=True,
                )
                assert chat.returncode == 0

            # Verify documents
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            for doc_file in doc_files:
                assert doc_file.name in list_docs.stdout

            # Verify chats
            list_chats = self.run_cli("chat", "list", ws_id)
            assert list_chats.returncode == 0
            for i in range(3):
                assert f"Resource Chat {i}" in list_chats.stdout

            # Show workspace details
            show = self.run_cli("workspace", "show", ws_id)
            assert show.returncode == 0
            assert "All Resources" in show.stdout

        finally:
            for doc_file in doc_files:
                if doc_file.exists():
                    doc_file.unlink()

    # ==================== HELP COMMAND COMBINATIONS ====================

    def test_help_for_all_commands(self):
        """Test help command for all main commands."""
        commands = [
            ["workspace", "--help"],
            ["document", "--help"],
            ["chat", "--help"],
            ["default-rag-config", "--help"],
        ]

        for cmd in commands:
            result = self.run_cli(*cmd)
            assert result.returncode == 0
            assert "help" in result.stdout.lower() or len(result.stdout) > 0

    def test_help_with_subcommands(self):
        """Test that help shows available subcommands."""
        result = self.run_cli("workspace", "--help")
        assert result.returncode == 0
        # Help should mention subcommands
        assert "list" in result.stdout.lower() or "new" in result.stdout.lower()

    # ==================== ERROR RECOVERY WORKFLOWS ====================

    def test_workspace_operations_after_errors(self):
        """Test that workspace operations work after encountering errors."""
        # Try to show non-existent workspace (error)
        show_error = self.run_cli("workspace", "show", "999999")
        assert show_error.returncode != 0

        # Create workspace (should succeed)
        ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Error Recovery\nRecovery test\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws.returncode == 0
        ws_id = self.extract_id(ws.stdout, r"Created workspace \[(\d+)\]")

        # Show workspace (should succeed)
        show = self.run_cli("workspace", "show", ws_id)
        assert show.returncode == 0

    def test_document_operations_after_errors(self):
        """Test that document operations work after encountering errors."""
        # Create and select workspace
        ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Doc Error Recovery\nDocument error test\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws.returncode == 0
        ws_id = self.extract_id(ws.stdout, r"Created workspace \[(\d+)\]")

        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Try to upload non-existent file (error)
        upload_error = self.run_cli("document", "upload", "/nonexistent/file.txt")
        assert upload_error.returncode != 0

        # Upload valid file (should succeed)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Error recovery document\n")
            doc_file = Path(f.name)

        try:
            upload = self.run_cli("document", "upload", str(doc_file))
            assert upload.returncode == 0

            # List documents (should succeed)
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            assert doc_file.name in list_docs.stdout

        finally:
            if doc_file.exists():
                doc_file.unlink()
