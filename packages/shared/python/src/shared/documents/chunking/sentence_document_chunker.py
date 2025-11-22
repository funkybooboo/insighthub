"""Sentence-based document chunking implementation."""

import re

from shared.documents.chunking.document_chunker import Chunker
from shared.types.document import Chunk, Document


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

            # If adding this sentence would exceed chunk_size and we have content
            if (
                current_chunk_length + sentence_length > self._chunk_size
                and current_chunk_sentences
            ):
                # Create chunk from current sentences
                chunk_text = " ".join(current_chunk_sentences)
                chunks.append(
                    Chunk(
                        id=f"{document.id}_chunk_{chunk_index}",
                        document_id=document.id,
                        text=chunk_text,
                        metadata={
                            "chunk_index": str(chunk_index),
                            "start_offset": str(text_offset),
                            "end_offset": str(text_offset + len(chunk_text)),
                            "sentence_count": str(len(current_chunk_sentences)),
                        },
                    )
                )

                # Prepare for next chunk with overlap
                chunk_index += 1
                text_offset += len(chunk_text) - self._overlap

                # Keep sentences for overlap
                overlap_text = ""
                overlap_sentences: list[str] = []
                for s in reversed(current_chunk_sentences):
                    if len(overlap_text) + len(s) <= self._overlap:
                        overlap_sentences.insert(0, s)
                        overlap_text = " ".join(overlap_sentences)
                    else:
                        break

                current_chunk_sentences = overlap_sentences
                current_chunk_length = len(overlap_text)

            # Add sentence to current chunk
            current_chunk_sentences.append(sentence)
            current_chunk_length += sentence_length + 1  # +1 for space

        # Handle remaining sentences
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append(
                Chunk(
                    id=f"{document.id}_chunk_{chunk_index}",
                    document_id=document.id,
                    text=chunk_text,
                    metadata={
                        "chunk_index": str(chunk_index),
                        "start_offset": str(text_offset),
                        "end_offset": str(text_offset + len(chunk_text)),
                        "sentence_count": str(len(current_chunk_sentences)),
                    },
                )
            )

        return chunks

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
