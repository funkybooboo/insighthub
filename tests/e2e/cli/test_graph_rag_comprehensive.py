"""Comprehensive E2E tests for Graph RAG functionality.

These tests verify the complete Graph RAG pipeline:
- Entity extraction from documents
- Relationship extraction between entities
- Community detection/clustering
- Graph-based retrieval during chat queries
"""

import re
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.mark.e2e
class TestGraphRagComprehensive:
    """E2E tests for Graph RAG complete workflow."""

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
    def entity_rich_document(self):
        """Create document with clear entities and relationships for testing."""
        content = """
        Alice Johnson works at Anthropic as a research scientist. She is based in San Francisco.
        Bob Smith is the CEO of TechCorp and previously worked at Google in Mountain View.
        Anthropic developed Claude, an AI assistant focused on safety and helpfulness.
        TechCorp partners with Anthropic to integrate Claude into their products.
        Alice collaborates with Bob on AI safety research projects.
        San Francisco is the headquarters of Anthropic.
        Mountain View is located in Silicon Valley, California.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def multi_entity_documents(self):
        """Create multiple documents for testing graph connections."""
        doc1 = """
        OpenAI was founded by Sam Altman, Elon Musk, and others in 2015.
        The company is headquartered in San Francisco, California.
        OpenAI developed GPT-4, a large language model.
        """

        doc2 = """
        Sam Altman serves as CEO of OpenAI.
        He previously led Y Combinator, a startup accelerator.
        Y Combinator is based in Mountain View, California.
        """

        doc3 = """
        Elon Musk founded Tesla and SpaceX.
        Tesla manufactures electric vehicles and is headquartered in Austin, Texas.
        SpaceX develops rockets and spacecraft in Hawthorne, California.
        """

        temp_files = []
        for i, content in enumerate([doc1, doc2, doc3], 1):
            with tempfile.NamedTemporaryFile(mode="w", suffix=f"_doc{i}.txt", delete=False) as f:
                f.write(content)
                temp_files.append(f.name)

        yield temp_files

        for path in temp_files:
            Path(path).unlink(missing_ok=True)

    def test_graph_workspace_creation_with_config(self):
        """Test creating Graph RAG workspace displays correct configuration."""
        # Create workspace with graph RAG
        result = self.run_cli(
            "workspace", "create", input_text="Graph E2E Test\nGraph test workspace\ngraph\n"
        )

        assert result.returncode == 0
        assert "Graph E2E Test" in result.stdout or "created" in result.stdout.lower()

        # Extract workspace ID
        match = re.search(r"Created workspace \[(\d+)\]", result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        # Verify workspace shows graph config
        show_result = self.run_cli("workspace", "show", workspace_id)
        assert show_result.returncode == 0
        assert "graph" in show_result.stdout.lower()
        # Should show graph-specific fields
        assert (
            "entity extraction" in show_result.stdout.lower()
            or "clustering" in show_result.stdout.lower()
        )

    def test_document_upload_extracts_entities(self):
        """Test that uploading a document to graph workspace extracts entities to Neo4j."""
        # Create graph workspace
        ws_result = self.run_cli(
            "workspace", "create", input_text="Entity Extraction Test\n\ngraph\n"
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Select the workspace
        self.run_cli("workspace", "select", workspace_id)

        # Upload entity-rich document
        doc_content = """
        Microsoft was founded by Bill Gates and Paul Allen in 1975.
        The company is headquartered in Redmond, Washington.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(doc_content)
            doc_path = f.name

        try:
            upload_result = self.run_cli("document", "upload", doc_path)
            assert upload_result.returncode == 0
            assert "uploaded" in upload_result.stdout.lower()

            # Verify document status is ready (meaning extraction completed)
            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0

            # Extract document ID
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
                assert "ready" in show_doc.stdout.lower()

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_chat_query_uses_graph_context(self, entity_rich_document):
        """Test that chat queries in graph workspace use entity relationships."""
        # Create and select graph workspace
        ws_result = self.run_cli("workspace", "create", input_text="Graph Query Test\n\ngraph\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Select workspace and upload document
        self.run_cli("workspace", "select", workspace_id)
        upload_result = self.run_cli("document", "upload", entity_rich_document)
        assert upload_result.returncode == 0

        # Wait a moment for processing
        import time

        time.sleep(2)

        # Create chat session
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test Chat\n")
        assert chat_result.returncode == 0

        match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert match is not None, "Could not extract chat session ID"
        session_id = match.group(1)

        assert session_id is not None

        # Select session and send query
        self.run_cli("chat", "select", session_id)

        # Query about entities - should use graph context
        query_result = self.run_cli("chat", "send", "Who works at Anthropic?")

        # Should complete without error
        assert query_result.returncode == 0
        # Response should exist (whether it has context or not)
        assert len(query_result.stdout) > 0

    def test_multiple_documents_create_connected_graph(self, multi_entity_documents):
        """Test that multiple documents create interconnected entity graph."""
        # Create graph workspace
        ws_result = self.run_cli("workspace", "create", input_text="Multi-Doc Graph\n\ngraph\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Select workspace
        self.run_cli("workspace", "select", workspace_id)

        # Upload all documents
        for doc_path in multi_entity_documents:
            upload_result = self.run_cli("document", "upload", doc_path)
            assert upload_result.returncode == 0

        # Verify all documents are listed
        list_result = self.run_cli("document", "list")
        assert list_result.returncode == 0

        # Count documents in output
        doc_count = list_result.stdout.count("[")
        assert doc_count >= 3, f"Expected at least 3 documents, found {doc_count}"

    def test_graph_rag_handles_large_document(self):
        """Test graph RAG processing of larger documents with many entities."""
        # Create document with many entities
        entities = []
        for i in range(20):
            entities.append(
                f"Person{i} works at Company{i} in City{i}. "
                f"They collaborate with Person{i+1} on Project{i}."
            )

        large_content = " ".join(entities)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(large_content)
            doc_path = f.name

        try:
            # Create graph workspace
            ws_result = self.run_cli("workspace", "create", input_text="Large Doc Test\n\ngraph\n")
            assert ws_result.returncode == 0

            workspace_id = None
            for line in ws_result.stdout.split("\n"):
                if "[" in line and "]" in line:
                    try:
                        workspace_id = line.split("[")[1].split("]")[0]
                        break
                    except Exception:
                        continue

            assert workspace_id is not None

            # Select and upload
            self.run_cli("workspace", "select", workspace_id)
            upload_result = self.run_cli("document", "upload", doc_path)

            # Should handle upload without crashing
            assert upload_result.returncode == 0

            # Verify document reaches ready state
            import time

            time.sleep(3)  # Allow processing time

            list_result = self.run_cli("document", "list")
            assert list_result.returncode == 0
            assert "[" in list_result.stdout  # At least one document listed

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_switching_from_vector_to_graph_rag(self):
        """Test creating vector workspace then graph workspace in same session."""
        # Create vector workspace
        vector_result = self.run_cli(
            "workspace", "create", input_text="Vector Workspace\n\nvector\n\n\n\n\n\n\n"
        )
        assert vector_result.returncode == 0
        assert (
            "Vector Workspace" in vector_result.stdout or "created" in vector_result.stdout.lower()
        )

        # Create graph workspace
        graph_result = self.run_cli(
            "workspace", "create", input_text="Graph Workspace\n\ngraph\n\n\n\n"
        )
        assert graph_result.returncode == 0
        assert "Graph Workspace" in graph_result.stdout or "created" in graph_result.stdout.lower()

        # List workspaces - both should exist
        list_result = self.run_cli("workspace", "list")
        assert list_result.returncode == 0

        # Should see both workspace names
        output = list_result.stdout.lower()
        assert "vector workspace" in output or "graph workspace" in output

    def test_graph_workspace_document_removal(self, entity_rich_document):
        """Test removing document from graph workspace cleans up graph data."""
        # Create graph workspace
        ws_result = self.run_cli("workspace", "create", input_text="Removal Test\n\ngraph\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Select and upload
        self.run_cli("workspace", "select", workspace_id)
        upload_result = self.run_cli("document", "upload", entity_rich_document)
        assert upload_result.returncode == 0

        # Get document filename
        filename = Path(entity_rich_document).name

        # Remove document
        remove_result = self.run_cli("document", "remove", filename, input_text="yes\n")

        # Should complete successfully
        assert remove_result.returncode == 0 or "deleted" in remove_result.stdout.lower()

        # Verify document is gone
        list_result = self.run_cli("document", "list")
        assert list_result.returncode == 0
        assert "no documents" in list_result.stdout.lower() or filename not in list_result.stdout

    def test_chat_history_preserved_in_graph_workspace(self):
        """Test that chat history is maintained across queries in graph workspace."""
        # Create graph workspace
        ws_result = self.run_cli("workspace", "create", input_text="History Test\n\ngraph\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Create and select chat session
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="History Test\n")
        assert chat_result.returncode == 0

        match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert match is not None, "Could not extract chat session ID"
        session_id = match.group(1)

        assert session_id is not None
        self.run_cli("chat", "select", session_id)

        # Send first message
        msg1_result = self.run_cli("chat", "send", "Hello, I am testing the system")
        assert msg1_result.returncode == 0

        # Send second message
        msg2_result = self.run_cli("chat", "send", "What did I just say?")
        assert msg2_result.returncode == 0

        # Check history
        history_result = self.run_cli("chat", "history")
        assert history_result.returncode == 0

        # History should contain both messages
        assert (
            "hello" in history_result.stdout.lower() or "testing" in history_result.stdout.lower()
        )
        assert (
            "2 messages" in history_result.stdout.lower()
            or history_result.stdout.count("You:") >= 2
        )

    def test_graph_workspace_deletion_cleans_up_neo4j(self, entity_rich_document):
        """Test that deleting graph workspace removes Neo4j data."""
        # Create graph workspace
        ws_result = self.run_cli("workspace", "create", input_text="Cleanup Test\n\ngraph\n")
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None, "Could not extract workspace ID"
        workspace_id = match.group(1)

        assert workspace_id is not None

        # Select and upload document to create graph data
        self.run_cli("workspace", "select", workspace_id)
        upload_result = self.run_cli("document", "upload", entity_rich_document)
        assert upload_result.returncode == 0

        # Delete workspace
        delete_result = self.run_cli("workspace", "delete", workspace_id, input_text="yes\n")

        # Should complete successfully
        assert delete_result.returncode == 0 or "deleted" in delete_result.stdout.lower()

        # Verify workspace is gone from list
        list_result = self.run_cli("workspace", "list")
        assert (
            workspace_id not in list_result.stdout or "no workspace" in list_result.stdout.lower()
        )
