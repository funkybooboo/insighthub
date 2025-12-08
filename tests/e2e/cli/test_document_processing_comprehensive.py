"""Comprehensive E2E tests for document processing workflows.

These tests verify:
- Different document formats (TXT, PDF if supported)
- Document parsing and content extraction
- Error handling for invalid documents
- Large document processing
- Special characters and encoding
"""

import re
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.mark.e2e
class TestDocumentProcessingComprehensive:
    """E2E tests for document processing workflows."""

    def run_cli(self, *args, input_text=None):
        """Helper to run CLI command and return result."""
        cmd = ["poetry", "run", "python", "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            input=input_text,
        )
        return result

    @pytest.fixture
    def workspace_id(self):
        """Create a workspace for document testing."""
        ws_result = self.run_cli(
            "workspace", "create", input_text="Doc Processing Test\n\nvector\n"
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None
        self.run_cli("workspace", "select", workspace_id)
        return workspace_id

    def test_upload_plain_text_document(self, workspace_id):
        """Test uploading a simple plain text document."""
        content = "This is a simple plain text document for testing."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            doc_path = f.name

        try:
            upload_result = self.run_cli("document", "add", doc_path)
            assert upload_result.returncode == 0
            assert "added" in upload_result.stdout.lower()

            # Verify document is listed
            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0
            assert Path(doc_path).name in list_result.stdout or "[" in list_result.stdout

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_upload_document_with_unicode_content(self, workspace_id):
        """Test uploading document with special characters and unicode."""
        content = """
        Testing unicode: café, naïve, 日本語, 中文, Ελληνικά
        Special characters: © ® ™ € £ ¥
        Emojis: 😀 🎉 🚀 💻
        Mathematical symbols: ∑ ∫ ∞ ≈ ≠
        """

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write(content)
            doc_path = f.name

        try:
            upload_result = self.run_cli("document", "add", doc_path)
            assert upload_result.returncode == 0
            assert "added" in upload_result.stdout.lower()

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_upload_very_large_document(self, workspace_id):
        """Test uploading a large document (several MB of text)."""
        # Generate ~1MB of text
        large_content = "This is a test sentence. " * 40000  # ~1MB

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(large_content)
            doc_path = f.name

        try:
            upload_result = self.run_cli("document", "add", doc_path)
            # Should handle large document
            assert upload_result.returncode == 0
            assert "added" in upload_result.stdout.lower()

            # Allow time for processing
            import time

            time.sleep(3)

            # Check document status
            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_upload_empty_document(self, workspace_id):
        """Test handling of empty document."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            # Write nothing
            f.write("")
            doc_path = f.name

        try:
            upload_result = self.run_cli("document", "add", doc_path)
            # Should either succeed with warning or fail gracefully
            assert upload_result.returncode in (0, 1)

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_upload_document_with_long_filename(self, workspace_id):
        """Test uploading document with very long filename."""
        content = "Test content for long filename."

        # Create filename at boundary of filesystem limits
        long_name = "a" * 200 + ".txt"  # Most filesystems support up to 255 chars

        with tempfile.NamedTemporaryFile(mode="w", suffix=long_name, delete=False) as f:
            f.write(content)
            doc_path = f.name

        try:
            upload_result = self.run_cli("document", "add", doc_path)
            # Should handle or reject gracefully
            assert upload_result.returncode in (0, 1)

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_upload_multiple_documents_same_content(self, workspace_id):
        """Test uploading multiple documents with identical content."""
        content = "This is duplicate content for testing."

        temp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_dup{i}.txt", delete=False) as f:
                f.write(content)
                temp_files.append(f.name)

        try:
            # Add all three
            for doc_path in temp_files:
                upload_result = self.run_cli("document", "add", doc_path)
                assert upload_result.returncode == 0

            # All should be listed as separate documents
            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0
            doc_count = list_result.stdout.count("[")
            assert doc_count >= 3, f"Expected at least 3 documents, found {doc_count}"

        finally:
            for doc_path in temp_files:
                Path(doc_path).unlink(missing_ok=True)

    def test_upload_document_with_special_filename_chars(self, workspace_id):
        """Test uploading document with special characters in filename."""
        content = "Test content with special filename."

        # Different special characters (some may not be allowed)
        special_names = [
            "test_with_underscores.txt",
            "test-with-dashes.txt",
            "test.multiple.dots.txt",
        ]

        for special_name in special_names:
            with tempfile.NamedTemporaryFile(mode="w", suffix=special_name, delete=False) as f:
                f.write(content)
                doc_path = f.name

            try:
                upload_result = self.run_cli("document", "add", doc_path)
                # Should succeed or fail gracefully
                assert upload_result.returncode in (0, 1)
            finally:
                Path(doc_path).unlink(missing_ok=True)

    def test_document_show_displays_metadata(self, workspace_id):
        """Test that document show command displays all relevant metadata."""
        content = "Test content for metadata display."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            doc_path = f.name

        try:
            upload_result = self.run_cli("document", "add", doc_path)
            assert upload_result.returncode == 0

            # Get document ID
            list_result = self.run_cli("document", "list")
            doc_id = None
            for line in list_result.stdout.split("\n"):
                if "[" in line and "]" in line:
                    try:
                        doc_id = line.split("[")[1].split("]")[0]
                        break
                    except Exception:
                        continue

            if doc_id:
                show_result = self.run_cli("document", "show", doc_id)
                assert show_result.returncode == 0

                output = show_result.stdout.lower()
                # Should show key metadata
                assert "filename" in output or "name" in output
                assert "size" in output or "bytes" in output
                assert "status" in output

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_remove_document_by_exact_filename(self, workspace_id):
        """Test removing document using exact filename match."""
        content = "Test document for removal."

        with tempfile.NamedTemporaryFile(mode="w", suffix="_removal_test.txt", delete=False) as f:
            f.write(content)
            doc_path = f.name

        filename = Path(doc_path).name

        try:
            # Upload
            upload_result = self.run_cli("document", "add", doc_path)
            assert upload_result.returncode == 0

            # Remove by filename
            remove_result = self.run_cli("document", "remove", filename, input_text="yes\n")
            assert remove_result.returncode == 0 or "deleted" in remove_result.stdout.lower()

            # Verify removed
            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0
            assert (
                filename not in list_result.stdout or "no documents" in list_result.stdout.lower()
            )

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_upload_and_remove_rapid_sequence(self, workspace_id):
        """Test rapidly uploading and removing documents."""
        for i in range(3):
            content = f"Rapid test document {i}"

            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_rapid{i}.txt", delete=False) as f:
                f.write(content)
                doc_path = f.name

            filename = Path(doc_path).name

            try:
                # Upload
                upload_result = self.run_cli("document", "add", doc_path)
                assert upload_result.returncode == 0

                # Immediately remove
                remove_result = self.run_cli("document", "remove", filename, input_text="yes\n")
                # Should handle rapid operations
                assert remove_result.returncode in (0, 1)

            finally:
                Path(doc_path).unlink(missing_ok=True)

    def test_document_list_empty_workspace(self, workspace_id):
        """Test listing documents in empty workspace."""
        list_result = self.run_cli("document", "list")
        assert list_result.returncode == 0
        assert (
            "no documents" in list_result.stdout.lower()
            or len(list_result.stdout.strip()) == 0
            or "found" in list_result.stdout.lower()
        )

    def test_document_list_after_multiple_uploads(self, workspace_id):
        """Test document list after uploading multiple documents."""
        temp_files = []

        for i in range(5):
            content = f"Document {i} content for listing test."
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_list{i}.txt", delete=False) as f:
                f.write(content)
                temp_files.append(f.name)

        try:
            # Add all
            for doc_path in temp_files:
                upload_result = self.run_cli("document", "add", doc_path)
                assert upload_result.returncode == 0

            # List should show all
            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0

            # Count documents in output
            doc_count = list_result.stdout.count("[")
            assert doc_count >= 5, f"Expected at least 5 documents, found {doc_count}"

        finally:
            for doc_path in temp_files:
                Path(doc_path).unlink(missing_ok=True)

    def test_document_with_multiple_line_breaks(self, workspace_id):
        """Test document with excessive newlines and whitespace."""
        content = "Line 1\n\n\n\nLine 2\n\n\n\n\n\nLine 3\n" + "\n" * 20 + "Line 4"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            doc_path = f.name

        try:
            upload_result = self.run_cli("document", "add", doc_path)
            assert upload_result.returncode == 0
            assert "added" in upload_result.stdout.lower()

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_document_with_mixed_content_types(self, workspace_id):
        """Test document with code, URLs, and mixed content."""
        content = """
        This document contains mixed content types:

        Some code:
        def hello_world():
            print("Hello, World!")

        A URL: https://www.example.com/path/to/resource

        An email: test@example.com

        Some numbers: 123456789, 3.14159

        Mixed case: ThIs Is MiXeD CaSe TeXt
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            doc_path = f.name

        try:
            upload_result = self.run_cli("document", "add", doc_path)
            assert upload_result.returncode == 0
            assert "added" in upload_result.stdout.lower()

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_cancel_document_removal(self, workspace_id):
        """Test canceling document removal confirmation."""
        content = "Document that won't be removed."

        with tempfile.NamedTemporaryFile(mode="w", suffix="_cancel.txt", delete=False) as f:
            f.write(content)
            doc_path = f.name

        filename = Path(doc_path).name

        try:
            # Upload
            upload_result = self.run_cli("document", "add", doc_path)
            assert upload_result.returncode == 0

            # Try to remove but cancel
            remove_result = self.run_cli("document", "remove", filename, input_text="no\n")

            # Should be cancelled
            assert "cancel" in remove_result.stdout.lower() or remove_result.returncode != 0

            # Document should still exist
            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0
            assert filename in list_result.stdout or "[" in list_result.stdout

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_document_processing_in_graph_workspace(self):
        """Test document processing specifically in graph workspace."""
        # Create graph workspace
        ws_result = self.run_cli("workspace", "create", input_text="Graph Doc Test\n\ngraph\n")
        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        self.run_cli("workspace", "select", workspace_id)

        # Add entity-rich document
        content = """
        John Smith works at Microsoft in Seattle.
        Jane Doe is employed by Google in Mountain View.
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            doc_path = f.name

        try:
            upload_result = self.run_cli("document", "add", doc_path)
            assert upload_result.returncode == 0
            assert "added" in upload_result.stdout.lower()

            # Graph processing should complete
            import time

            time.sleep(2)

            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0

        finally:
            Path(doc_path).unlink(missing_ok=True)
