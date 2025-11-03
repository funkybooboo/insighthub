"""
Text-based chunking implementations
"""

import re

from src.rag.chunking.base import BaseChunker, ChunkingStrategy
from src.rag.types import Chunk, Metadata


class CharacterChunker(BaseChunker):
    """Chunks documents by fixed character count with overlap."""

    def chunk_text(self, text: str, metadata: Metadata | None = None) -> list[Chunk]:
        """Split text into fixed-size character chunks with overlap."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            if chunk.strip():
                chunks.append(chunk)

            start = end - self.chunk_overlap

            # Prevent infinite loop if overlap >= chunk_size
            if self.chunk_overlap >= self.chunk_size:
                start = end

        return self._add_metadata_to_chunks(chunks, metadata)

    @property
    def strategy(self) -> ChunkingStrategy:
        return ChunkingStrategy.CHARACTER


class SentenceChunker(BaseChunker):
    """Chunks documents by sentences, grouping to reach target size."""

    def chunk_text(self, text: str, metadata: Metadata | None = None) -> list[Chunk]:
        """Split text based on sentences, grouping to approximate chunk_size."""
        # Split on sentence boundaries
        sentence_pattern = r"(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$"
        sentences = re.split(sentence_pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks: list[str] = []
        current_chunk: list[str] = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            if current_size + sentence_size > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))

                # Handle overlap by keeping last few sentences
                if self.chunk_overlap > 0:
                    overlap_chunk: list[str] = []
                    overlap_size = 0
                    for sent in reversed(current_chunk):
                        if overlap_size + len(sent) <= self.chunk_overlap:
                            overlap_chunk.insert(0, sent)
                            overlap_size += len(sent)
                        else:
                            break
                    current_chunk = overlap_chunk
                    current_size = overlap_size
                else:
                    current_chunk = []
                    current_size = 0

            current_chunk.append(sentence)
            current_size += sentence_size

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return self._add_metadata_to_chunks(chunks, metadata)

    @property
    def strategy(self) -> ChunkingStrategy:
        return ChunkingStrategy.SENTENCE


class WordChunker(BaseChunker):
    """Chunks documents by word count with overlap."""

    def chunk_text(self, text: str, metadata: Metadata | None = None) -> list[Chunk]:
        """Split text into chunks based on word count."""
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk = " ".join(chunk_words)

            if chunk.strip():
                chunks.append(chunk)

            start = end - self.chunk_overlap

            # Prevent infinite loop
            if self.chunk_overlap >= self.chunk_size:
                start = end

        return self._add_metadata_to_chunks(chunks, metadata)

    @property
    def strategy(self) -> ChunkingStrategy:
        return ChunkingStrategy.WORD


class SemanticChunker(BaseChunker):
    """
    Semantic-based chunking (placeholder for future implementation).
    Will use embeddings to chunk by semantic similarity.
    """

    def chunk_text(self, text: str, metadata: Metadata | None = None) -> list[Chunk]:
        """Placeholder for semantic chunking."""
        raise NotImplementedError(
            "Semantic chunking not yet implemented. "
            "Use CharacterChunker, SentenceChunker, or WordChunker instead."
        )

    @property
    def strategy(self) -> ChunkingStrategy:
        return ChunkingStrategy.SEMANTIC
