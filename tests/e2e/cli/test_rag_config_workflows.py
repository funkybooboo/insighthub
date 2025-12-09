"""Comprehensive E2E tests for different RAG configurations with full workflows.

These tests verify that different RAG configurations work end-to-end:
- Create workspace with specific config
- Add document
- Chat with the document

This ensures all RAG options are actually functional in practice.
"""

import re
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.mark.e2e
class TestVectorRAGConfigWorkflows:
    """E2E workflow tests for different Vector RAG configurations."""

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

    @pytest.fixture(scope="class")
    def sample_document(self):
        """Create a sample document for testing (shared across class to reduce memory)."""
        content = """
        Python is a versatile programming language created by Guido van Rossum.
        It was first released in 1991 and has since become one of the most popular languages.
        Python is known for its clear syntax and readability.
        The language supports multiple programming paradigms including procedural, object-oriented, and functional.
        Python has a large standard library and an extensive ecosystem of third-party packages.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    def test_sentence_chunking_nomic_embedding_workflow(self, sample_document):
        """Test full workflow with sentence chunking and nomic embedding."""
        # Set default config
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="Sentence Nomic Test\nSentence chunking with nomic\nvector\n\n\n\n\n\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None
        workspace_id = match.group(1)

        # Add document
        upload_result = self.run_cli(
            "document", "add", sample_document, "--workspace-id", workspace_id
        )
        assert upload_result.returncode == 0

        # Note: Processing happens async, sleep briefly to allow completion
        import time

        time.sleep(1)  # Reduced from 2s to 1s

        # Create chat session
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test Chat\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        # Send query
        query_result = self.run_cli("chat", "send", "Who created Python?")
        assert query_result.returncode == 0
        assert len(query_result.stdout) > 0

    def test_character_chunking_workflow(self, sample_document):
        """Test full workflow with character chunking."""
        # Set config
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="vector\ncharacter\n800\n150\nnomic-embed-text\n5\nnone\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="Character Chunking Test\n\nvector\n\n\n\n\n\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None
        workspace_id = match.group(1)

        # Add document
        upload_result = self.run_cli(
            "document", "add", sample_document, "--workspace-id", workspace_id
        )
        assert upload_result.returncode == 0

        import time

        time.sleep(1)  # Reduced for memory efficiency

        # Create and query
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        query_result = self.run_cli("chat", "send", "What year was Python released?")
        assert query_result.returncode == 0
        assert len(query_result.stdout) > 0

    def test_semantic_chunking_workflow(self, sample_document):
        """Test full workflow with semantic chunking."""
        # Set config
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="vector\nsemantic\n1000\n200\nnomic-embed-text\n5\nnone\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="Semantic Chunking Test\n\nvector\n\n\n\n\n\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None
        workspace_id = match.group(1)

        # Add document
        upload_result = self.run_cli(
            "document", "add", sample_document, "--workspace-id", workspace_id
        )
        assert upload_result.returncode == 0

        import time

        time.sleep(1)  # Reduced for memory efficiency

        # Create and query
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        query_result = self.run_cli(
            "chat", "send", "What programming paradigms does Python support?"
        )
        assert query_result.returncode == 0
        assert len(query_result.stdout) > 0

    def test_token_chunking_workflow(self, sample_document):
        """Test full workflow with token chunking."""
        # Set config
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="vector\ntoken\n500\n100\nnomic-embed-text\n5\nnone\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="Token Chunking Test\n\nvector\n\n\n\n\n\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None
        workspace_id = match.group(1)

        # Add document and query
        upload_result = self.run_cli(
            "document", "add", sample_document, "--workspace-id", workspace_id
        )
        assert upload_result.returncode == 0

        import time

        time.sleep(1)  # Reduced for memory efficiency

        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        query_result = self.run_cli("chat", "send", "Tell me about Python")
        assert query_result.returncode == 0

    def test_vector_with_bm25_reranking_workflow(self, sample_document):
        """Test full workflow with BM25 reranking."""
        # Set config with BM25 reranking
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nbm25\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="BM25 Reranking Test\n\nvector\n\n\n\n\n\nbm25\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None
        workspace_id = match.group(1)

        # Add document
        upload_result = self.run_cli(
            "document", "add", sample_document, "--workspace-id", workspace_id
        )
        assert upload_result.returncode == 0

        import time

        time.sleep(1)  # Reduced for memory efficiency

        # Create chat and query
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        query_result = self.run_cli("chat", "send", "What is Python known for?")
        assert query_result.returncode == 0
        assert len(query_result.stdout) > 0

    def test_vector_with_cross_encoder_reranking_workflow(self, sample_document):
        """Test full workflow with cross-encoder reranking."""
        # Set config with cross-encoder reranking
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="vector\nsentence\n1000\n200\nnomic-embed-text\n5\ncross-encoder\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="CrossEncoder Test\n\nvector\n\n\n\n\n\ncross-encoder\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None
        workspace_id = match.group(1)

        # Add document
        upload_result = self.run_cli(
            "document", "add", sample_document, "--workspace-id", workspace_id
        )
        assert upload_result.returncode == 0

        import time

        time.sleep(1)  # Reduced for memory efficiency

        # Create chat and query
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        query_result = self.run_cli("chat", "send", "Describe Python's ecosystem")
        assert query_result.returncode == 0
        assert len(query_result.stdout) > 0

    def test_vector_with_rrf_reranking_workflow(self, sample_document):
        """Test full workflow with RRF reranking."""
        # Set config with RRF reranking
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nrrf\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="RRF Test\n\nvector\n\n\n\n\n\nrrf\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None
        workspace_id = match.group(1)

        # Add document
        upload_result = self.run_cli(
            "document", "add", sample_document, "--workspace-id", workspace_id
        )
        assert upload_result.returncode == 0

        import time

        time.sleep(1)  # Reduced for memory efficiency

        # Create chat and query
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        query_result = self.run_cli("chat", "send", "What is Python's standard library?")
        assert query_result.returncode == 0
        assert len(query_result.stdout) > 0

    def test_markdown_chunking_workflow(self):
        """Test full workflow with markdown chunking and markdown document."""
        # Create markdown document
        md_content = """
