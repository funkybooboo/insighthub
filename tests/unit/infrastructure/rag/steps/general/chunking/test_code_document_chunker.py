"""Unit tests for CodeDocumentChunker."""

from src.infrastructure.rag.steps.general.chunking.code_document_chunker import CodeDocumentChunker
from src.infrastructure.types.document import Document


class TestCodeDocumentChunker:
    """Unit tests for CodeDocumentChunker."""

    def test_chunk_python_file(self):
        """Test chunking a simple Python file."""
        code = """class MyClass:
    def __init__(self):
        self.x = 1

    def my_method(self, y):
        return self.x + y

def my_function(a, b):
    return a * b"""
        chunker = CodeDocumentChunker(chunk_size=100, overlap=0)
        document = Document(id="doc1", workspace_id="ws1", title="Test Code", content=code)
        chunks = chunker.chunk(document)
        assert len(chunks) == 2
        assert "class MyClass" in chunks[0].text
        assert "def my_method" in chunks[0].text
        assert "def my_function" in chunks[1].text

    def test_chunk_no_blocks(self):
        """Test fallback to line-based chunking."""
        text = "line 1\nline 2\nline 3\n" * 20
        chunker = CodeDocumentChunker(chunk_size=50, overlap=0)
        document = Document(id="doc1", workspace_id="ws1", title="Test Text", content=text)
        chunks = chunker.chunk(document)
        assert len(chunks) > 1
        assert "line 1" in chunks[0].text

    def test_chunk_large_function(self):
        """Test chunking a function larger than chunk_size."""
        code = """
def large_function():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8
    i = 9
    j = 10
    k = 11
    l = 12
    m = 13
    n = 14
    o = 15
"""
        chunker = CodeDocumentChunker(chunk_size=50, overlap=0)
        document = Document(id="doc1", workspace_id="ws1", title="Test Code", content=code)
        chunks = chunker.chunk(document)
        assert len(chunks) > 1
        assert "def large_function" in chunks[0].text

    def test_chunk_empty_file(self):
        """Test chunking an empty file."""
        chunker = CodeDocumentChunker(chunk_size=100, overlap=0)
        document = Document(id="doc1", workspace_id="ws1", title="Empty", content="")
        chunks = chunker.chunk(document)
        assert len(chunks) == 0

    def test_estimate_chunk_count(self):
        """Test estimation of chunk count."""
        code = "class MyClass:\n    pass\n\ndef my_function():\n    pass"
        chunker = CodeDocumentChunker(chunk_size=100, overlap=0)
        document = Document(id="doc1", workspace_id="ws1", title="Test Code", content=code)
        estimated_chunks = chunker.estimate_chunk_count(document)
        assert estimated_chunks >= 1

    def test_find_code_blocks(self):
        """Test the _find_code_blocks method."""
        code = """class MyClass:
    def __init__(self):
        pass

def my_function():
    pass"""
        chunker = CodeDocumentChunker(chunk_size=100, overlap=0)
        blocks = chunker._find_code_blocks(code)
        assert len(blocks) == 3
        assert blocks[0]["type"] == "class"
        assert blocks[0]["name"] == "MyClass"
        assert blocks[1]["type"] == "function"
        assert blocks[1]["name"] == "__init__"
        assert blocks[2]["type"] == "function"
        assert blocks[2]["name"] == "my_function"
