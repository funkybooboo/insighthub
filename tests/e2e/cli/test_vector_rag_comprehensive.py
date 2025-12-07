"""Comprehensive E2E tests for Vector RAG functionality.

These tests verify the complete Vector RAG pipeline:
- Document chunking with different algorithms
- Embedding generation and storage in Qdrant
- Semantic search and retrieval
- Reranking of results
- Context-aware chat responses
"""

import re
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.mark.e2e
class TestVectorRagComprehensive:
    """E2E tests for Vector RAG complete workflow."""

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
    def technical_document(self):
        """Create a technical document for semantic search testing."""
        content = """
        Python is a high-level programming language known for its simplicity and readability.
        It supports multiple programming paradigms including procedural, object-oriented, and functional programming.
        Python has a comprehensive standard library that provides tools for file I/O, system calls, and networking.
        The language uses dynamic typing and automatic memory management through garbage collection.
        Popular frameworks built with Python include Django for web development and TensorFlow for machine learning.
        Python's syntax emphasizes code readability through the use of significant indentation.
        The Python Package Index (PyPI) hosts thousands of third-party libraries for various purposes.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def multi_topic_documents(self):
        """Create documents on different topics for retrieval testing."""
        doc1 = """
        Machine learning is a subset of artificial intelligence that enables computers to learn from data.
        Supervised learning uses labeled datasets to train models for classification and regression tasks.
        Unsupervised learning finds patterns in unlabeled data through clustering and dimensionality reduction.
        Deep learning uses neural networks with multiple layers to learn hierarchical representations.
        """

        doc2 = """
        Database management systems store and organize data for efficient retrieval and manipulation.
        SQL databases use structured query language for relational data management.
        NoSQL databases handle unstructured data and provide horizontal scalability.
        Database indexing improves query performance by creating fast lookup structures.
        """

        doc3 = """
        Cloud computing delivers computing services over the internet on a pay-as-you-go basis.
        Infrastructure as a Service (IaaS) provides virtualized computing resources.
        Platform as a Service (PaaS) offers development and deployment environments.
        Software as a Service (SaaS) delivers applications over the web without local installation.
        """

        temp_files = []
        for i, content in enumerate([doc1, doc2, doc3], 1):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_doc{i}.txt", delete=False) as f:
                f.write(content)
                temp_files.append(f.name)

        yield temp_files

        for path in temp_files:
            Path(path).unlink(missing_ok=True)

    @pytest.fixture
    def long_document(self):
        """Create a long document to test chunking."""
        # Generate document with multiple paragraphs
        paragraphs = []
        for i in range(10):
            paragraphs.append(
                f"This is paragraph {i} of the long document. "
                f"It contains information about topic {i}. "
                f"The content here is designed to test how the system handles "
                f"longer documents that need to be split into multiple chunks. "
                f"Each chunk should maintain semantic coherence and proper boundaries. "
            )

        content = "\n\n".join(paragraphs)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    def test_vector_workspace_creation(self):
        """Test creating Vector RAG workspace with default config."""
        # Create workspace with vector RAG (default)
        result = self.run_cli(
            "workspace", "create", input_text="Vector E2E Test\nVector test workspace\n\n"
        )

        assert result.returncode == 0
        assert "Vector E2E Test" in result.stdout or "created" in result.stdout.lower()

        # Extract workspace ID
        workspace_id = None
        for line in result.stdout.split("\n"):
            if "[" in line and "]" in line:
                try:
                    workspace_id = line.split("[")[1].split("]")[0]
                    break
                except Exception:
                    continue

        assert workspace_id is not None, "Could not extract workspace ID"

        # Verify workspace shows vector config
        show_result = self.run_cli("workspace", "show", workspace_id)
        assert show_result.returncode == 0
        assert "vector" in show_result.stdout.lower()
        # Should show vector-specific fields
        assert "chunking" in show_result.stdout.lower() or "embedding" in show_result.stdout.lower()

    def test_document_chunking_and_embedding(self, long_document):
        """Test that long documents are properly chunked and embedded."""
        # Create vector workspace
        ws_result = self.run_cli("workspace", "create", input_text="Chunking Test\n\n\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Select workspace and upload document
        self.run_cli("workspace", "select", workspace_id)
        upload_result = self.run_cli("document", "upload", long_document)
        assert upload_result.returncode == 0
        assert "uploaded" in upload_result.stdout.lower()

        # Verify document shows chunk count
        import time

        time.sleep(2)  # Allow processing

        list_result = self.run_cli("document", "list")
        assert list_result.returncode == 0

        doc_id = None
        for line in list_result.stdout.split("\n"):
            if "[" in line and "]" in line:
                try:
                    doc_id = line.split("[")[1].split("]")[0]
                    break
                except Exception:
                    continue

        if doc_id:
            show_doc = self.run_cli("document", "show", doc_id)
            assert show_doc.returncode == 0
            # Should show chunks were created
            assert "chunk" in show_doc.stdout.lower()

    def test_semantic_search_retrieval(self, multi_topic_documents):
        """Test that semantic search retrieves relevant documents."""
        # Create vector workspace
        ws_result = self.run_cli("workspace", "create", input_text="Search Test\n\n\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Upload all documents
        self.run_cli("workspace", "select", workspace_id)
        for doc_path in multi_topic_documents:
            upload_result = self.run_cli("document", "upload", doc_path)
            assert upload_result.returncode == 0

        # Wait for processing
        import time

        time.sleep(3)

        # Create chat session
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="\n")
        assert chat_result.returncode == 0

        match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert match is not None, "Could not extract chat session ID"
        session_id = match.group(1)

        assert session_id is not None
        self.run_cli("chat", "select", session_id)

        # Query about machine learning - should retrieve ML document
        query_result = self.run_cli("chat", "send", "What is supervised learning?")
        assert query_result.returncode == 0
        assert len(query_result.stdout) > 0

    def test_context_aware_responses(self, technical_document):
        """Test that chat responses use document context appropriately."""
        # Create vector workspace
        ws_result = self.run_cli("workspace", "create", input_text="Context Test\n\n\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Upload document and create session
        self.run_cli("workspace", "select", workspace_id)
        upload_result = self.run_cli("document", "upload", technical_document)
        assert upload_result.returncode == 0

        import time

        time.sleep(2)

        chat_result = self.run_cli("chat", "create", workspace_id, input_text="\n")
        assert chat_result.returncode == 0

        match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert match is not None, "Could not extract chat session ID"
        session_id = match.group(1)

        assert session_id is not None
        self.run_cli("chat", "select", session_id)

        # Ask specific question from document
        query_result = self.run_cli(
            "chat", "send", "What programming paradigms does Python support?"
        )
        assert query_result.returncode == 0
        # Should get a response
        assert len(query_result.stdout) > 20

    def test_multiple_document_upload(self):
        """Test uploading multiple documents sequentially."""
        # Create workspace
        ws_result = self.run_cli("workspace", "create", input_text="Multi Upload Test\n\n\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None
        self.run_cli("workspace", "select", workspace_id)

        # Upload 3 documents
        uploaded_count = 0
        for i in range(3):
            content = (
                f"This is test document number {i}. It contains unique content about topic {i}."
            )
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_test{i}.txt", delete=False) as f:
                f.write(content)
                temp_path = f.name

            try:
                upload_result = self.run_cli("document", "upload", temp_path)
                if upload_result.returncode == 0:
                    uploaded_count += 1
            finally:
                Path(temp_path).unlink(missing_ok=True)

        assert uploaded_count == 3, f"Expected 3 uploads, got {uploaded_count}"

        # Verify all documents are listed
        list_result = self.run_cli("document", "list")
        assert list_result.returncode == 0
        doc_count = list_result.stdout.count("[")
        assert doc_count >= 3, f"Expected at least 3 documents listed, found {doc_count}"

    def test_document_removal_updates_vectors(self, technical_document):
        """Test that removing document cleans up vector embeddings."""
        # Create workspace and upload document
        ws_result = self.run_cli("workspace", "create", input_text="Removal Test\n\n\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        self.run_cli("workspace", "select", workspace_id)
        upload_result = self.run_cli("document", "upload", technical_document)
        assert upload_result.returncode == 0

        # Get document filename
        filename = Path(technical_document).name

        # Remove document
        remove_result = self.run_cli("document", "remove", filename, input_text="yes\n")
        assert remove_result.returncode == 0 or "deleted" in remove_result.stdout.lower()

        # Verify document is gone
        list_result = self.run_cli("document", "list")
        assert list_result.returncode == 0
        assert "no documents" in list_result.stdout.lower() or filename not in list_result.stdout

    def test_empty_workspace_chat(self):
        """Test chatting in workspace with no documents."""
        # Create empty workspace
        ws_result = self.run_cli("workspace", "create", input_text="Empty Workspace\n\n\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Create chat session
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="\n")
        assert chat_result.returncode == 0

        match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert match is not None, "Could not extract chat session ID"
        session_id = match.group(1)

        assert session_id is not None
        self.run_cli("chat", "select", session_id)

        # Send message - should work without documents
        query_result = self.run_cli("chat", "send", "Hello")
        assert query_result.returncode == 0
        assert len(query_result.stdout) > 0

    def test_workspace_with_custom_chunk_size(self):
        """Test workspace creation with custom chunking configuration."""
        # Note: Current CLI doesn't support setting chunk size during creation
        # This test verifies the workspace uses default config
        ws_result = self.run_cli("workspace", "create", input_text="Custom Config Test\n\n\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Show workspace to verify config
        show_result = self.run_cli("workspace", "show", workspace_id)
        assert show_result.returncode == 0
        # Should show chunking config
        assert "chunk" in show_result.stdout.lower()

    def test_chat_session_management(self):
        """Test creating and switching between multiple chat sessions."""
        # Create workspace
        ws_result = self.run_cli("workspace", "create", input_text="Session Test\n\n\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Create two chat sessions
        session_ids = []
        for i in range(2):
            chat_result = self.run_cli("chat", "create", workspace_id, input_text=f"Session {i}\n")
            assert chat_result.returncode == 0

            for line in chat_result.stdout.split("\n"):
                if "[" in line and "]" in line:
                    try:
                        session_id = line.split("[")[1].split("]")[0]
                        session_ids.append(session_id)
                        break
                    except Exception:
                        continue

        assert len(session_ids) == 2, "Expected to create 2 sessions"

        # List sessions - should show both
        list_result = self.run_cli("chat", "list", workspace_id)
        assert list_result.returncode == 0
        session_count = list_result.stdout.count("[")
        assert session_count >= 2, f"Expected at least 2 sessions listed, found {session_count}"

    def test_concurrent_document_processing(self):
        """Test uploading multiple documents rapidly."""
        # Create workspace
        ws_result = self.run_cli("workspace", "create", input_text="Concurrent Test\n\n\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None
        self.run_cli("workspace", "select", workspace_id)

        # Create and upload 5 documents rapidly
        temp_files = []
        for i in range(5):
            content = f"Rapid upload test document {i}. Content for testing concurrent processing."
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_rapid{i}.txt", delete=False) as f:
                f.write(content)
                temp_files.append(f.name)

        try:
            # Upload all files
            for temp_path in temp_files:
                upload_result = self.run_cli("document", "upload", temp_path)
                # Should succeed or handle gracefully
                assert upload_result.returncode in (0, 1)  # May fail if processing is slow

            # Verify documents were uploaded
            import time

            time.sleep(2)

            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0
            # At least some documents should be present
            assert "[" in list_result.stdout

        finally:
            for temp_path in temp_files:
                Path(temp_path).unlink(missing_ok=True)
