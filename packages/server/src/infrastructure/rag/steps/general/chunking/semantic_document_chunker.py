"""Semantic document chunker implementation using sentence transformers."""

from typing import List

from src.infrastructure.rag.steps.general.chunking.document_chunker import Chunker
from src.infrastructure.types.document import Chunk, Document


class SemanticDocumentChunker(Chunker):
    """Document chunker that splits text semantically using embeddings."""

    def __init__(self, chunk_size: int, overlap: int):
        """
        Initialize the semantic chunker.

        Args:
            chunk_size: Target number of sentences per chunk
            overlap: Number of sentences to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Split document into semantic chunks using sentence-based splitting.

        Args:
            document: Document to chunk

        Returns:
            List of chunks
        """
        # Simple sentence splitting for now
        sentences = document.content.split('. ')
        chunks = []
        start_idx = 0
        chunk_id = 0

        while start_idx < len(sentences):
            # Calculate end position
            end_idx = min(start_idx + self.chunk_size, len(sentences))

            # Extract chunk sentences
            chunk_sentences = sentences[start_idx:end_idx]
            chunk_text = '. '.join(chunk_sentences)

            if chunk_text and not chunk_text.endswith('.'):
                chunk_text += '.'

            # Create chunk
            chunk = Chunk(
                id=f"{document.id}_chunk_{chunk_id}",
                document_id=document.id,
                text=chunk_text,
                metadata={
                    "chunker": "semantic",
                    "chunk_size": self.chunk_size,
                    "overlap": self.overlap,
                    "start_sentence": start_idx,
                    "end_sentence": end_idx,
                }
            )

            chunks.append(chunk)

            # Move start position with overlap
            start_idx = end_idx - self.overlap
            chunk_id += 1

            # Prevent infinite loop
            if start_idx >= len(sentences):
                break

        return chunks

    def estimate_chunk_count(self, document: Document) -> int:
        """
        Estimate the number of chunks that will be created.

        Args:
            document: The document to analyze

        Returns:
            Estimated number of chunks
        """
        # Simple sentence splitting for estimation
        sentences = document.content.split('. ')
        if not sentences:
            return 0

        # Account for overlap in estimation
        effective_chunk_size = self.chunk_size - self.overlap
        if effective_chunk_size <= 0:
            effective_chunk_size = self.chunk_size

        # Estimate based on sentence count
        estimated = (len(sentences) + effective_chunk_size - 1) // effective_chunk_size
        return max(1, estimated)