# Python Programming Language

## History
Python was created by Guido van Rossum and released in 1991.

## Features
- Easy to read syntax
- Multiple programming paradigms
- Large standard library

## Popularity
Python is one of the most popular programming languages worldwide.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(md_content)
            doc_path = f.name

        try:
            # Set config
            config_result = self.run_cli(
                "default-rag-config",
                "create",
                input_text="vector\nmarkdown\n1000\n200\nnomic-embed-text\n5\nnone\n",
            )
            assert config_result.returncode == 0

            # Create workspace
            ws_result = self.run_cli(
                "workspace",
                "create",
                input_text="Markdown Chunking Test\n\nvector\nmarkdown\n\n\n\n\n",
            )
            assert ws_result.returncode == 0

            match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
            assert match is not None
            workspace_id = match.group(1)

            # Add document
            upload_result = self.run_cli(
                "document", "add", doc_path, "--workspace-id", workspace_id
            )
            assert upload_result.returncode == 0

            import time

            time.sleep(1)  # Reduced for memory efficiency

            # Create chat and query
            chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
            assert chat_result.returncode == 0

            session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
            assert session_match is not None
            session_id = session_match.group(1)

            self.run_cli("chat", "select", session_id)

            query_result = self.run_cli("chat", "send", "What are Python's features?")
            assert query_result.returncode == 0
            assert len(query_result.stdout) > 0

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_html_chunking_workflow(self):
        """Test full workflow with HTML chunking and HTML document."""
        # Create HTML document
        html_content = """
<!DOCTYPE html>
<html>
<head><title>Python</title></head>
<body>
    <h1>Python Programming</h1>
    <p>Python was created by Guido van Rossum in 1991.</p>
    <h2>Key Features</h2>
    <ul>
        <li>Clear syntax</li>
        <li>Multiple paradigms</li>
        <li>Extensive libraries</li>
    </ul>
</body>
</html>
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(html_content)
            doc_path = f.name

        try:
            # Set config
            config_result = self.run_cli(
                "default-rag-config",
                "create",
                input_text="vector\nhtml\n1000\n200\nnomic-embed-text\n5\nnone\n",
            )
            assert config_result.returncode == 0

            # Create workspace
            ws_result = self.run_cli(
                "workspace",
                "create",
                input_text="HTML Chunking Test\n\nvector\nhtml\n\n\n\n\n",
            )
            assert ws_result.returncode == 0

            match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
            assert match is not None
            workspace_id = match.group(1)

            # Add document
            upload_result = self.run_cli(
                "document", "add", doc_path, "--workspace-id", workspace_id
            )
            assert upload_result.returncode == 0

            import time

            time.sleep(1)  # Reduced for memory efficiency

            # Create chat and query
            chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
            assert chat_result.returncode == 0

            session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
            assert session_match is not None
            session_id = session_match.group(1)

            self.run_cli("chat", "select", session_id)

            query_result = self.run_cli("chat", "send", "Who created Python?")
            assert query_result.returncode == 0
            assert len(query_result.stdout) > 0

        finally:
            Path(doc_path).unlink(missing_ok=True)

    def test_code_chunking_workflow(self):
        """Test full workflow with code chunking and Python code document."""
        # Create Python code document
        code_content = """
def greet(name):
    '''Greet a person by name.

    Args:
        name: The person's name

    Returns:
        A greeting string
    '''
    return f"Hello, {name}!"

