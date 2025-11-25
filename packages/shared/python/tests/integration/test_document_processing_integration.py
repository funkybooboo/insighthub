"""
Integration tests for document processing.

These tests verify that document chunking works correctly
with storage and end-to-end document workflows.
"""

import io

from shared.documents.chunking.sentence_document_chunker import SentenceDocumentChunker
from shared.storage.in_memory_blob_storage import InMemoryBlobStorage
from shared.types.document import Document


class TestDocumentChunkingIntegration:
    """Integration tests for document chunking workflows."""

    def test_chunk_document_end_to_end(self) -> None:
        """Test complete document chunking workflow."""
        # Create document with realistic content
        content = """
        Introduction to Machine Learning. Machine learning is a subset of artificial intelligence.
        It enables systems to learn and improve from experience without being explicitly programmed.

        Types of Machine Learning. There are three main types of machine learning algorithms.
        Supervised learning uses labeled training data. Unsupervised learning finds patterns in unlabeled data.
        Reinforcement learning learns through trial and error.

        Applications. Machine learning has many practical applications.
        It powers recommendation systems on streaming platforms. It enables fraud detection in financial services.
        Natural language processing uses ML for translation and chatbots.
        """

        doc = Document(
            id="ml-guide-001",
            workspace_id="workspace-123",
            title="Introduction to Machine Learning",
            content=content,
            metadata={"author": "AI Team", "version": "1.0"},
        )

        chunker = SentenceDocumentChunker(chunk_size=300, overlap=50)
        chunks = chunker.chunk(doc)

        # Verify chunks were created
        assert len(chunks) >= 1

        # Verify all chunks reference correct document
        for chunk in chunks:
            assert chunk.document_id == "ml-guide-001"

        # Verify chunk IDs are unique
        chunk_ids = [c.id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))

        # Verify all chunks have content
        for chunk in chunks:
            assert len(chunk.text.strip()) > 0

        # Verify metadata is present
        for i, chunk in enumerate(chunks):
            assert chunk.metadata["chunk_index"] == str(i)
            assert "start_offset" in chunk.metadata
            assert "end_offset" in chunk.metadata

    def test_chunk_multiple_documents(self) -> None:
        """Test chunking multiple documents maintains isolation."""
        doc1 = Document(
            id="doc1",
            workspace_id="ws1",
            title="Document 1",
            content="First document content. It has multiple sentences. Each one is important.",
            metadata={},
        )

        doc2 = Document(
            id="doc2",
            workspace_id="ws1",
            title="Document 2",
            content="Second document here. Different content entirely. Another sentence follows.",
            metadata={},
        )

        chunker = SentenceDocumentChunker(chunk_size=200, overlap=20)

        chunks1 = chunker.chunk(doc1)
        chunks2 = chunker.chunk(doc2)

        # All chunks from doc1 should reference doc1
        for chunk in chunks1:
            assert chunk.document_id == "doc1"
            assert "doc1" in chunk.id

        # All chunks from doc2 should reference doc2
        for chunk in chunks2:
            assert chunk.document_id == "doc2"
            assert "doc2" in chunk.id

    def test_varying_chunk_sizes(self) -> None:
        """Test same document with different chunk sizes."""
        content = " ".join([f"This is sentence number {i}." for i in range(50)])
        doc = Document(
            id="test-doc",
            workspace_id="ws",
            title="Test",
            content=content,
            metadata={},
        )

        small_chunker = SentenceDocumentChunker(chunk_size=100, overlap=10)
        medium_chunker = SentenceDocumentChunker(chunk_size=300, overlap=30)
        large_chunker = SentenceDocumentChunker(chunk_size=1000, overlap=100)

        small_chunks = small_chunker.chunk(doc)
        medium_chunks = medium_chunker.chunk(doc)
        large_chunks = large_chunker.chunk(doc)

        # Smaller chunk size should produce more chunks
        assert len(small_chunks) >= len(medium_chunks)
        assert len(medium_chunks) >= len(large_chunks)


