"""E2E tests for concurrent CLI operations."""

import subprocess
import sys
import tempfile
import threading
from pathlib import Path

import pytest


@pytest.mark.integration
@pytest.mark.slow
class TestCLIConcurrency:
    """End-to-end tests for concurrent CLI operations."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    def run_cli_with_input(self, args, input_text):
        """Helper to run CLI command with input and return result."""
        cmd = [sys.executable, "-m", "src.cli"] + list(args)
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
        )
        return result

    def test_concurrent_workspace_creation(self):
        """Test creating multiple workspaces concurrently."""
        results = []
        threads = []

        def create_workspace(index):
            result = self.run_cli_with_input(
                ["workspace", "new"], f"Concurrent WS {index}\nDescription {index}\nvector\n"
            )
            results.append((index, result))

        # Create 5 workspaces concurrently
        for i in range(5):
            thread = threading.Thread(target=create_workspace, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All should succeed
        for index, result in results:
            assert result.returncode == 0, f"Workspace {index} creation failed"
            assert "created workspace" in result.stdout.lower()

    def test_concurrent_document_uploads(self):
        """Test uploading multiple documents concurrently to same workspace."""
        # Create workspace first
        create_ws = self.run_cli_with_input(
            ["workspace", "new"], "Concurrent Docs\nConcurrent upload test\nvector\n"
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        assert ws_id is not None

        # Select workspace
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Create test files
        test_files = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=f"_concurrent_{i}.txt", delete=False
            ) as f:
                f.write(f"Concurrent document {i} content.\n")
                test_files.append(Path(f.name))

        results = []
        threads = []

        def upload_document(file_path, index):
            result = self.run_cli("document", "upload", str(file_path))
            results.append((index, result))

        try:
            # Upload all files concurrently
            for i, file_path in enumerate(test_files):
                thread = threading.Thread(target=upload_document, args=(file_path, i))
                threads.append(thread)
                thread.start()

            # Wait for all uploads
            for thread in threads:
                thread.join()

            # All should succeed
            for index, result in results:
                assert result.returncode == 0, f"Document {index} upload failed: {result.stderr}"
                assert "uploaded" in result.stdout.lower()

            # Verify all documents are in the list
            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0
            for file_path in test_files:
                assert file_path.name in list_result.stdout

        finally:
            # Cleanup
            for file_path in test_files:
                if file_path.exists():
                    file_path.unlink()

    def test_concurrent_chat_session_creation(self):
        """Test creating multiple chat sessions concurrently in same workspace."""
        # Create workspace first
        create_ws = self.run_cli_with_input(
            ["workspace", "new"], "Concurrent Chats\nConcurrent chat test\nvector\n"
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        assert ws_id is not None

        results = []
        threads = []

        def create_chat(workspace_id, index):
            result = self.run_cli_with_input(
                ["chat", "new", workspace_id], f"Concurrent Chat {index}\n"
            )
            results.append((index, result))

        # Create 5 chat sessions concurrently
        for i in range(5):
            thread = threading.Thread(target=create_chat, args=(ws_id, i))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # All should succeed
        for index, result in results:
            assert result.returncode == 0, f"Chat {index} creation failed"
            assert "created chat session" in result.stdout.lower()

        # Verify all chats are listed
        list_result = self.run_cli("chat", "list", ws_id)
        assert list_result.returncode == 0
        for i in range(5):
            assert f"Concurrent Chat {i}" in list_result.stdout

    def test_concurrent_workspace_selection(self):
        """Test selecting different workspaces concurrently."""
        # Create multiple workspaces
        workspace_ids = []
        for i in range(3):
            create = self.run_cli_with_input(
                ["workspace", "new"], f"Select WS {i}\nDescription {i}\nvector\n"
            )
            assert create.returncode == 0

            import re

            match = re.search(r"Created workspace \[(\d+)\]", create.stdout)
            ws_id = match.group(1) if match else None
            assert ws_id is not None
            workspace_ids.append(ws_id)

        results = []
        threads = []

        def select_workspace(ws_id, index):
            result = self.run_cli("workspace", "select", ws_id)
            results.append((index, result))

        # Select workspaces concurrently
        for i, ws_id in enumerate(workspace_ids):
            thread = threading.Thread(target=select_workspace, args=(ws_id, i))
            threads.append(thread)
            thread.start()

        # Wait for all selections
        for thread in threads:
            thread.join()

        # All should succeed (last one wins)
        for index, result in results:
            assert result.returncode == 0, f"Workspace {index} selection failed"

    def test_concurrent_document_removal(self):
        """Test removing different documents concurrently."""
        # Create workspace and upload multiple documents
        create_ws = self.run_cli_with_input(
            ["workspace", "new"], "Concurrent Remove\nConcurrent removal test\nvector\n"
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Create and upload test files
        test_files = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=f"_remove_{i}.txt", delete=False
            ) as f:
                f.write(f"Document {i} content.\n")
                test_files.append(Path(f.name))

        # Upload all files
        for file_path in test_files:
            upload = self.run_cli("document", "upload", str(file_path))
            assert upload.returncode == 0

        results = []
        threads = []

        def remove_document(filename, index):
            result = self.run_cli_with_input(["document", "remove", filename], "yes\n")
            results.append((index, result))

        try:
            # Remove all documents concurrently
            for i, file_path in enumerate(test_files):
                thread = threading.Thread(target=remove_document, args=(file_path.name, i))
                threads.append(thread)
                thread.start()

            # Wait for all removals
            for thread in threads:
                thread.join()

            # All should succeed
            for index, result in results:
                assert result.returncode == 0, f"Document {index} removal failed: {result.stderr}"

            # Verify all documents are removed
            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0
            for file_path in test_files:
                assert file_path.name not in list_result.stdout

        finally:
            # Cleanup temp files
            for file_path in test_files:
                if file_path.exists():
                    file_path.unlink()

    def test_concurrent_read_operations(self):
        """Test concurrent read-only operations (list, show)."""
        # Create workspace with some data
        create_ws = self.run_cli_with_input(
            ["workspace", "new"], "Concurrent Reads\nConcurrent read test\nvector\n"
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None

        results = []
        threads = []

        def list_workspaces(index):
            result = self.run_cli("workspace", "list")
            results.append(("list", index, result))

        def show_workspace(workspace_id, index):
            result = self.run_cli("workspace", "show", workspace_id)
            results.append(("show", index, result))

        # Run multiple concurrent reads
        for i in range(10):
            if i % 2 == 0:
                thread = threading.Thread(target=list_workspaces, args=(i,))
            else:
                thread = threading.Thread(target=show_workspace, args=(ws_id, i))
            threads.append(thread)
            thread.start()

        # Wait for all reads
        for thread in threads:
            thread.join()

        # All should succeed
        for op_type, index, result in results:
            assert (
                result.returncode == 0
            ), f"Read operation {op_type} {index} failed: {result.stderr}"

    def test_concurrent_workspace_updates(self):
        """Test updating same workspace concurrently (race condition test)."""
        # Create workspace
        create = self.run_cli_with_input(
            ["workspace", "new"], "Update Test\nOriginal description\nvector\n"
        )
        assert create.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create.stdout)
        ws_id = match.group(1) if match else None
        assert ws_id is not None

        results = []
        threads = []

        def update_workspace(workspace_id, index):
            result = self.run_cli_with_input(
                ["workspace", "update", workspace_id],
                f"Updated Name {index}\nUpdated description {index}\n",
            )
            results.append((index, result))

        # Update same workspace concurrently
        for i in range(3):
            thread = threading.Thread(target=update_workspace, args=(ws_id, i))
            threads.append(thread)
            thread.start()

        # Wait for all updates
        for thread in threads:
            thread.join()

        # All should succeed (last write wins)
        success_count = sum(1 for _, result in results if result.returncode == 0)
        # At least one should succeed
        assert success_count >= 1

        # Verify workspace still exists and is valid
        show = self.run_cli("workspace", "show", ws_id)
        assert show.returncode == 0

    def test_concurrent_mixed_operations(self):
        """Test mixed read/write operations concurrently."""
        # Create workspace
        create_ws = self.run_cli_with_input(
            ["workspace", "new"], "Mixed Ops\nMixed operations test\nvector\n"
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Create test files
        test_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_mixed_{i}.txt", delete=False) as f:
                f.write(f"Mixed ops document {i}.\n")
                test_files.append(Path(f.name))

        results = []
        threads = []

        def upload_doc(file_path, index):
            result = self.run_cli("document", "upload", str(file_path))
            results.append(("upload", index, result))

        def list_docs(index):
            result = self.run_cli("document", "list")
            results.append(("list", index, result))

        def show_workspace(workspace_id, index):
            result = self.run_cli("workspace", "show", workspace_id)
            results.append(("show", index, result))

        try:
            # Mix of operations
            for i in range(3):
                # Upload
                thread = threading.Thread(target=upload_doc, args=(test_files[i], i))
                threads.append(thread)
                thread.start()

                # List
                thread = threading.Thread(target=list_docs, args=(i,))
                threads.append(thread)
                thread.start()

                # Show
                thread = threading.Thread(target=show_workspace, args=(ws_id, i))
                threads.append(thread)
                thread.start()

            # Wait for all operations
            for thread in threads:
                thread.join()

            # Check results - reads should all succeed
            for op_type, index, result in results:
                if op_type in ["list", "show"]:
                    assert result.returncode == 0, f"{op_type} operation {index} failed"

        finally:
            for file_path in test_files:
                if file_path.exists():
                    file_path.unlink()

    def test_concurrent_rag_config_updates(self):
        """Test updating default RAG config concurrently."""
        results = []
        threads = []

        def update_rag_config(index):
            chunk_size = 500 + (index * 100)
            result = self.run_cli_with_input(
                ["default-rag-config", "new"],
                f"vector\nsentence\n{chunk_size}\n100\nollama\n{3+index}\nnone\n",
            )
            results.append((index, result))

        # Update config concurrently
        for i in range(3):
            thread = threading.Thread(target=update_rag_config, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all updates
        for thread in threads:
            thread.join()

        # At least one should succeed (last write wins)
        success_count = sum(1 for _, result in results if result.returncode == 0)
        assert success_count >= 1

        # Verify config is still valid
        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
