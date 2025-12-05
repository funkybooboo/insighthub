"""E2E tests for rag-options CLI commands."""

import subprocess
import sys

import pytest


@pytest.mark.integration
class TestRagOptionsCLI:
    """End-to-end tests for rag-options CLI commands."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    def test_rag_options_list_command_exists(self):
        """Test that rag-options list command exists and runs."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0
        assert "available rag options" in result.stdout.lower()

    def test_rag_options_list_shows_rag_types(self):
        """Test that rag-options list shows RAG types."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        # Check for RAG types section
        assert "rag types" in result.stdout.lower()
        assert "vector" in result.stdout.lower()
        assert "graph" in result.stdout.lower()

    def test_rag_options_list_shows_chunking_algorithms(self):
        """Test that rag-options list shows chunking algorithms."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        # Check for chunking algorithms section
        assert "chunking algorithms" in result.stdout.lower()
        # Should have at least one chunking algorithm
        assert "sentence" in result.stdout.lower() or "character" in result.stdout.lower()

    def test_rag_options_list_shows_embedding_algorithms(self):
        """Test that rag-options list shows embedding algorithms."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        # Check for embedding algorithms section
        assert "embedding algorithms" in result.stdout.lower()
        # Should show at least one embedding algorithm
        assert any(
            alg in result.stdout.lower()
            for alg in ["nomic", "minilm", "mxbai", "embed"]
        )

    def test_rag_options_list_shows_rerank_algorithms(self):
        """Test that rag-options list shows reranking algorithms."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        # Check for rerank algorithms section
        assert "rerank algorithms" in result.stdout.lower()
        # Should have none option at minimum
        assert "none" in result.stdout.lower()

    def test_rag_options_list_shows_graph_algorithms(self):
        """Test that rag-options list shows graph RAG algorithms."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        # Check for graph-specific sections
        assert "entity extraction algorithms" in result.stdout.lower()
        assert "relationship extraction algorithms" in result.stdout.lower()
        assert "clustering algorithms" in result.stdout.lower()

    def test_rag_options_list_shows_entity_extraction(self):
        """Test that rag-options list shows entity extraction options."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        # Check for entity extraction options
        assert "entity extraction" in result.stdout.lower()
        assert any(
            opt in result.stdout.lower()
            for opt in ["spacy", "llm"]
        )

    def test_rag_options_list_shows_relationship_extraction(self):
        """Test that rag-options list shows relationship extraction options."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        # Check for relationship extraction options
        assert "relationship extraction" in result.stdout.lower()
        assert any(
            opt in result.stdout.lower()
            for opt in ["dependency-parsing", "llm"]
        )

    def test_rag_options_list_shows_clustering(self):
        """Test that rag-options list shows clustering options."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        # Check for clustering options
        assert "clustering algorithms" in result.stdout.lower()
        assert any(
            opt in result.stdout.lower()
            for opt in ["leiden", "louvain"]
        )

    def test_rag_options_help_command(self):
        """Test rag-options help command."""
        result = self.run_cli("rag-options", "--help")
        assert result.returncode == 0
        assert "rag options" in result.stdout.lower()
        assert "list" in result.stdout.lower()

    def test_rag_options_list_format(self):
        """Test that rag-options list output is well-formatted."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        # Check for expected format elements
        lines = result.stdout.split("\n")
        assert any("available rag options" in line.lower() for line in lines)

        # Should have multiple sections
        assert "rag types" in result.stdout.lower()
        assert "algorithms" in result.stdout.lower()

    def test_rag_options_list_includes_descriptions(self):
        """Test that rag-options list includes descriptions for options."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        # Check that descriptions are present (indicated by colons)
        assert ":" in result.stdout

        # Check for specific known descriptions
        output_lower = result.stdout.lower()
        # Vector should have description about embeddings
        if "vector" in output_lower:
            assert "embedding" in output_lower or "similarity" in output_lower

    def test_rag_options_list_all_categories_present(self):
        """Test that all expected categories are present in rag-options list."""
        result = self.run_cli("rag-options", "list")
        assert result.returncode == 0

        expected_sections = [
            "rag types",
            "chunking algorithms",
            "embedding algorithms",
            "rerank algorithms",
            "entity extraction algorithms",
            "relationship extraction algorithms",
            "clustering algorithms",
        ]

        output_lower = result.stdout.lower()
        for section in expected_sections:
            assert section in output_lower, f"Missing section: {section}"
