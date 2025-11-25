"""Semantic document chunker implementation using sentence transformers."""

from typing import List

from shared.documents.chunking.document_chunker import Chunker
from shared.types.document import Chunk, Document


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
        Split document into semantic chunks.

        For now, this is a simple sentence-based implementation.
        TODO: Implement proper semantic chunking using embeddings.

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