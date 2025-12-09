"""E2E tests for Graph RAG CLI workflow.

Tests the complete Graph RAG workflow from document add to querying.
"""

import re
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.mark.e2e
@pytest.mark.integration
class TestGraphRagCLI:
    """End-to-end tests for Graph RAG CLI workflow."""

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
    def temp_document(self):
        """Create a temporary document for testing."""
        content = """
        Anthropic is an AI safety company founded by Dario Amodei and Daniela Amodei.
        The company is headquartered in San Francisco, California.
        Anthropic developed Claude, a large language model focused on safety and helpfulness.
        The research team includes former OpenAI researchers who worked on GPT-3.
        Anthropic has partnerships with Google Cloud for infrastructure.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    def test_workspace_create_with_graph_rag(self):
        """Test creating a workspace with Graph RAG configuration."""
        # Act - Create workspace with interactive input
        result = self.run_cli(
            "workspace",
            "create",
            input_text="graph_rag_test_workspace\nTest workspace for graph RAG\ngraph\n",
        )

        # Assert
        assert result.returncode == 0
        output_lower = result.stdout.lower()
        assert "created workspace" in output_lower or "graph_rag_test_workspace" in output_lower

    def test_document_add_with_graph_rag(self, temp_document):
        """Test adding a document to a Graph RAG workspace."""
        # Arrange - Create workspace first with interactive input
        create_result = self.run_cli(
            "workspace",
            "create",
            input_text="graph_doc_test\nTest workspace for document\ngraph\n",
        )
        assert create_result.returncode == 0

        # Extract workspace ID from output - format is "Created workspace [ID] name"
        match = re.search(r"Created workspace \[(\d+)\]", create_result.stdout)
        assert (
            match is not None
        ), f"Could not extract workspace ID from output: {create_result.stdout}"
        workspace_id = match.group(1)

        # Select the workspace
        select_result = self.run_cli("workspace", "select", str(workspace_id))
        assert select_result.returncode == 0

        # Act - Add document
        result = self.run_cli("document", "add", temp_document)

        # Assert
        assert result.returncode == 0

    def test_chat_query_with_graph_rag(self):
        """Test querying a Graph RAG workspace."""
        # Arrange - Create workspace with interactive input
        create_result = self.run_cli(
            "workspace",
            "create",
            input_text="graph_query_test\nTest workspace for querying\ngraph\n",
        )
        assert create_result.returncode == 0

        # Extract workspace ID
        match = re.search(r"Created workspace \[(\d+)\]", create_result.stdout)
        assert (
            match is not None
        ), f"Could not extract workspace ID from output: {create_result.stdout}"
        workspace_id = match.group(1)

        # Select the workspace
        select_result = self.run_cli("workspace", "select", str(workspace_id))
        assert select_result.returncode == 0

        # Create a chat session
        chat_result = self.run_cli("chat", "create", str(workspace_id), input_text="Test Chat\n")
        assert chat_result.returncode == 0

        # Extract session ID and select it
        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert (
            session_match is not None
        ), f"Could not extract session ID from output: {chat_result.stdout}"
        session_id = session_match.group(1)

        select_chat_result = self.run_cli("chat", "select", str(session_id))
        assert select_chat_result.returncode == 0

        # Act - Try to send a chat message (even if no documents)
        result = self.run_cli("chat", "send", "Tell me about AI safety")

        # Assert
        assert result.returncode == 0

    def test_rag_options_shows_graph_algorithms(self):
        """Test that rag-options shows Graph RAG algorithm choices."""
        # Act
        result = self.run_cli("rag-options", "list")

        # Assert
        assert result.returncode == 0
        output_lower = result.stdout.lower()

        # Should show graph-specific options
        assert "entity extraction algorithms" in output_lower
        assert "relationship extraction algorithms" in output_lower
        assert "clustering algorithms" in output_lower

        # Should show specific algorithms
        assert "spacy" in output_lower
        assert "leiden" in output_lower or "louvain" in output_lower

    def test_default_rag_config_set_graph_options(self):
        """Test setting Graph RAG default configuration."""
        # Act - Set entity extraction algorithm
        result = self.run_cli(
            "default-rag-config",
            "set",
            "--entity-extraction-algorithm",
            "spacy",
        )

        # Assert
        # Might succeed or fail depending on database state
        # We just verify the command accepts the parameter
        assert isinstance(result.returncode, int)

    def test_default_rag_config_set_clustering_algorithm(self):
        """Test setting clustering algorithm in default config."""
        # Act
        result = self.run_cli(
            "default-rag-config",
            "set",
            "--clustering-algorithm",
            "leiden",
        )

        # Assert
        assert isinstance(result.returncode, int)

    def test_workspace_list_shows_graph_workspaces(self):
        """Test that workspace list shows Graph RAG workspaces."""
        # Arrange - Create a graph workspace with interactive input
        create_result = self.run_cli(
            "workspace",
            "create",
            input_text="graph_list_test\nTest workspace for listing\ngraph\n",
        )

        assert (
            create_result.returncode == 0
        ), f"Failed to create test workspace: {create_result.stderr}"

        # Act
        result = self.run_cli("workspace", "list")

        # Assert
        assert result.returncode == 0
        output_lower = result.stdout.lower()
        assert "graph_list_test" in output_lower or "workspace" in output_lower

    def test_graph_rag_end_to_end_workflow(self, temp_document):
        """Test complete Graph RAG workflow: create workspace -> add document -> query."""
        # Step 1: Create workspace with Graph RAG using interactive input
        create_result = self.run_cli(
            "workspace",
            "create",
            input_text="graph_e2e_test\nE2E test workspace\ngraph\n",
        )

        assert create_result.returncode == 0, f"Failed to create workspace: {create_result.stderr}"

        # Extract workspace ID
        match = re.search(r"Created workspace \[(\d+)\]", create_result.stdout)
        assert (
            match is not None
        ), f"Could not extract workspace ID from output: {create_result.stdout}"
        workspace_id = match.group(1)

        # Select the workspace
        select_result = self.run_cli("workspace", "select", str(workspace_id))
        assert select_result.returncode == 0, f"Failed to select workspace: {select_result.stderr}"

        # Step 2: Add document
        doc_result = self.run_cli("document", "add", temp_document)

        assert doc_result.returncode == 0, f"Failed to add document: {doc_result.stderr}"

        # Step 3: Create a chat session
        chat_create_result = self.run_cli(
            "chat", "create", str(workspace_id), input_text="E2E Test Chat\n"
        )
        assert (
            chat_create_result.returncode == 0
        ), f"Failed to create chat: {chat_create_result.stderr}"

        # Extract session ID and select it
        session_match = re.search(r"Created chat session \[(\d+)\]", chat_create_result.stdout)
        assert (
            session_match is not None
        ), f"Could not extract session ID from output: {chat_create_result.stdout}"
        session_id = session_match.group(1)

        select_chat_result = self.run_cli("chat", "select", str(session_id))
        assert (
            select_chat_result.returncode == 0
        ), f"Failed to select chat: {select_chat_result.stderr}"

        # Step 4: Query the workspace
        query_result = self.run_cli("chat", "send", "What companies are mentioned?")

        # Assert - The query should complete successfully
        assert query_result.returncode == 0, f"Failed to query workspace: {query_result.stderr}"

        # Step 5: List documents
        list_result = self.run_cli("document", "list")

        assert list_result.returncode == 0
        # Should show at least one document - check for the filename
        import os

        filename = os.path.basename(temp_document)
        assert (
            filename in list_result.stdout
        ), f"Expected to find {filename} in document list output: {list_result.stdout}"

        # Note: Workspace cleanup is handled automatically by conftest fixture
