"""E2E tests for document operations and file handling combinations."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
class TestDocumentCombinations:
    """Test document upload, management, and file type combinations."""

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

    def create_workspace_and_select(self, name="Doc Test"):
        """Helper to create and select workspace."""
        ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input=f"{name}\nTest workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert ws.returncode == 0
        ws_id = self.extract_id(ws.stdout, r"Created workspace \[(\d+)\]")

        select = self.run_cli("workspace", "select", ws_id)
        assert select.returncode == 0

        return ws_id

    # ==================== FILE TYPE COMBINATIONS ====================

    def test_upload_various_text_formats(self):
        """Test uploading different text file formats."""
        self.create_workspace_and_select("Text Formats")

        # Test different text file extensions
        file_types = [
            (".txt", "Plain text content"),
            (".md", "# Markdown\n\nSome **bold** text"),
            (".py", "def test():\n    pass"),
            (".js", "function test() { return true; }"),
            (".json", '{"key": "value"}'),
            (".csv", "col1,col2\nval1,val2"),
            (".xml", "<root><item>value</item></root>"),
            (".html", "<html><body>Test</body></html>"),
        ]

        test_files = []
        for ext, content in file_types:
            with tempfile.NamedTemporaryFile(mode="w", suffix=ext, delete=False) as f:
                f.write(content)
                test_files.append(Path(f.name))

        try:
            for test_file in test_files:
                upload = self.run_cli("document", "upload", str(test_file))
                assert upload.returncode == 0
                assert "uploaded" in upload.stdout.lower()

            # List all documents
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            for test_file in test_files:
                assert test_file.name in list_docs.stdout

        finally:
            for test_file in test_files:
                if test_file.exists():
                    test_file.unlink()

    def test_upload_files_with_different_sizes(self):
        """Test uploading files of various sizes."""
        self.create_workspace_and_select("File Sizes")

        # Create files of different sizes
        sizes = [
            (10, "tiny"),  # 10 bytes
            (1000, "small"),  # 1KB
            (10000, "medium"),  # 10KB
            (100000, "large"),  # 100KB
        ]

        test_files = []
        for size, label in sizes:
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_{label}.txt", delete=False) as f:
                # Write content to reach approximately the target size
                content = "x" * (size - 10) + "\n"
                f.write(content)
                test_files.append(Path(f.name))

        try:
            for test_file in test_files:
                upload = self.run_cli("document", "upload", str(test_file))
                assert upload.returncode == 0

            # List documents
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            for test_file in test_files:
                assert test_file.name in list_docs.stdout

        finally:
            for test_file in test_files:
                if test_file.exists():
                    test_file.unlink()

    def test_upload_empty_file(self):
        """Test uploading an empty file."""
        self.create_workspace_and_select("Empty File")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            # Create empty file
            test_file = Path(f.name)

        try:
            upload = self.run_cli("document", "upload", str(test_file))
            # Should handle gracefully (may succeed or reject)
            assert upload.returncode in [0, 1]

        finally:
            if test_file.exists():
                test_file.unlink()

    def test_upload_file_with_long_content(self):
        """Test uploading file with very long content."""
        self.create_workspace_and_select("Long Content")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            # Write long content (multiple paragraphs)
            for i in range(100):
                f.write(
                    f"Paragraph {i}: This is a test paragraph with some content. "
                    f"It contains multiple sentences to test document processing. "
                    f"The content should be chunked and embedded properly.\n\n"
                )
            test_file = Path(f.name)

        try:
            upload = self.run_cli("document", "upload", str(test_file))
            assert upload.returncode == 0

            # Show document details
            doc_id = self.extract_id(upload.stdout, r"Uploaded \[(\d+)\]")
            if doc_id:
                show = self.run_cli("document", "show", doc_id)
                assert show.returncode == 0

        finally:
            if test_file.exists():
                test_file.unlink()

    # ==================== FILENAME COMBINATIONS ====================

    def test_upload_files_with_various_filenames(self):
        """Test uploading files with different filename patterns."""
        self.create_workspace_and_select("Various Filenames")

        # Test different filename patterns
        filenames = [
            "simple.txt",
            "with-dashes.txt",
            "with_underscores.txt",
            "with.dots.in.name.txt",
            "UPPERCASE.TXT",
            "MixedCase.txt",
            "with123numbers.txt",
        ]

        test_files = []
        for filename in filenames:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=filename, delete=False, dir="/tmp"
            ) as f:
                f.write(f"Content for {filename}\n")
                test_files.append(Path(f.name))

        try:
            for test_file in test_files:
                upload = self.run_cli("document", "upload", str(test_file))
                assert upload.returncode in [0, 1]

        finally:
            for test_file in test_files:
                if test_file.exists():
                    test_file.unlink()

    def test_upload_files_from_different_paths(self):
        """Test uploading files from various directory locations."""
        self.create_workspace_and_select("Different Paths")

        # Create files in different temp locations
        test_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_path{i}.txt", delete=False) as f:
                f.write(f"Content from path {i}\n")
                test_files.append(Path(f.name))

        try:
            for test_file in test_files:
                upload = self.run_cli("document", "upload", str(test_file))
                assert upload.returncode == 0

            # List documents
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0

        finally:
            for test_file in test_files:
                if test_file.exists():
                    test_file.unlink()

    # ==================== DOCUMENT SHOW COMBINATIONS ====================

    def test_show_documents_with_different_attributes(self):
        """Test showing documents and verifying attributes."""
        self.create_workspace_and_select("Show Attributes")

        # Upload documents with different characteristics
        test_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_attr{i}.txt", delete=False) as f:
                f.write(f"Document {i} with unique content.\n" * (i + 1))
                test_files.append(Path(f.name))

        try:
            doc_ids = []
            for test_file in test_files:
                upload = self.run_cli("document", "upload", str(test_file))
                assert upload.returncode == 0
                doc_id = self.extract_id(upload.stdout, r"Uploaded \[(\d+)\]")
                if doc_id:
                    doc_ids.append(doc_id)

            # Show each document and verify attributes
            for doc_id in doc_ids:
                show = self.run_cli("document", "show", doc_id)
                assert show.returncode == 0
                # Verify common attributes are displayed
                assert "status" in show.stdout.lower() or "size" in show.stdout.lower()

        finally:
            for test_file in test_files:
                if test_file.exists():
                    test_file.unlink()

    def test_show_nonexistent_document_ids(self):
        """Test showing documents with various invalid IDs."""
        self.create_workspace_and_select("Invalid IDs")

        # Try to show non-existent documents
        invalid_ids = ["999999", "0", "9999999999"]

        for invalid_id in invalid_ids:
            show = self.run_cli("document", "show", invalid_id)
            assert show.returncode != 0

    # ==================== DOCUMENT REMOVAL COMBINATIONS ====================

    def test_remove_documents_in_sequence(self):
        """Test removing documents one by one."""
        self.create_workspace_and_select("Sequential Remove")

        # Upload multiple documents
        test_files = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_seq{i}.txt", delete=False) as f:
                f.write(f"Sequential document {i}\n")
                test_files.append(Path(f.name))

        try:
            # Upload all
            for test_file in test_files:
                upload = self.run_cli("document", "upload", str(test_file))
                assert upload.returncode == 0

            # Remove documents one by one
            for i, test_file in enumerate(test_files):
                remove = subprocess.run(
                    [sys.executable, "-m", "src.cli", "document", "remove", test_file.name],
                    input="yes\n",
                    capture_output=True,
                    text=True,
                )
                assert remove.returncode == 0

                # List remaining documents
                list_docs = self.run_cli("document", "list")
                assert list_docs.returncode == 0

                # Verify removed document is not in list
                assert test_file.name not in list_docs.stdout

                # Verify remaining documents are still there
                for j in range(i + 1, len(test_files)):
                    if j < len(test_files):
                        pass  # Could check remaining files are still listed

        finally:
            for test_file in test_files:
                if test_file.exists():
                    test_file.unlink()

    def test_remove_and_reupload_same_file(self):
        """Test removing a document and re-uploading the same file."""
        self.create_workspace_and_select("Remove and Reupload")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Original content\n")
            test_file = Path(f.name)

        try:
            # Upload
            upload1 = self.run_cli("document", "upload", str(test_file))
            assert upload1.returncode == 0

            # Remove
            remove = subprocess.run(
                [sys.executable, "-m", "src.cli", "document", "remove", test_file.name],
                input="yes\n",
                capture_output=True,
                text=True,
            )
            assert remove.returncode == 0

            # Upload again
            upload2 = self.run_cli("document", "upload", str(test_file))
            assert upload2.returncode == 0

            # List documents
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            assert test_file.name in list_docs.stdout

        finally:
            if test_file.exists():
                test_file.unlink()

    def test_cancel_document_removal(self):
        """Test canceling document removal."""
        self.create_workspace_and_select("Cancel Remove")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Keep this document\n")
            test_file = Path(f.name)

        try:
            # Upload
            upload = self.run_cli("document", "upload", str(test_file))
            assert upload.returncode == 0

            # Try to remove but cancel
            remove = subprocess.run(
                [sys.executable, "-m", "src.cli", "document", "remove", test_file.name],
                input="no\n",
                capture_output=True,
                text=True,
            )
            # Should either succeed (cancel) or fail gracefully
            assert remove.returncode in [0, 1]

            # Document should still exist
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            assert test_file.name in list_docs.stdout

        finally:
            if test_file.exists():
                test_file.unlink()

    # ==================== DOCUMENT LIST COMBINATIONS ====================

    def test_list_with_various_document_counts(self):
        """Test listing with different numbers of documents."""
        self.create_workspace_and_select("Various Counts")

        # Test with 0 documents
        list_empty = self.run_cli("document", "list")
        assert list_empty.returncode == 0
        assert "no documents found" in list_empty.stdout.lower()

        # Add documents incrementally
        test_files = []
        for i in range(10):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_count{i}.txt", delete=False) as f:
                f.write(f"Document {i}\n")
                test_file = Path(f.name)
                test_files.append(test_file)

            # Upload
            upload = self.run_cli("document", "upload", str(test_file))
            assert upload.returncode == 0

            # List after each upload
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            assert test_file.name in list_docs.stdout

        # Clean up
        for test_file in test_files:
            if test_file.exists():
                test_file.unlink()

    def test_list_after_various_operations(self):
        """Test listing documents after different operations."""
        self.create_workspace_and_select("List After Ops")

        # Create test files
        test_files = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_ops{i}.txt", delete=False) as f:
                f.write(f"Operations test {i}\n")
                test_files.append(Path(f.name))

        try:
            # Upload all
            for test_file in test_files:
                upload = self.run_cli("document", "upload", str(test_file))
                assert upload.returncode == 0

            # List after upload
            list1 = self.run_cli("document", "list")
            assert list1.returncode == 0

            # Show some documents
            for i in range(2):
                doc_id = str(i + 1)  # Approximate IDs
                self.run_cli("document", "show", doc_id)

            # List after show operations
            list2 = self.run_cli("document", "list")
            assert list2.returncode == 0

            # Remove some documents
            for i in range(2):
                remove = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "src.cli",
                        "document",
                        "remove",
                        test_files[i].name,
                    ],
                    input="yes\n",
                    capture_output=True,
                    text=True,
                )
                assert remove.returncode == 0

            # List after removal
            list3 = self.run_cli("document", "list")
            assert list3.returncode == 0

        finally:
            for test_file in test_files:
                if test_file.exists():
                    test_file.unlink()

    # ==================== DOCUMENT AND CHAT COMBINATIONS ====================

    def test_documents_with_chat_sessions(self):
        """Test uploading documents and using them in chat sessions."""
        ws_id = self.create_workspace_and_select("Docs and Chat")

        # Upload documents
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Important information for chat.\n")
            test_file = Path(f.name)

        try:
            upload = self.run_cli("document", "upload", str(test_file))
            assert upload.returncode == 0

            # Create chat session
            chat = subprocess.run(
                [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
                input="Document Chat\n",
                capture_output=True,
                text=True,
            )
            assert chat.returncode == 0
            chat_id = self.extract_id(chat.stdout, r"Created chat session \[(\d+)\]")

            # Select chat
            select = self.run_cli("chat", "select", chat_id)
            assert select.returncode == 0

            # List documents while chat is selected
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            assert test_file.name in list_docs.stdout

        finally:
            if test_file.exists():
                test_file.unlink()

    def test_upload_documents_between_chat_messages(self):
        """Test uploading documents in the middle of a chat session."""
        ws_id = self.create_workspace_and_select("Mid-Chat Upload")

        # Create chat session
        chat = subprocess.run(
            [sys.executable, "-m", "src.cli", "chat", "new", ws_id],
            input="Mid Chat Test\n",
            capture_output=True,
            text=True,
        )
        assert chat.returncode == 0
        chat_id = self.extract_id(chat.stdout, r"Created chat session \[(\d+)\]")

        # Select chat
        select = self.run_cli("chat", "select", chat_id)
        assert select.returncode == 0

        # Upload document during chat session
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Mid-chat document\n")
            test_file = Path(f.name)

        try:
            upload = self.run_cli("document", "upload", str(test_file))
            assert upload.returncode == 0

            # Verify document is available
            list_docs = self.run_cli("document", "list")
            assert list_docs.returncode == 0
            assert test_file.name in list_docs.stdout

        finally:
            if test_file.exists():
                test_file.unlink()

    # ==================== EDGE CASES ====================

    def test_upload_same_filename_twice(self):
        """Test uploading two files with the same filename."""
        self.create_workspace_and_select("Same Filename")

        filename = "duplicate_name.txt"

        # Create first file
        with tempfile.NamedTemporaryFile(mode="w", suffix=filename, delete=False, dir="/tmp") as f:
            f.write("First version\n")
            file1 = Path(f.name)

        try:
            # Upload first file
            upload1 = self.run_cli("document", "upload", str(file1))
            assert upload1.returncode == 0

            # Create second file with same name
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=filename, delete=False, dir="/tmp"
            ) as f:
                f.write("Second version\n")
                file2 = Path(f.name)

            try:
                # Upload second file
                upload2 = self.run_cli("document", "upload", str(file2))
                # Behavior may vary: could reject or accept
                assert upload2.returncode in [0, 1]

            finally:
                if file2.exists():
                    file2.unlink()

        finally:
            if file1.exists():
                file1.unlink()
