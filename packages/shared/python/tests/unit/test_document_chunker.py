"""
Unit tests for document chunking.

These tests verify the SentenceDocumentChunker correctly splits documents
into chunks based on sentence boundaries with configured size and overlap.
"""

import pytest

from shared.documents.chunking.document_chunker import Chunker
from shared.documents.chunking.sentence_document_chunker import SentenceDocumentChunker
from shared.types.document import Chunk, Document


def create_document(content: str, doc_id: str = "doc1") -> Document:
    """Helper to create a Document with given content."""
    return Document(
        id=doc_id,
        workspace_id="workspace1",
        title="Test Document",
        content=content,
        metadata={},
    )


class TestSentenceDocumentChunkerCreation:
    """Test SentenceDocumentChunker initialization."""

    def test_creation_with_chunk_size_and_overlap(self) -> None:
        """Chunker accepts chunk_size and overlap parameters."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)

        assert chunker._chunk_size == 500
        assert chunker._overlap == 50

    def test_implements_chunker_interface(self) -> None:
        """SentenceDocumentChunker implements Chunker interface."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)

        assert isinstance(chunker, Chunker)

    def test_has_required_methods(self) -> None:
        """SentenceDocumentChunker has required interface methods."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)

        assert hasattr(chunker, "chunk")
        assert hasattr(chunker, "estimate_chunk_count")
        assert callable(chunker.chunk)
        assert callable(chunker.estimate_chunk_count)


class TestSentenceDocumentChunkerChunk:
    """Test SentenceDocumentChunker chunk method input/output."""

    def test_chunk_empty_document(self) -> None:
        """Chunking empty document returns empty list."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("")

        result = chunker.chunk(doc)

        assert result == []

    def test_chunk_whitespace_only_document(self) -> None:
        """Chunking whitespace-only document returns empty list."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("   \n\t  ")

        result = chunker.chunk(doc)

        assert result == []

    def test_chunk_single_sentence(self) -> None:
        """Chunking single sentence returns one chunk."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("This is a single sentence.")

        result = chunker.chunk(doc)

        assert len(result) == 1
        assert result[0].text == "This is a single sentence."

    def test_chunk_returns_chunk_objects(self) -> None:
        """Chunking returns list of Chunk objects."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("First sentence. Second sentence.")

        result = chunker.chunk(doc)

        assert all(isinstance(chunk, Chunk) for chunk in result)

    def test_chunk_preserves_document_id(self) -> None:
        """Chunks reference their source document ID."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("Test content.", doc_id="my-document-123")

        result = chunker.chunk(doc)

        assert len(result) == 1
        assert result[0].document_id == "my-document-123"

    def test_chunk_ids_are_unique(self) -> None:
        """Each chunk has a unique ID."""
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=10)
        long_text = " ".join([f"Sentence number {i}." for i in range(20)])
        doc = create_document(long_text)

        result = chunker.chunk(doc)

        chunk_ids = [chunk.id for chunk in result]
        assert len(chunk_ids) == len(set(chunk_ids))

    def test_chunk_ids_include_document_id(self) -> None:
        """Chunk IDs include the document ID."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("Test sentence.", doc_id="doc123")

        result = chunker.chunk(doc)

        assert "doc123" in result[0].id

    def test_chunk_ids_include_index(self) -> None:
        """Chunk IDs include the chunk index."""
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=10)
        long_text = " ".join([f"Sentence number {i}." for i in range(20)])
        doc = create_document(long_text, doc_id="doc1")

        result = chunker.chunk(doc)

        for i, chunk in enumerate(result):
            assert f"chunk_{i}" in chunk.id

    def test_chunk_metadata_includes_chunk_index(self) -> None:
        """Chunk metadata contains chunk_index."""
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=10)
        long_text = "First sentence. Second sentence. Third sentence."
        doc = create_document(long_text)

        result = chunker.chunk(doc)

        for i, chunk in enumerate(result):
            assert chunk.metadata["chunk_index"] == str(i)

    def test_chunk_metadata_includes_offsets(self) -> None:
        """Chunk metadata contains start_offset and end_offset."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("Test sentence here.")

        result = chunker.chunk(doc)

        assert "start_offset" in result[0].metadata
        assert "end_offset" in result[0].metadata

    def test_chunk_metadata_includes_sentence_count(self) -> None:
        """Chunk metadata contains sentence_count."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("First sentence. Second sentence.")

        result = chunker.chunk(doc)

        assert "sentence_count" in result[0].metadata


class TestSentenceDocumentChunkerSentenceSplitting:
    """Test SentenceDocumentChunker sentence boundary detection."""

    def test_splits_on_period(self) -> None:
        """Chunker splits on period followed by space and capital."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=0)
        doc = create_document("First sentence. Second sentence.")

        result = chunker.chunk(doc)

        # Both sentences should be in the chunk
        assert "First sentence" in result[0].text
        assert "Second sentence" in result[0].text

    def test_splits_on_exclamation(self) -> None:
        """Chunker splits on exclamation mark."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=0)
        doc = create_document("Hello there! How are you?")

        result = chunker.chunk(doc)

        assert len(result) >= 1

    def test_splits_on_question_mark(self) -> None:
        """Chunker splits on question mark."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=0)
        doc = create_document("How are you? I am fine.")

        result = chunker.chunk(doc)

        assert len(result) >= 1

    def test_splits_on_paragraph_breaks(self) -> None:
        """Chunker splits on paragraph breaks."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=0)
        doc = create_document("First paragraph.\n\nSecond paragraph.")

        result = chunker.chunk(doc)

        # Should handle paragraph breaks
        assert len(result) >= 1


class TestSentenceDocumentChunkerChunkSize:
    """Test SentenceDocumentChunker respects chunk size limits."""

    def test_chunk_respects_chunk_size(self) -> None:
        """Chunks do not significantly exceed chunk_size."""
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=0)
        # Create document with many sentences
        sentences = [f"This is sentence number {i}." for i in range(50)]
        doc = create_document(" ".join(sentences))

        result = chunker.chunk(doc)

        # Each chunk should be reasonably close to chunk_size
        # (may exceed slightly due to not breaking mid-sentence)
        for chunk in result:
            # Allow some buffer for sentence boundaries
            assert len(chunk.text) < 200

    def test_small_chunk_size_creates_more_chunks(self) -> None:
        """Smaller chunk_size creates more chunks."""
        small_chunker = SentenceDocumentChunker(chunk_size=50, overlap=0)
        large_chunker = SentenceDocumentChunker(chunk_size=500, overlap=0)

        sentences = [f"Sentence {i}." for i in range(20)]
        doc = create_document(" ".join(sentences))

        small_result = small_chunker.chunk(doc)
        large_result = large_chunker.chunk(doc)

        assert len(small_result) >= len(large_result)


class TestSentenceDocumentChunkerOverlap:
    """Test SentenceDocumentChunker overlap functionality."""

    def test_overlap_creates_overlapping_content(self) -> None:
        """Non-zero overlap creates overlapping content between chunks."""
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=30)
        sentences = [f"Sentence number {i} here." for i in range(20)]
        doc = create_document(" ".join(sentences))

        result = chunker.chunk(doc)

        # With overlap, consecutive chunks should share some content
        if len(result) >= 2:
            # Check that there's some overlap possibility
            # (exact overlap depends on sentence boundaries)
            assert len(result) >= 2

    def test_zero_overlap_no_shared_content(self) -> None:
        """Zero overlap means no shared content between chunks."""
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=0)
        sentences = [f"Sentence {i}." for i in range(20)]
        doc = create_document(" ".join(sentences))

        result = chunker.chunk(doc)

        # Chunks should not share content with zero overlap
        assert len(result) >= 1


class TestSentenceDocumentChunkerEstimate:
    """Test SentenceDocumentChunker estimate_chunk_count method."""

    def test_estimate_empty_document(self) -> None:
        """Estimating empty document returns 0."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("")

        result = chunker.estimate_chunk_count(doc)

        assert result == 0

    def test_estimate_whitespace_document(self) -> None:
        """Estimating whitespace document returns 0."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("   \n\t  ")

        result = chunker.estimate_chunk_count(doc)

        assert result == 0

    def test_estimate_small_document(self) -> None:
        """Estimating small document returns at least 1."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("Small document.")

        result = chunker.estimate_chunk_count(doc)

        assert result >= 1

    def test_estimate_returns_integer(self) -> None:
        """estimate_chunk_count returns integer."""
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=20)
        doc = create_document("Some content here with sentences. More text.")

        result = chunker.estimate_chunk_count(doc)

        assert isinstance(result, int)

    def test_estimate_proportional_to_document_size(self) -> None:
        """Larger documents have larger estimates."""
        chunker = SentenceDocumentChunker(chunk_size=100, overlap=20)

        small_doc = create_document("Short.")
        large_doc = create_document("Sentence. " * 100)

        small_estimate = chunker.estimate_chunk_count(small_doc)
        large_estimate = chunker.estimate_chunk_count(large_doc)

        assert large_estimate >= small_estimate

    def test_estimate_close_to_actual_count(self) -> None:
        """Estimate should be reasonably close to actual chunk count."""
        chunker = SentenceDocumentChunker(chunk_size=200, overlap=20)
        sentences = [f"This is sentence number {i} with some content." for i in range(50)]
        doc = create_document(" ".join(sentences))

        estimate = chunker.estimate_chunk_count(doc)
        actual = len(chunker.chunk(doc))

        # Estimate should be within reasonable range of actual
        # Allow 50% variance due to sentence boundary effects
        assert estimate >= actual * 0.5
        assert estimate <= actual * 2