class Calculator:
    '''A simple calculator class.'''

    def add(self, a, b):
        '''Add two numbers.'''
        return a + b

    def subtract(self, a, b):
        '''Subtract b from a.'''
        return a - b

# Main execution
if __name__ == "__main__":
    calc = Calculator()
    result = calc.add(5, 3)
    print(greet("Python"))
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code_content)
            doc_path = f.name

        try:
            # Set config
            config_result = self.run_cli(
                "default-rag-config",
                "create",
                input_text="vector\ncode\n1000\n200\nnomic-embed-text\n5\nnone\n",
            )
            assert config_result.returncode == 0

            # Create workspace
            ws_result = self.run_cli(
                "workspace",
                "create",
                input_text="Code Chunking Test\n\nvector\ncode\n\n\n\n\n",
            )
            assert ws_result.returncode == 0

            match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
            assert match is not None
            workspace_id = match.group(1)

            # Add document
            upload_result = self.run_cli(
                "document", "add", doc_path, "--workspace-id", workspace_id
            )
            assert upload_result.returncode == 0

            import time

            time.sleep(1)  # Reduced for memory efficiency

            # Create chat and query
            chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
            assert chat_result.returncode == 0

            session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
            assert session_match is not None
            session_id = session_match.group(1)

            self.run_cli("chat", "select", session_id)

            query_result = self.run_cli("chat", "send", "What does the Calculator class do?")
            assert query_result.returncode == 0
            assert len(query_result.stdout) > 0

        finally:
            Path(doc_path).unlink(missing_ok=True)