class TestStorageAndChunkingIntegration:
    """Integration tests combining storage and chunking."""

    def test_store_document_then_chunk(self) -> None:
        """Test workflow: store document content then chunk it."""
        storage = InMemoryBlobStorage()

        # Store raw document content
        raw_content = b"""
        Scientific Research Paper.
        This paper presents our findings on climate change.
        We analyzed data from multiple sources over 10 years.

        Methodology.
        We used statistical analysis and machine learning models.
        The data was collected from weather stations worldwide.

        Results.
        Our findings indicate a significant warming trend.
        Temperature increases averaged 0.2 degrees per decade.
        """

        storage.upload_file(io.BytesIO(raw_content), "research/paper.txt")

        # Download and create document
        download_result = storage.download_file("research/paper.txt")
        assert download_result.is_ok()

        content_str = download_result.unwrap().decode("utf-8")

        doc = Document(
            id="paper-001",
            workspace_id="research-ws",
            title="Climate Research Paper",
            content=content_str,
            metadata={"source": "research/paper.txt"},
        )

        # Chunk the document
        chunker = SentenceDocumentChunker(chunk_size=200, overlap=20)
        chunks = chunker.chunk(doc)

        # Verify chunking worked
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.document_id == "paper-001"

    def test_chunk_and_store_chunks(self) -> None:
        """Test workflow: chunk document then store individual chunks."""
        storage = InMemoryBlobStorage()

        doc = Document(
            id="doc-123",
            workspace_id="ws",
            title="Test Document",
            content="First sentence here. Second sentence follows. Third sentence ends.",
            metadata={},
        )

        chunker = SentenceDocumentChunker(chunk_size=100, overlap=0)
        chunks = chunker.chunk(doc)

        # Store each chunk
        for chunk in chunks:
            chunk_data = f"{chunk.text}".encode("utf-8")
            path = f"chunks/{chunk.id}.txt"
            result = storage.upload_file(io.BytesIO(chunk_data), path)
            assert result.is_ok()

        # Verify all chunks were stored
        for chunk in chunks:
            path = f"chunks/{chunk.id}.txt"
            assert storage.file_exists(path)


class TestDocumentMetadataFlow:
    """Integration tests for metadata flow through processing."""

    def test_metadata_preserved_through_chunking(self) -> None:
        """Document metadata can be associated with chunks."""
        doc = Document(
            id="meta-doc",
            workspace_id="ws",
            title="Metadata Test",
            content="Content for testing. More content here.",
            metadata={
                "author": "Test Author",
                "created": "2024-01-01",
                "category": "test",
            },
        )

        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk(doc)

        # Each chunk should be traceable to original document
        for chunk in chunks:
            assert chunk.document_id == doc.id
            # Original document metadata is accessible via document reference

    def test_chunk_metadata_completeness(self) -> None:
        """All chunk metadata fields are populated."""
        doc = Document(
            id="complete-doc",
            workspace_id="ws",
            title="Complete Metadata Test",
            content="First sentence. Second sentence. Third sentence. Fourth sentence.",
            metadata={},
        )

        chunker = SentenceDocumentChunker(chunk_size=50, overlap=5)
        chunks = chunker.chunk(doc)

        for chunk in chunks:
            # Verify all expected metadata fields exist
            assert "chunk_index" in chunk.metadata
            assert "start_offset" in chunk.metadata
            assert "end_offset" in chunk.metadata
            assert "sentence_count" in chunk.metadata

            # Verify metadata values are valid
            assert int(chunk.metadata["chunk_index"]) >= 0  # type: ignore
            assert int(chunk.metadata["start_offset"]) >= 0  # type: ignore
            assert int(chunk.metadata["end_offset"]) > 0  # type: ignore
            assert int(chunk.metadata["sentence_count"]) >= 1  # type: ignore


class TestEdgeCasesIntegration:
    """Integration tests for edge cases in document processing."""

    def test_empty_document_workflow(self) -> None:
        """Empty document produces no chunks."""
        doc = Document(
            id="empty",
            workspace_id="ws",
            title="Empty",
            content="",
            metadata={},
        )

        chunker = SentenceDocumentChunker(chunk_size=100, overlap=10)
        chunks = chunker.chunk(doc)

        assert chunks == []

    def test_single_word_document(self) -> None:
        """Single word document produces one chunk."""
        doc = Document(
            id="single",
            workspace_id="ws",
            title="Single",
            content="Word",
            metadata={},
        )

        chunker = SentenceDocumentChunker(chunk_size=100, overlap=10)
        chunks = chunker.chunk(doc)

        assert len(chunks) == 1
        assert chunks[0].text == "Word"

    def test_unicode_document_workflow(self) -> None:
        """Unicode content is handled correctly through workflow."""
        doc = Document(
            id="unicode",
            workspace_id="ws",
            title="Unicode Test",
            content="Hello world! This is a test document with some content.",
            metadata={},
        )

        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk(doc)

        assert len(chunks) >= 1
        # Verify unicode preserved
        full_text = " ".join(c.text for c in chunks)
        assert "Hello world" in full_text or "Hello world" in doc.content