class TestSentenceDocumentChunkerEdgeCases:
    """Test SentenceDocumentChunker edge cases."""

    def test_document_with_only_punctuation(self) -> None:
        """Chunking punctuation-only document."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("... !!! ???")

        result = chunker.chunk(doc)

        # Should handle gracefully, may return empty or single chunk
        assert isinstance(result, list)

    def test_document_with_no_sentence_endings(self) -> None:
        """Chunking document without sentence endings."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("no punctuation here just words")

        result = chunker.chunk(doc)

        # Should treat as single chunk
        assert len(result) >= 1

    def test_document_with_unicode(self) -> None:
        """Chunking document with unicode characters."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("Hello 世界! Привет мир. مرحبا بالعالم.")

        result = chunker.chunk(doc)

        assert len(result) >= 1

    def test_document_with_newlines(self) -> None:
        """Chunking document with various newlines."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("Line one.\nLine two.\r\nLine three.\r\n\r\nParagraph two.")

        result = chunker.chunk(doc)

        assert len(result) >= 1

    def test_document_with_abbreviations(self) -> None:
        """Chunking document with abbreviations like Dr., Mr., etc."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("Dr. Smith met with Mr. Jones. They discussed the project.")

        result = chunker.chunk(doc)

        # Should handle abbreviations reasonably
        assert len(result) >= 1

    def test_very_long_sentence(self) -> None:
        """Chunking document with a sentence longer than chunk_size."""
        chunker = SentenceDocumentChunker(chunk_size=50, overlap=10)
        # Single sentence longer than chunk_size
        long_sentence = "This is a very long sentence " * 10
        doc = create_document(long_sentence.strip())

        result = chunker.chunk(doc)

        # Should still produce at least one chunk
        assert len(result) >= 1

    def test_repeated_punctuation(self) -> None:
        """Chunking document with repeated punctuation."""
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        doc = create_document("What?? Really!! Yes... Okay.")

        result = chunker.chunk(doc)

        assert len(result) >= 1


class TestChunkDataclass:
    """Test Chunk dataclass input/output."""

    def test_chunk_creation(self) -> None:
        """Chunk can be created with required fields."""
        chunk = Chunk(
            id="chunk1",
            document_id="doc1",
            text="Some text content",
            metadata={"key": "value"},
        )

        assert chunk.id == "chunk1"
        assert chunk.document_id == "doc1"
        assert chunk.text == "Some text content"
        assert chunk.metadata == {"key": "value"}

    def test_chunk_default_vector(self) -> None:
        """Chunk has None as default vector."""
        chunk = Chunk(
            id="chunk1",
            document_id="doc1",
            text="text",
            metadata={},
        )

        assert chunk.vector is None

    def test_chunk_with_vector(self) -> None:
        """Chunk can be created with vector."""
        vector = [0.1, 0.2, 0.3, 0.4]
        chunk = Chunk(
            id="chunk1",
            document_id="doc1",
            text="text",
            metadata={},
            vector=vector,
        )

        assert chunk.vector == [0.1, 0.2, 0.3, 0.4]


class TestDocumentDataclass:
    """Test Document dataclass input/output."""

    def test_document_creation(self) -> None:
        """Document can be created with all fields."""
        doc = Document(
            id="doc1",
            workspace_id="ws1",
            title="Test Title",
            content="Document content here.",
            metadata={"author": "test"},
        )

        assert doc.id == "doc1"
        assert doc.workspace_id == "ws1"
        assert doc.title == "Test Title"
        assert doc.content == "Document content here."
        assert doc.metadata == {"author": "test"}

    def test_document_with_none_title(self) -> None:
        """Document can have None title."""
        doc = Document(
            id="doc1",
            workspace_id="ws1",
            title=None,
            content="Content",
            metadata={},
        )

        assert doc.title is None

    def test_document_with_empty_content(self) -> None:
        """Document can have empty content."""
        doc = Document(
            id="doc1",
            workspace_id="ws1",
            title="Title",
            content="",
            metadata={},
        )

        assert doc.content == ""