@pytest.mark.e2e
class TestGraphRAGConfigWorkflows:
    """E2E workflow tests for different Graph RAG configurations."""

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

    @pytest.fixture(scope="class")
    def entity_document(self):
        """Create a document rich in entities for graph RAG testing (shared across class)."""
        content = """
        Apple Inc was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.
        The company is headquartered in Cupertino, California.
        Tim Cook became the CEO of Apple in 2011 after Steve Jobs.
        Apple develops the iPhone, which was first released in 2007.
        Steve Jobs also co-founded Pixar Animation Studios.
        Pixar is located in Emeryville, California.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    def test_spacy_dependency_leiden_workflow(self, entity_document):
        """Test full workflow with spacy entity extraction, dependency parsing, and leiden clustering."""
        # Set config
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="graph\nspacy\ndependency-parsing\nleiden\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="Spacy Dep Leiden Test\n\ngraph\nspacy\ndependency-parsing\nleiden\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None
        workspace_id = match.group(1)

        # Select workspace
        self.run_cli("workspace", "select", workspace_id)

        # Add document
        upload_result = self.run_cli("document", "add", entity_document)
        assert upload_result.returncode == 0

        import time

        time.sleep(2)  # Graph processing (reduced for memory)

        # Create chat session
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        # Query about entities
        query_result = self.run_cli("chat", "send", "Who founded Apple?")
        assert query_result.returncode == 0
        assert len(query_result.stdout) > 0

    def test_spacy_dependency_louvain_workflow(self, entity_document):
        """Test full workflow with spacy, dependency parsing, and louvain clustering."""
        # Set config
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="graph\nspacy\ndependency-parsing\nlouvain\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="Spacy Dep Louvain Test\n\ngraph\nspacy\ndependency-parsing\nlouvain\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        assert match is not None
        workspace_id = match.group(1)

        self.run_cli("workspace", "select", workspace_id)

        # Add document
        upload_result = self.run_cli("document", "add", entity_document)
        assert upload_result.returncode == 0

        import time

        time.sleep(2)  # Reduced for memory efficiency

        # Create chat and query
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        query_result = self.run_cli("chat", "send", "Where is Apple located?")
        assert query_result.returncode == 0
        assert len(query_result.stdout) > 0

    def test_llm_entity_dependency_leiden_workflow(self, entity_document):
        """Test full workflow with LLM entity extraction, dependency parsing, and leiden."""
        # Set config
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="graph\nllm\ndependency-parsing\nleiden\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="LLM Entity Test\n\ngraph\nllm\ndependency-parsing\nleiden\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        if match is None:
            pytest.skip("Could not create workspace - LLM provider may not be configured")

        workspace_id = match.group(1)
        self.run_cli("workspace", "select", workspace_id)

        # Add document (may skip if LLM not configured)
        upload_result = self.run_cli("document", "add", entity_document)

        if upload_result.returncode != 0:
            if "llm_provider is required" in upload_result.stderr.lower():
                pytest.skip("LLM provider not configured for graph RAG")

        assert upload_result.returncode == 0

        import time

        time.sleep(2)  # Reduced for memory efficiency

        # Create chat and query
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        query_result = self.run_cli("chat", "send", "Who is the CEO of Apple?")
        assert query_result.returncode == 0

    def test_spacy_llm_relationship_leiden_workflow(self, entity_document):
        """Test full workflow with spacy entities, LLM relationship extraction, and leiden."""
        # Set config
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="graph\nspacy\nllm\nleiden\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="Spacy LLM Rel Test\n\ngraph\nspacy\nllm\nleiden\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        if match is None:
            pytest.skip("Could not create workspace - LLM provider may not be configured")

        workspace_id = match.group(1)
        self.run_cli("workspace", "select", workspace_id)

        # Add document
        upload_result = self.run_cli("document", "add", entity_document)

        if upload_result.returncode != 0:
            if "llm_provider is required" in upload_result.stderr.lower():
                pytest.skip("LLM provider not configured for graph RAG")

        assert upload_result.returncode == 0

        import time

        time.sleep(2)  # Reduced for memory efficiency

        # Create chat and query
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        query_result = self.run_cli("chat", "send", "What companies did Steve Jobs found?")
        assert query_result.returncode == 0

    def test_all_llm_workflow(self, entity_document):
        """Test full workflow with all LLM-based extraction methods."""
        # Set config
        config_result = self.run_cli(
            "default-rag-config",
            "create",
            input_text="graph\nllm\nllm\nlouvain\n",
        )
        assert config_result.returncode == 0

        # Create workspace
        ws_result = self.run_cli(
            "workspace",
            "create",
            input_text="All LLM Test\n\ngraph\nllm\nllm\nlouvain\n",
        )
        assert ws_result.returncode == 0

        match = re.search(r"Created workspace \[(\d+)\]", ws_result.stdout)
        if match is None:
            pytest.skip("Could not create workspace - LLM provider may not be configured")

        workspace_id = match.group(1)
        self.run_cli("workspace", "select", workspace_id)

        # Add document
        upload_result = self.run_cli("document", "add", entity_document)

        if upload_result.returncode != 0:
            if "llm_provider is required" in upload_result.stderr.lower():
                pytest.skip("LLM provider not configured for graph RAG")

        assert upload_result.returncode == 0

        import time

        time.sleep(2)  # LLM processing (reduced for memory)

        # Create chat and query
        chat_result = self.run_cli("chat", "create", workspace_id, input_text="Test\n")
        assert chat_result.returncode == 0

        session_match = re.search(r"Created chat session \[(\d+)\]", chat_result.stdout)
        assert session_match is not None
        session_id = session_match.group(1)

        self.run_cli("chat", "select", session_id)

        query_result = self.run_cli("chat", "send", "Tell me about Apple's history")
        assert query_result.returncode == 0


@pytest.mark.e2e
class TestRAGConfigSwitching:
    """Test switching between different RAG configurations in workflows."""

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

    @pytest.fixture(scope="class")
    def test_document(self):
        """Create a test document (shared across class)."""
        content = "Machine learning is a subset of artificial intelligence."
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink(missing_ok=True)

    def test_create_vector_then_graph_workspaces(self, test_document):
        """Test creating vector workspace then graph workspace with documents."""
        # Create vector workspace
        vector_config = self.run_cli(
            "default-rag-config",
            "create",
            input_text="vector\nsentence\n1000\n200\nnomic-embed-text\n5\nnone\n",
        )
        assert vector_config.returncode == 0

        vector_ws = self.run_cli(
            "workspace",
            "create",
            input_text="Vector Workspace\n\nvector\n\n\n\n\n\n",
        )
        assert vector_ws.returncode == 0

        v_match = re.search(r"Created workspace \[(\d+)\]", vector_ws.stdout)
        assert v_match is not None
        v_workspace_id = v_match.group(1)

        # Add document to vector workspace
        v_upload = self.run_cli("document", "add", test_document, "--workspace-id", v_workspace_id)
        assert v_upload.returncode == 0

        # Create graph workspace
        graph_config = self.run_cli(
            "default-rag-config",
            "create",
            input_text="graph\nspacy\ndependency-parsing\nleiden\n",
        )
        assert graph_config.returncode == 0

        graph_ws = self.run_cli(
            "workspace",
            "create",
            input_text="Graph Workspace\n\ngraph\nspacy\ndependency-parsing\nleiden\n",
        )
        assert graph_ws.returncode == 0

        g_match = re.search(r"Created workspace \[(\d+)\]", graph_ws.stdout)
        assert g_match is not None
        g_workspace_id = g_match.group(1)

        # Add document to graph workspace
        self.run_cli("workspace", "select", g_workspace_id)
        g_upload = self.run_cli("document", "add", test_document)
        assert g_upload.returncode == 0

        # Verify both workspaces exist
        list_result = self.run_cli("workspace", "list")
        assert list_result.returncode == 0
        assert v_workspace_id in list_result.stdout or "Vector Workspace" in list_result.stdout
        assert g_workspace_id in list_result.stdout or "Graph Workspace" in list_result.stdout
