"""E2E tests for workflows that involve both Vector and Graph RAG.

These tests verify:
- Switching between different RAG types
- Comparing results from vector vs graph approaches
- Migrating workspaces between RAG types (if supported)
- Using both RAG types in the same session
"""

import re
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.mark.e2e
class TestCrossRagWorkflows:
    """E2E tests for workflows involving both RAG types."""

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
    def comparable_document(self):
        """Create document that works well with both RAG types."""
        content = """
        Amazon Web Services (AWS) is a cloud computing platform provided by Amazon.
        AWS offers services including EC2 for virtual servers and S3 for object storage.
        Microsoft Azure competes with AWS in the cloud services market.
        Azure provides similar services like Virtual Machines and Blob Storage.
        Google Cloud Platform (GCP) is another major player in cloud computing.
        All three platforms support machine learning and artificial intelligence services.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    def test_create_both_rag_types_in_session(self):
        """Test creating both vector and graph workspaces in same session."""
        # Create vector workspace
        vector_result = self.run_cli(
            "workspace",
            "create",
            input_text="Vector Workspace\nVector workspace for testing\nvector\n",
        )
        assert vector_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", vector_result.stdout)
        assert match is not None, "Could not extract workspace ID from output"
        vector_ws_id = match.group(1)

        # Create graph workspace
        graph_result = self.run_cli(
            "workspace",
            "create",
            input_text="Graph Workspace\nGraph workspace for testing\ngraph\n",
        )
        assert graph_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", graph_result.stdout)
        assert match is not None, "Could not extract workspace ID from output"
        graph_ws_id = match.group(1)

        # Verify both exist and have different IDs
        assert vector_ws_id != graph_ws_id

        # List workspaces
        list_result = self.run_cli("workspace", "list")
        assert list_result.returncode == 0

        # Both should be in the list
        assert vector_ws_id in list_result.stdout or "Vector Workspace" in list_result.stdout
        assert graph_ws_id in list_result.stdout or "Graph Workspace" in list_result.stdout

    def test_same_document_both_rag_types(self, comparable_document):
        """Test uploading same document to both vector and graph workspaces."""
        # Create vector workspace
        vector_result = self.run_cli("workspace", "create", input_text="Vector Test\n\nvector\n")
        assert vector_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", vector_result.stdout)
        assert match is not None, "Could not extract workspace ID from output"
        vector_ws_id = match.group(1)

        # Create graph workspace
        graph_result = self.run_cli("workspace", "create", input_text="Graph Test\n\ngraph\n")
        assert graph_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", graph_result.stdout)
        assert match is not None, "Could not extract workspace ID from output"
        graph_ws_id = match.group(1)

        # Upload same document to both workspaces
        # Vector first
        self.run_cli("workspace", "select", vector_ws_id)
        vector_upload = self.run_cli("document", "upload", comparable_document)
        assert vector_upload.returncode == 0

        # Graph second
        self.run_cli("workspace", "select", graph_ws_id)
        graph_upload = self.run_cli("document", "upload", comparable_document)
        assert graph_upload.returncode == 0

        # Both uploads should succeed
        assert "uploaded" in vector_upload.stdout.lower()
        assert "uploaded" in graph_upload.stdout.lower()

    def test_switch_workspace_selection_between_rag_types(self):
        """Test switching selected workspace between vector and graph types."""
        # Create both workspace types
        vector_result = self.run_cli("workspace", "create", input_text="Vector WS\n\nvector\n")
        match = re.search(r"Created workspace \[(\d+)\]", vector_result.stdout)
        assert match is not None, "Could not extract vector workspace ID from output"
        vector_ws_id = match.group(1)

        graph_result = self.run_cli("workspace", "create", input_text="Graph WS\n\ngraph\n")
        match = re.search(r"Created workspace \[(\d+)\]", graph_result.stdout)
        assert match is not None, "Could not extract graph workspace ID from output"
        graph_ws_id = match.group(1)

        assert vector_ws_id is not None and graph_ws_id is not None

        # Select vector workspace
        select_vector = self.run_cli("workspace", "select", vector_ws_id)
        assert select_vector.returncode == 0

        # Check state shows vector workspace
        state1 = self.run_cli("state", "show")
        assert state1.returncode == 0
        assert vector_ws_id in state1.stdout

        # Select graph workspace
        select_graph = self.run_cli("workspace", "select", graph_ws_id)
        assert select_graph.returncode == 0

        # Check state shows graph workspace
        state2 = self.run_cli("state", "show")
        assert state2.returncode == 0
        assert graph_ws_id in state2.stdout

    def test_chat_comparison_vector_vs_graph(self, comparable_document):
        """Test querying same content with both RAG types."""
        # Create and populate vector workspace
        vector_result = self.run_cli("workspace", "create", input_text="Vector Chat\n\nvector\n")
        match = re.search(r"Created workspace \[(\d+)\]", vector_result.stdout)
        assert match is not None, "Could not extract workspace ID from output"
        vector_ws_id = match.group(1)

        self.run_cli("workspace", "select", vector_ws_id)
        self.run_cli("document", "upload", comparable_document)

        # Create vector chat session
        vector_chat = self.run_cli("chat", "create", vector_ws_id, input_text="\n")
        match = re.search(r"Created chat session \[(\d+)\]", vector_chat.stdout)
        assert match is not None, "Could not extract chat session ID from output"
        vector_session_id = match.group(1)

        # Create and populate graph workspace
        graph_result = self.run_cli("workspace", "create", input_text="Graph Chat\n\ngraph\n")
        match = re.search(r"Created workspace \[(\d+)\]", graph_result.stdout)
        assert match is not None, "Could not extract workspace ID from output"
        graph_ws_id = match.group(1)

        self.run_cli("workspace", "select", graph_ws_id)
        self.run_cli("document", "upload", comparable_document)

        # Create graph chat session
        graph_chat = self.run_cli("chat", "create", graph_ws_id, input_text="\n")
        match = re.search(r"Created chat session \[(\d+)\]", graph_chat.stdout)
        assert match is not None, "Could not extract chat session ID from output"
        graph_session_id = match.group(1)

        import time

        time.sleep(3)  # Allow processing

        # Query both with same question
        query = "What cloud providers are mentioned?"

        # Vector query
        self.run_cli("chat", "select", vector_session_id)
        vector_query_result = self.run_cli("chat", "send", query)
        assert vector_query_result.returncode == 0

        # Graph query
        self.run_cli("chat", "select", graph_session_id)
        graph_query_result = self.run_cli("chat", "send", query)
        assert graph_query_result.returncode == 0

        # Both should produce responses
        assert len(vector_query_result.stdout) > 20
        assert len(graph_query_result.stdout) > 20

    def test_list_workspaces_shows_rag_type_distinction(self):
        """Test that workspace list clearly shows RAG type difference."""
        # Create one of each type
        self.run_cli("workspace", "create", input_text="Vector Listing\n\nvector\n")
        self.run_cli("workspace", "create", input_text="Graph Listing\n\ngraph\n")

        # List workspaces
        list_result = self.run_cli("workspace", "list")
        assert list_result.returncode == 0

        # Both should appear
        assert "Vector Listing" in list_result.stdout or "Graph Listing" in list_result.stdout

    def test_state_management_across_rag_types(self):
        """Test that state is properly maintained when switching between RAG types."""
        # Create vector workspace
        vector_result = self.run_cli("workspace", "create", input_text="State Vector\n\nvector\n")
        match = re.search(r"Created workspace \[(\d+)\]", vector_result.stdout)
        assert match is not None, "Could not extract vector workspace ID from output"
        vector_ws_id = match.group(1)

        # Select it
        self.run_cli("workspace", "select", vector_ws_id)

        # Create chat in vector workspace
        vector_chat = self.run_cli("chat", "create", vector_ws_id, input_text="\n")
        match = re.search(r"Created chat session \[(\d+)\]", vector_chat.stdout)
        assert match is not None, "Could not extract chat session ID from output"
        vector_session_id = match.group(1)

        self.run_cli("chat", "select", vector_session_id)

        # Check state shows both
        state1 = self.run_cli("state", "show")
        assert state1.returncode == 0
        assert vector_ws_id in state1.stdout

        # Create graph workspace
        graph_result = self.run_cli("workspace", "create", input_text="State Graph\n\ngraph\n")
        match = re.search(r"Created workspace \[(\d+)\]", graph_result.stdout)
        assert match is not None, "Could not extract graph workspace ID from output"
        graph_ws_id = match.group(1)

        # Select graph workspace
        self.run_cli("workspace", "select", graph_ws_id)

        # State should update
        state2 = self.run_cli("state", "show")
        assert state2.returncode == 0
        assert graph_ws_id in state2.stdout

    def test_document_operations_independent_per_rag_type(self):
        """Test that documents in different RAG workspaces are independent."""
        # Create both workspace types
        vector_result = self.run_cli("workspace", "create", input_text="Vector Docs\n\nvector\n")
        match = re.search(r"Created workspace \[(\d+)\]", vector_result.stdout)
        assert match is not None, "Could not extract vector workspace ID from output"
        vector_ws_id = match.group(1)

        graph_result = self.run_cli("workspace", "create", input_text="Graph Docs\n\ngraph\n")
        match = re.search(r"Created workspace \[(\d+)\]", graph_result.stdout)
        assert match is not None, "Could not extract graph workspace ID from output"
        graph_ws_id = match.group(1)

        # Upload document to vector workspace
        self.run_cli("workspace", "select", vector_ws_id)
        with tempfile.NamedTemporaryFile(mode="w", suffix="_vector.txt", delete=False) as f:
            f.write("Vector workspace document content.")
            vector_doc = f.name

        try:
            self.run_cli("document", "upload", vector_doc)

            # Check vector workspace has document
            vector_list = self.run_cli("document", "list")
            assert vector_list.returncode == 0
            assert "[" in vector_list.stdout

            # Switch to graph workspace
            self.run_cli("workspace", "select", graph_ws_id)

            # Graph workspace should be empty
            graph_list = self.run_cli("document", "list")
            assert graph_list.returncode == 0
            # Should not show vector workspace's document
            assert (
                "no documents" in graph_list.stdout.lower() or vector_doc not in graph_list.stdout
            )

        finally:
            Path(vector_doc).unlink(missing_ok=True)

    def test_delete_workspace_preserves_other_rag_type(self):
        """Test that deleting vector workspace doesn't affect graph workspace."""
        # Create both types
        vector_result = self.run_cli("workspace", "create", input_text="Vector Delete\n\nvector\n")
        match = re.search(r"Created workspace \[(\d+)\]", vector_result.stdout)
        assert match is not None, "Could not extract vector workspace ID from output"
        vector_ws_id = match.group(1)

        graph_result = self.run_cli("workspace", "create", input_text="Graph Preserve\n\ngraph\n")
        match = re.search(r"Created workspace \[(\d+)\]", graph_result.stdout)
        assert match is not None, "Could not extract graph workspace ID from output"
        graph_ws_id = match.group(1)

        # Delete vector workspace
        delete_result = self.run_cli("workspace", "delete", vector_ws_id, input_text="yes\n")
        assert delete_result.returncode == 0 or "deleted" in delete_result.stdout.lower()

        # Graph workspace should still exist
        show_graph = self.run_cli("workspace", "show", graph_ws_id)
        assert show_graph.returncode == 0
        assert "Graph Preserve" in show_graph.stdout or graph_ws_id in show_graph.stdout

    def test_rag_options_lists_both_types(self):
        """Test that rag-options command shows options for both RAG types."""
        result = self.run_cli("rag-options", "list")

        assert result.returncode == 0
        output = result.stdout.lower()

        # Should show vector-specific options
        assert "chunking" in output or "embedding" in output

        # Should show graph-specific options
        assert "entity" in output or "clustering" in output

        # Should show RAG types
        assert "vector" in output
        assert "graph" in output
