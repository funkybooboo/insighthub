"""Sentence-based document chunking implementation."""

import re

from src.infrastructure.rag.steps.general.chunking.document_chunker import Chunker
from src.infrastructure.types.document import Chunk, Document


class SentenceDocumentChunker(Chunker):
    """
    Splits text into chunks based on sentence boundaries.

    Uses regex-based sentence splitting with configurable chunk size and overlap.
    Sentences are grouped together until the chunk size is reached, ensuring
    chunks don't break mid-sentence.

    Example:
        chunker = SentenceDocumentChunker(chunk_size=500, overlap=50)
        chunks = chunker.chunk(document)
    """

    # Sentence splitting pattern - handles common sentence endings
    SENTENCE_PATTERN: re.Pattern[str] = re.compile(
        r"(?<=[.!?])\s+(?=[A-Z])|"  # Standard sentence endings
        r"(?<=[.!?])\s*\n+|"  # Sentence endings followed by newlines
        r"\n{2,}"  # Paragraph breaks
    )

    def __init__(self, chunk_size: int, overlap: int) -> None:
        """
        Initialize sentence chunker.

        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self._chunk_size = chunk_size
        self._overlap = overlap

    def _split_into_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences using regex patterns.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Split on sentence boundaries
        sentences = self.SENTENCE_PATTERN.split(text)

        # Clean up sentences
        cleaned: list[str] = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                cleaned.append(sentence)

        return cleaned

    def chunk(self, document: Document) -> list[Chunk]:
        """
        Split a document into chunks based on sentence boundaries.

        Groups sentences together until chunk_size is reached, then starts
        a new chunk with overlap from previous chunk.

        Args:
            document: The document to chunk

        Returns:
            List of text chunks with metadata
        """
        text = document.content
        if not text or not text.strip():
            return []

        sentences = self._split_into_sentences(text)
        if not sentences:
            return []

        chunks: list[Chunk] = []
        current_chunk_sentences: list[str] = []
        current_chunk_length = 0
        chunk_index = 0
        text_offset = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if self._should_create_chunk(
                current_chunk_length, sentence_length, current_chunk_sentences
            ):
                chunk_text = " ".join(current_chunk_sentences)
                chunk = self._create_chunk(document.id, chunk_index, chunk_text, text_offset)
                chunks.append(chunk)

                chunk_index += 1
                text_offset += len(chunk_text) - self._overlap

                overlap_sentences = self._get_overlap_sentences(current_chunk_sentences)
                current_chunk_sentences = overlap_sentences
                current_chunk_length = len(" ".join(overlap_sentences))

            # Add sentence to current chunk
            current_chunk_sentences.append(sentence)
            current_chunk_length += sentence_length + 1  # +1 for space

        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunk = self._create_chunk(document.id, chunk_index, chunk_text, text_offset)
            chunks.append(chunk)

        return chunks

    def _should_create_chunk(
        self, current_length: int, sentence_length: int, sentences: list[str]
    ) -> bool:
        """Check if we should create a chunk."""
        return current_length + sentence_length > self._chunk_size and len(sentences) > 0

    def _create_chunk(self, doc_id: str, chunk_index: int, text: str, text_offset: int) -> Chunk:
        """Create a chunk with metadata."""
        return Chunk(
            id=f"{doc_id}_chunk_{chunk_index}",
            document_id=doc_id,
            text=text,
            metadata={
                "chunk_index": str(chunk_index),
                "start_offset": str(text_offset),
                "end_offset": str(text_offset + len(text)),
                "sentence_count": str(len(text.split(". "))),
            },
        )

    def _get_overlap_sentences(self, sentences: list[str]) -> list[str]:
        """Get sentences for overlap with next chunk."""
        overlap_text = ""
        overlap_sentences: list[str] = []

        for s in reversed(sentences):
            if len(overlap_text) + len(s) <= self._overlap:
                overlap_sentences.insert(0, s)
                overlap_text = " ".join(overlap_sentences)
            else:
                break

        return overlap_sentences

    def estimate_chunk_count(self, document: Document) -> int:
        """
        Estimate the number of chunks that will be created.

        Args:
            document: The document to analyze

        Returns:
            Estimated number of chunks
        """
        text = document.content
        if not text or not text.strip():
            return 0

        text_length = len(text)

        # Account for overlap in estimation
        effective_chunk_size = self._chunk_size - self._overlap
        if effective_chunk_size <= 0:
            effective_chunk_size = self._chunk_size

        # Estimate based on text length
        estimated = (text_length + effective_chunk_size - 1) // effective_chunk_size
        return max(1, estimated)
