"""E2E tests for RAG configuration combinations and core options."""

import subprocess
import sys

import pytest


@pytest.mark.integration
class TestRAGConfigCombinations:
    """Test all core RAG configuration combinations."""

    def run_cli(self, *args):
        """Helper to run CLI command and return result."""
        cmd = [sys.executable, "-m", "src.cli", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        return result

    # ==================== VECTOR RAG COMBINATIONS ====================

    def test_vector_sentence_chunking_nomic_embedding(self):
        """Test vector RAG with sentence chunking and nomic embedding."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "saved" in result.stdout.lower()

        # Verify the config
        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "vector" in show.stdout.lower()
        assert "sentence" in show.stdout.lower()
        assert "nomic-embed-text" in show.stdout.lower()

    def test_vector_character_chunking_ollama_embedding(self):
        """Test vector RAG with character chunking and ollama embedding."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\ncharacter\n800\n150\nollama\n3\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "character" in show.stdout.lower()
        assert "ollama" in show.stdout.lower()

    def test_vector_semantic_chunking_huggingface_embedding(self):
        """Test vector RAG with semantic chunking and huggingface embedding."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsemantic\n1200\n250\nhuggingface\n7\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "semantic" in show.stdout.lower()
        assert "huggingface" in show.stdout.lower()

    def test_vector_dummy_chunking_dummy_embedding(self):
        """Test vector RAG with dummy chunking and dummy embedding."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\ndummy\n500\n100\ndummy\n2\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "dummy" in show.stdout.lower()

    def test_vector_with_dummy_reranking(self):
        """Test vector RAG with dummy reranking algorithm."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n5\ndummy\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "dummy" in show.stdout.lower() or "rerank" in show.stdout.lower()

    def test_vector_large_chunk_size(self):
        """Test vector RAG with large chunk size."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n2000\n400\nnomic-embed-text\n10\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_vector_small_chunk_size(self):
        """Test vector RAG with small chunk size."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\ncharacter\n100\n20\nnomic-embed-text\n3\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_vector_zero_overlap(self):
        """Test vector RAG with zero overlap."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n0\nnomic-embed-text\n5\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_vector_high_top_k(self):
        """Test vector RAG with high top_k value."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n20\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_vector_top_k_one(self):
        """Test vector RAG with top_k of 1."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n1\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    # ==================== GRAPH RAG COMBINATIONS ====================

    def test_graph_spacy_dependency_leiden(self):
        """Test graph RAG with spacy, dependency-parsing, leiden."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\nspacy\ndependency-parsing\nleiden\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "graph" in show.stdout.lower()
        assert "spacy" in show.stdout.lower()
        assert "dependency-parsing" in show.stdout.lower()
        assert "leiden" in show.stdout.lower()

    def test_graph_dummy_dependency_leiden(self):
        """Test graph RAG with dummy entity extraction."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\ndummy\ndependency-parsing\nleiden\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "graph" in show.stdout.lower()
        assert "dummy" in show.stdout.lower()

    def test_graph_spacy_dummy_leiden(self):
        """Test graph RAG with dummy relationship extraction."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\nspacy\ndummy\nleiden\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "graph" in show.stdout.lower()

    def test_graph_spacy_dependency_dummy_clustering(self):
        """Test graph RAG with dummy clustering."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\nspacy\ndependency-parsing\ndummy\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "graph" in show.stdout.lower()

    def test_graph_all_dummy(self):
        """Test graph RAG with all dummy algorithms."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\ndummy\ndummy\ndummy\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "graph" in show.stdout.lower()

    # ==================== RAG TYPE SWITCHING ====================

    def test_switch_from_vector_to_graph(self):
        """Test switching from vector to graph RAG configuration."""
        # Set vector config
        vector = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
            capture_output=True,
            text=True,
        )
        assert vector.returncode == 0

        # Switch to graph config
        graph = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\nspacy\ndependency-parsing\nleiden\n",
            capture_output=True,
            text=True,
        )
        assert graph.returncode == 0

        # Verify graph is active
        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "graph" in show.stdout.lower()

    def test_switch_from_graph_to_vector(self):
        """Test switching from graph to vector RAG configuration."""
        # Set graph config
        graph = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\nspacy\ndependency-parsing\nleiden\n",
            capture_output=True,
            text=True,
        )
        assert graph.returncode == 0

        # Switch to vector config
        vector = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
            capture_output=True,
            text=True,
        )
        assert vector.returncode == 0

        # Verify vector is active
        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0
        assert "vector" in show.stdout.lower()

    def test_multiple_config_updates(self):
        """Test updating config multiple times."""
        configs = [
            "vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
            "graph\nspacy\ndependency-parsing\nleiden\n",
            "vector\ncharacter\n500\n100\ndummy\n3\nnone\n",
            "graph\ndummy\ndummy\ndummy\n",
        ]

        for config in configs:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
                input=config,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0

    # ==================== DEFAULT VALUE USAGE ====================

    def test_vector_all_defaults(self):
        """Test vector RAG using all default values (empty inputs)."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n\n\nnomic-embed-text\n\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        show = self.run_cli("default-rag-config", "show")
        assert show.returncode == 0

    def test_vector_partial_defaults(self):
        """Test vector RAG using some default values."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1500\n\nnomic-embed-text\n\nnone\n",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    # ==================== CONFIG WITH WORKSPACE CREATION ====================

    def test_create_workspace_after_vector_config(self):
        """Test creating workspace after setting vector config."""
        # Set vector config
        config = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
            capture_output=True,
            text=True,
        )
        assert config.returncode == 0

        # Create workspace with vector type
        workspace = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Vector Workspace\nTest workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert workspace.returncode == 0
        assert "created workspace" in workspace.stdout.lower()

    def test_create_workspace_after_graph_config(self):
        """Test creating workspace after setting graph config."""
        # Set graph config
        config = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\nspacy\ndependency-parsing\nleiden\n",
            capture_output=True,
            text=True,
        )
        assert config.returncode == 0

        # Create workspace with graph type
        workspace = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Graph Workspace\nTest workspace\ngraph\n",
            capture_output=True,
            text=True,
        )
        assert workspace.returncode == 0
        assert "created workspace" in workspace.stdout.lower()

    def test_create_mixed_workspace_types(self):
        """Test creating both vector and graph workspaces."""
        # Set vector config
        vector_config = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
            capture_output=True,
            text=True,
        )
        assert vector_config.returncode == 0

        # Create vector workspace
        vector_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Vector WS\nVector workspace\nvector\n",
            capture_output=True,
            text=True,
        )
        assert vector_ws.returncode == 0

        # Set graph config
        graph_config = subprocess.run(
            [sys.executable, "-m", "src.cli", "default-rag-config", "new"],
            input="graph\nspacy\ndependency-parsing\nleiden\n",
            capture_output=True,
            text=True,
        )
        assert graph_config.returncode == 0

        # Create graph workspace
        graph_ws = subprocess.run(
            [sys.executable, "-m", "src.cli", "workspace", "new"],
            input="Graph WS\nGraph workspace\ngraph\n",
            capture_output=True,
            text=True,
        )
        assert graph_ws.returncode == 0

        # List workspaces
        list_ws = self.run_cli("workspace", "list")
        assert list_ws.returncode == 0
        assert "Vector WS" in list_ws.stdout
        assert "Graph WS" in list_ws.stdout
