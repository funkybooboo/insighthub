"""E2E tests for default-rag-config CLI commands."""

import subprocess
import sys

import pytest


@pytest.mark.integration
class TestDefaultRagConfigCLI:
    """End-to-end tests for default-rag-config CLI commands."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    def test_default_rag_config_show(self):
        """Test default-rag-config show command."""
        result = self.run_cli("default-rag-config", "show")
        assert result.returncode == 0
        assert "rag type" in result.stdout.lower()
        # Should show either vector or graph config
        assert (
            "chunking algorithm" in result.stdout.lower()
            or "entity extraction" in result.stdout.lower()
        )

    def test_default_rag_config_new_vector(self):
        """Test default-rag-config new command with vector type."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "saved" in result.stdout.lower()

        # Verify it was saved by showing it
        show_result = self.run_cli("default-rag-config", "show")
        assert show_result.returncode == 0
        assert "vector" in show_result.stdout.lower()
        assert "sentence" in show_result.stdout.lower()
        assert "1000" in show_result.stdout
        assert "200" in show_result.stdout

    def test_default_rag_config_new_graph(self):
        """Test default-rag-config new command with graph type."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\nspacy\ndependency-parsing\nleiden\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "saved" in result.stdout.lower()

        # Verify it was saved by showing it
        show_result = self.run_cli("default-rag-config", "show")
        assert show_result.returncode == 0
        assert "graph" in show_result.stdout.lower()
        assert "spacy" in show_result.stdout.lower()
        assert "dependency-parsing" in show_result.stdout.lower()
        assert "leiden" in show_result.stdout.lower()

    def test_default_rag_config_update_vector_to_graph(self):
        """Test updating default config from vector to graph."""
        # First set to vector
        subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n512\n100\nnomic-embed-text\n3\nnone\n",
            capture_output=True,
            text=True,
        )

        # Then update to graph
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\nspacy\ndependency-parsing\nleiden\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Verify graph config is now active
        show_result = self.run_cli("default-rag-config", "show")
        assert show_result.returncode == 0
        assert "graph" in show_result.stdout.lower()

    def test_default_rag_config_invalid_rag_type(self):
        """Test default-rag-config new with invalid RAG type."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="invalid\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "error" in result.stderr.lower()

    def test_default_rag_config_help(self):
        """Test default-rag-config help command."""
        result = self.run_cli("default-rag-config", "--help")
        assert result.returncode == 0
        assert "default rag" in result.stdout.lower()
        assert "show" in result.stdout.lower()
        assert "new" in result.stdout.lower()

    def test_default_rag_config_auto_create_on_show(self):
        """Test that default config is auto-created if it doesn't exist."""
        # The show command should auto-create config if none exists
        result = self.run_cli("default-rag-config", "show")
        assert result.returncode == 0
        # Should show default vector config
        assert "rag type" in result.stdout.lower()
