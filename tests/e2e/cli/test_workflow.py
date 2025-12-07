"""E2E tests for CLI workflow - testing multiple commands together."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
class TestCLIWorkflow:
    """End-to-end tests for complete CLI workflows."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    def extract_id(self, output, pattern, group_name=None):
        """Extract ID from command output using regex pattern."""
        import re

        match = re.search(pattern, output)
        if match:
            return match.group(1) if not group_name else match.group(group_name)
        return None

    def test_complete_workspace_document_workflow(self):
        """Test complete workflow: create workspace, upload docs, list, remove."""
        # Create workspace
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Workflow Test\nComplete workflow test\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_id = self.extract_id(create_ws.stdout, r"Created workspace \[(\d+)\]")
        assert ws_id is not None

        # Select workspace
        select_ws = self.run_cli("workspace", "select", ws_id)
        assert select_ws.returncode == 0

        # Create test documents
        docs = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_test_{i}.txt", delete=False) as f:
                f.write(f"Test document {i} content.\n")
                docs.append(Path(f.name))

        try:
            # Upload all documents
            for doc in docs:
                upload = self.run_cli("document", "upload", str(doc))
                assert upload.returncode == 0
                assert "uploaded" in upload.stdout.lower()

            # List documents - should show all 3
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            for doc in docs:
                assert doc.name in list_docs.stdout

            # Remove one document
            remove = subprocess.run(
                [sys.executable, "-m", "src.cli", "document", "remove", docs[0].name],
                input="yes\n",
                capture_output=True,
                text=True,
            )
            assert remove.returncode == 0

            # List again - should show 2
            list_after = self.run_cli("document", "list")
            assert list_after.returncode == 0
            assert docs[0].name not in list_after.stdout
            assert docs[1].name in list_after.stdout
            assert docs[2].name in list_after.stdout

            # Show workspace details
            show_ws = self.run_cli("workspace", "show", ws_id)
            assert show_ws.returncode == 0
            assert "Workflow Test" in show_ws.stdout

        finally:
            for doc in docs:
                if doc.exists():
                    doc.unlink()

    def test_complete_workspace_chat_workflow(self):
        """Test complete workflow: create workspace, create chat sessions, send messages."""
        # Create workspace
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Chat Workflow\nChat workflow test\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_id = self.extract_id(create_ws.stdout, r"Created workspace \[(\d+)\]")
        assert ws_id is not None

        # Create first chat session
        chat1 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
            input="First Session\n",
            capture_output=True,
            text=True,
        )
        assert chat1.returncode == 0
        chat1_id = self.extract_id(chat1.stdout, r"Created chat session \[(\d+)\]")
        assert chat1_id is not None

        # Create second chat session
        chat2 = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "create", ws_id],
            input="Second Session\n",
            capture_output=True,
            text=True,
        )
        assert chat2.returncode == 0
        chat2_id = self.extract_id(chat2.stdout, r"Created chat session \[(\d+)\]")
        assert chat2_id is not None

        # List chat sessions
        list_chats = self.run_cli("chat", "list", ws_id)
        assert list_chats.returncode == 0
        assert "First Session" in list_chats.stdout
        assert "Second Session" in list_chats.stdout

        # Select first session
        select_chat = self.run_cli("chat", "select", chat1_id)
        assert select_chat.returncode == 0

        # Check history (should be empty)
        history1 = self.run_cli("chat", "history")
        assert history1.returncode == 0
        assert "no messages" in history1.stdout.lower()

        # Delete second session
        delete_chat = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "delete", chat2_id],
            input="yes\n",
            capture_output=True,
            text=True,
        )
        assert delete_chat.returncode == 0

        # List again - should only show first session
        list_after = self.run_cli("chat", "list", ws_id)
        assert list_after.returncode == 0
        assert "First Session" in list_after.stdout
        assert "Second Session" not in list_after.stdout

    def test_workspace_rag_config_workflow(self):
        """Test workflow: set default RAG config, create workspace with it."""
        # Set default vector RAG config
        set_config = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "create"],
            input="vector\nsentence\n800\n150\nnomic-embed-text\n3\nnone\n",
            capture_output=True,
            text=True,
        )
        assert set_config.returncode == 0

        # Verify config was saved
        show_config = self.run_cli("default-rag-config", "show")
        assert show_config.returncode == 0
        assert "vector" in show_config.stdout.lower()
        assert "800" in show_config.stdout

        # Create workspace (should use default config)
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="RAG Config Test\nRAG config workflow\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_id = self.extract_id(create_ws.stdout, r"Created workspace \[(\d+)\]")
        assert ws_id is not None

        # Show workspace and verify RAG config
        show_ws = self.run_cli("workspace", "show", ws_id)
        assert show_ws.returncode == 0
        assert "RAG Config Test" in show_ws.stdout

    def test_multiple_workspace_switching_workflow(self):
        """Test workflow: create multiple workspaces and switch between them."""
        workspace_ids = []

        # Create 3 workspaces
        for i in range(3):
            create = subprocess.run(
                [sys.executable, "-m", "src.cli", "workspace", "create"],
                input=f"Workspace {i}\nDescription {i}\nvector\n",
                capture_output=True,
                text=True,
            )
            assert create.returncode == 0
            ws_id = self.extract_id(create.stdout, r"Created workspace \[(\d+)\]")
            assert ws_id is not None
            workspace_ids.append(ws_id)

        # Select each workspace and verify
        for ws_id in workspace_ids:
            select = self.run_cli("workspace", "select", ws_id)
            assert select.returncode == 0
            assert "selected" in select.stdout.lower()

        # List workspaces - should show all 3
        list_ws = self.run_cli("workspace", "list")
        assert list_ws.returncode == 0
        for i in range(3):
            assert f"Workspace {i}" in list_ws.stdout

    def test_document_upload_with_different_types(self):
        """Test uploading different document types."""
        # Create workspace
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Multi-type Docs\nMultiple document types\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_id = self.extract_id(create_ws.stdout, r"Created workspace \[(\d+)\]")
        assert ws_id is not None

        # Select workspace
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Create different file types
        test_files = []

        # Text file
        txt_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        txt_file.write("Plain text content.\n")
        txt_file.close()
        test_files.append(Path(txt_file.name))

        # Markdown file
        md_file = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
        md_file.write("# Markdown\n\nSome **bold** text.\n")
        md_file.close()
        test_files.append(Path(md_file.name))

        # Python file
        py_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
        py_file.write("def test():\n    pass\n")
        py_file.close()
        test_files.append(Path(py_file.name))

        try:
            # Upload all files
            for file in test_files:
                upload = self.run_cli("document", "upload", str(file))
                assert upload.returncode == 0
                assert "uploaded" in upload.stdout.lower()

            # List documents - should show all
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            for file in test_files:
                assert file.name in list_docs.stdout

        finally:
            for file in test_files:
                if file.exists():
                    file.unlink()

    def test_workspace_update_workflow(self):
        """Test creating, updating, and verifying workspace changes."""
        # Create workspace
        create = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Original Name\nOriginal description\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create.returncode == 0
        ws_id = self.extract_id(create.stdout, r"Created workspace \[(\d+)\]")
        assert ws_id is not None

        # Show original details
        show1 = self.run_cli("workspace", "show", ws_id)
        assert show1.returncode == 0
        assert "Original Name" in show1.stdout
        assert "Original description" in show1.stdout

        # Update workspace
        update = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "update", ws_id],
            input="Updated Name\nUpdated description\n",
            capture_output=True,
            text=True,
        )
        assert update.returncode == 0

        # Show updated details
        show2 = self.run_cli("workspace", "show", ws_id)
        assert show2.returncode == 0
        assert "Updated Name" in show2.stdout
        assert "Updated description" in show2.stdout
        assert "Original Name" not in show2.stdout

    def test_document_show_after_upload(self):
        """Test viewing document details after upload."""
        # Create and select workspace
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "create"],
            input="Doc Show Test\nTest document show\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0
        ws_id = self.extract_id(create_ws.stdout, r"Created workspace \[(\d+)\]")

        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Create test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content for document show.\n")
            test_file = Path(f.name)

        try:
            # Upload document
            upload = self.run_cli("document", "upload", str(test_file))
            assert upload.returncode == 0

            doc_id = self.extract_id(upload.stdout, r"Uploaded \[(\d+)\]")
            assert doc_id is not None

            # Show document details
            show_doc = self.run_cli("document", "show", doc_id)
            assert show_doc.returncode == 0
            assert test_file.name in show_doc.stdout

        finally:
            if test_file.exists():
                test_file.unlink()
