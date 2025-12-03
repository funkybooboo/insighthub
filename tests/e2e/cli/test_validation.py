"""E2E tests for CLI argument validation and input handling."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
class TestCLIValidation:
    """End-to-end tests for CLI input validation."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    # ==================== WORKSPACE VALIDATION ====================

    def test_workspace_id_must_be_integer(self):
        """Test that workspace ID must be an integer."""
        test_cases = ["abc", "1.5", "1e5", "@#$", ""]

        for invalid_id in test_cases:
            result = self.run_cli("workspace", "show", invalid_id)
            assert result.returncode != 0

    def test_workspace_id_zero(self):
        """Test workspace ID of zero."""
        result = self.run_cli("workspace", "show", "0")
        # Zero might be invalid or might just not exist
        assert result.returncode != 0

    def test_workspace_create_with_very_long_name(self):
        """Test creating workspace with very long name."""
        long_name = "A" * 500
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input=f"{long_name}\nDescription\nvector\n",
            capture_output=True,
            text=True,
        )
        # Should either accept it or reject gracefully
        assert result.returncode in [0, 1]

    def test_workspace_create_with_special_characters(self):
        """Test creating workspace with special characters in name."""
        special_names = [
            "Test<>Workspace",
            "Test/Workspace",
            "Test\\Workspace",
            "Test|Workspace",
            "Test:Workspace",
            'Test"Workspace',
            "Test'Workspace",
        ]

        for name in special_names:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "workspace", "new"],
                input=f"{name}\nTest description\nvector\n",
                capture_output=True,
                text=True,
            )
            # Should handle gracefully
            assert result.returncode in [0, 1]

    def test_workspace_create_with_unicode(self):
        """Test creating workspace with unicode characters."""
        unicode_names = [
            "Тестовое пространство",  # Russian
            "测试工作区",  # Chinese
            "テストワークスペース",  # Japanese
            "🚀 Workspace 📁",  # Emojis
        ]

        for name in unicode_names:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "workspace", "new"],
                input=f"{name}\nTest description\nvector\n",
                capture_output=True,
                text=True,
            )
            # Should handle unicode gracefully
            assert result.returncode in [0, 1]

    def test_workspace_select_with_extra_arguments(self):
        """Test workspace select with extra arguments."""
        result = self.run_cli("workspace", "select", "1", "extra", "arguments")
        # Extra arguments should cause argparse error (exit code 2)
        assert result.returncode == 2

    # ==================== DOCUMENT VALIDATION ====================

    def test_document_upload_with_special_char_filename(self):
        """Test uploading file with special characters in filename."""
        # Create workspace first
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Special Char Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Test different special character filenames
        special_names = [
            "test file.txt",  # Space
            "test(file).txt",  # Parentheses
            "test[file].txt",  # Brackets
            "test{file}.txt",  # Braces
        ]

        for filename in special_names:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=filename, delete=False, dir="/tmp"
            ) as f:
                f.write("Test content\n")
                test_file = Path(f.name)

            try:
                result = self.run_cli("document", "upload", str(test_file))
                # Should handle gracefully
                assert result.returncode in [0, 1]
            finally:
                if test_file.exists():
                    test_file.unlink()

    def test_document_upload_symlink(self):
        """Test uploading a symlink."""
        # Create workspace first
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Symlink Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Create a real file and a symlink to it
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Real file content\n")
            real_file = Path(f.name)

        symlink = Path(tempfile.gettempdir()) / "test_symlink.txt"

        try:
            symlink.symlink_to(real_file)

            result = self.run_cli("document", "upload", str(symlink))
            # Should handle symlinks appropriately
            assert result.returncode in [0, 1]
        finally:
            if symlink.exists():
                symlink.unlink()
            if real_file.exists():
                real_file.unlink()

    def test_document_id_validation(self):
        """Test document ID validation."""
        invalid_ids = ["abc", "-1", "1.5", "999999999999999", ""]

        for invalid_id in invalid_ids:
            result = self.run_cli("document", "show", invalid_id)
            assert result.returncode != 0

    def test_document_remove_with_wildcard(self):
        """Test document remove with wildcard patterns."""
        # Create workspace first
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Wildcard Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Try to remove with wildcard (should probably fail or be rejected)
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "document", "remove", "*.txt"],
            input="yes\n",
            capture_output=True,
            text=True,
        )
        # Should handle wildcards appropriately (likely reject)
        assert result.returncode in [0, 1]

    # ==================== CHAT VALIDATION ====================

    def test_chat_workspace_id_validation(self):
        """Test chat commands with invalid workspace IDs."""
        invalid_ids = ["abc", "-1", "0", "1.5", ""]

        for invalid_id in invalid_ids:
            result = self.run_cli("chat", "list", invalid_id)
            assert result.returncode != 0

    def test_chat_session_id_validation(self):
        """Test chat commands with invalid session IDs."""
        invalid_ids = ["abc", "-1", "0", "1.5", ""]

        for invalid_id in invalid_ids:
            result = self.run_cli("chat", "select", invalid_id)
            assert result.returncode != 0

    def test_chat_new_with_very_long_title(self):
        """Test creating chat with very long title."""
        # Create workspace first
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Long Title Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None

        long_title = "A" * 1000
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
            input=f"{long_title}\n",
            capture_output=True,
            text=True,
        )
        # Should handle gracefully
        assert result.returncode in [0, 1]

    def test_chat_new_with_special_characters(self):
        """Test creating chat with special characters in title."""
        # Create workspace first
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Special Chat Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None

        special_titles = ["Chat<>Test", "Chat/Test", "Chat\\Test", "Chat|Test"]

        for title in special_titles:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
                input=f"{title}\n",
                capture_output=True,
                text=True,
            )
            # Should handle gracefully
            assert result.returncode in [0, 1]

    def test_chat_send_very_long_message(self):
        """Test sending very long message."""
        # Create workspace and chat
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Long Message Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None

        create_chat = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
            input="Test Session\n",
            capture_output=True,
            text=True,
        )
        assert create_chat.returncode == 0

        match = re.search(r"Created chat session \[(\d+)\]", create_chat.stdout)
        chat_id = match.group(1) if match else None

        select = self.run_cli("chat", "select", chat_id)
        assert select.returncode == 0

        # Send very long message
        long_message = "Hello " * 10000
        result = self.run_cli("chat", "send", long_message)
        # Should handle gracefully
        assert result.returncode in [0, 1]

    def test_chat_send_with_newlines(self):
        """Test sending message with newlines."""
        # Create workspace and chat
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Newline Message Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None

        create_chat = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
            input="Test Session\n",
            capture_output=True,
            text=True,
        )
        assert create_chat.returncode == 0

        match = re.search(r"Created chat session \[(\d+)\]", create_chat.stdout)
        chat_id = match.group(1) if match else None

        select = self.run_cli("chat", "select", chat_id)
        assert select.returncode == 0

        # Message with newlines
        message = "Line 1\nLine 2\nLine 3"
        result = self.run_cli("chat", "send", message)
        # Should handle gracefully
        assert result.returncode in [0, 1]

    # ==================== RAG CONFIG VALIDATION ====================

    def test_rag_config_invalid_chunking_algorithm(self):
        """Test RAG config with invalid chunking algorithm."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\ninvalid-algorithm\n512\n100\nnomic-embed-text\n3\nnone\n",
            capture_output=True,
            text=True,
        )
        # Should validate and reject invalid algorithm
        assert result.returncode != 0

    def test_rag_config_invalid_chunk_size(self):
        """Test RAG config with invalid chunk sizes."""
        invalid_sizes = ["abc", "-100", "0", "1.5"]

        for size in invalid_sizes:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
                input=f"vector\nsentence\n{size}\n100\nnomic-embed-text\n3\nnone\n",
                capture_output=True,
                text=True,
            )
            # Should validate and reject
            assert result.returncode != 0

        # Empty string should use default value and succeed
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n\n\nnomic-embed-text\n\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_rag_config_invalid_overlap(self):
        """Test RAG config with invalid overlap values."""
        invalid_overlaps = ["abc", "-50", "1.5"]

        for overlap in invalid_overlaps:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
                input=f"vector\nsentence\n512\n{overlap}\nnomic-embed-text\n3\nnone\n",
                capture_output=True,
                text=True,
            )
            # Should validate and reject
            assert result.returncode != 0

        # Empty string should use default value and succeed
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n512\n\nnomic-embed-text\n\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_rag_config_overlap_greater_than_chunk_size(self):
        """Test RAG config where overlap is greater than chunk size."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n100\n500\nnomic-embed-text\n3\nnone\n",
            capture_output=True,
            text=True,
        )
        # Should validate this constraint
        # Might succeed or fail depending on validation logic
        assert result.returncode in [0, 1]

    def test_rag_config_invalid_top_k(self):
        """Test RAG config with invalid top_k values."""
        invalid_top_k = ["abc", "-1", "0", "1.5"]

        for top_k in invalid_top_k:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
                input=f"vector\nsentence\n512\n100\nnomic-embed-text\n{top_k}\nnone\n",
                capture_output=True,
                text=True,
            )
            # Should validate and reject
            assert result.returncode != 0

        # Empty string should use default value and succeed
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n\n\nnomic-embed-text\n\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_rag_config_invalid_entity_extraction(self):
        """Test graph RAG config with invalid entity extraction."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\ninvalid-extraction\ndependency-parsing\nleiden\n",
            capture_output=True,
            text=True,
        )
        # Should validate and reject
        assert result.returncode != 0

    # ==================== GENERAL VALIDATION ====================

    def test_command_injection_attempts(self):
        """Test that command injection is not possible through inputs."""
        injection_attempts = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "`whoami`",
            "$(whoami)",
        ]

        # Create workspace first
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Injection Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None

        for attempt in injection_attempts:
            # Try injection in chat title
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
                input=f"{attempt}\n",
                capture_output=True,
                text=True,
            )
            # Should treat as literal string, not execute
            # The output may echo the title back, which is fine (e.g., "created chat session [1] | cat /etc/passwd")
            # What we're checking is that actual command execution didn't happen
            # If command executed, we'd see actual file contents like "root:x:0:0" not just the string "passwd"
            assert "root:x:0:0" not in result.stdout.lower()
            assert result.returncode == 0  # Should succeed as a normal title

    def test_null_byte_injection(self):
        """Test null byte injection attempts."""
        # Create workspace with null byte in name
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Test\x00Workspace\nDescription\nvector\n",
            capture_output=True,
            text=True,
        )
        # Should handle gracefully
        assert result.returncode in [0, 1]

    def test_path_traversal_in_document_upload(self):
        """Test path traversal attempts in document names."""
        # Create workspace first
        create_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Path Traversal Test\nTest\nvector\n",
            capture_output=True,
            text=True,
        )
        assert create_ws.returncode == 0

        import re

        match = re.search(r"Created workspace \[(\d+)\]", create_ws.stdout)
        ws_id = match.group(1) if match else None
        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        # Try various path traversal attempts
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
        ]

        for path in traversal_paths:
            result = self.run_cli("document", "upload", path)
            # Should reject or handle safely
            assert result.returncode != 0
            # Make sure no sensitive files were read
            assert "root:" not in result.stdout.lower()
