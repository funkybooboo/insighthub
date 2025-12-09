"""Unit tests for CharacterDocumentChunker."""

from src.infrastructure.rag.steps.general.chunking.character_document_chunker import (
    CharacterDocumentChunker,
)
from src.infrastructure.types.document import Document


class TestCharacterDocumentChunker:
    """Unit tests for CharacterDocumentChunker."""

    def test_chunk_no_overlap(self):
        """Test basic chunking with no overlap."""
        chunker = CharacterDocumentChunker(chunk_size=10, overlap=0)
        document = Document(
            id="doc1", workspace_id="ws1", title="Test Document", content="This is a test sentence."
        )
        chunks = chunker.chunk(document)
        assert len(chunks) == 3
        assert chunks[0].text == "This is a "
        assert chunks[1].text == "test sente"
        assert chunks[2].text == "nce."

    def test_chunk_with_overlap(self):
        """Test chunking with overlap."""
        chunker = CharacterDocumentChunker(chunk_size=10, overlap=2)
        document = Document(
            id="doc1", workspace_id="ws1", title="Test Document", content="This is a test sentence."
        )
        chunks = chunker.chunk(document)
        assert len(chunks) == 3
        assert chunks[0].text == "This is a "
        assert chunks[1].text == "a test sen"
        assert chunks[2].text == "entence."

    def test_chunk_smaller_than_chunk_size(self):
        """Test chunking of text smaller than the chunk size."""
        chunker = CharacterDocumentChunker(chunk_size=100, overlap=10)
        document = Document(
            id="doc1", workspace_id="ws1", title="Test Document", content="Short text."
        )
        chunks = chunker.chunk(document)
        assert len(chunks) == 1
        assert chunks[0].text == "Short text."

    def test_chunk_empty_text(self):
        """Test chunking of empty text."""
        chunker = CharacterDocumentChunker(chunk_size=10, overlap=0)
        document = Document(id="doc1", workspace_id="ws1", title="Test Document", content="")
        chunks = chunker.chunk(document)
        assert len(chunks) == 0

    def test_estimate_chunk_count(self):
        """Test estimation of chunk count."""
        chunker = CharacterDocumentChunker(chunk_size=10, overlap=2)
        document = Document(
            id="doc1", workspace_id="ws1", title="Test Document", content="This is a test sentence."
        )
        estimated_chunks = chunker.estimate_chunk_count(document)
        assert estimated_chunks == 3

    def test_estimate_chunk_count_no_overlap(self):
        """Test estimation of chunk count with no overlap."""
        chunker = CharacterDocumentChunker(chunk_size=10, overlap=0)
        document = Document(
            id="doc1", workspace_id="ws1", title="Test Document", content="This is a test sentence."
        )
        estimated_chunks = chunker.estimate_chunk_count(document)
        assert estimated_chunks == 3

    def test_estimate_chunk_count_empty_text(self):
        """Test estimation of chunk count for empty text."""
        chunker = CharacterDocumentChunker(chunk_size=10, overlap=0)
        document = Document(id="doc1", workspace_id="ws1", title="Test Document", content="")
        estimated_chunks = chunker.estimate_chunk_count(document)
        assert estimated_chunks == 0
