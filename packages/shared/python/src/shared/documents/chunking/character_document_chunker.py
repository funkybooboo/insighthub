"""Character-based document chunker implementation."""

from typing import List

from shared.documents.chunking.document_chunker import Chunker
from shared.types.document import Chunk, Document


class CharacterDocumentChunker(Chunker):
    """Document chunker that splits text by character count."""

    def __init__(self, chunk_size: int, overlap: int):
        """
        Initialize the character chunker.

        Args:
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Split document into chunks by character count.

        Args:
            document: Document to chunk

        Returns:
            List of chunks
        """
        chunks = []
        text = document.content
        start = 0
        chunk_id = 0

        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))

            # Extract chunk text
            chunk_text = text[start:end]

            # Create chunk
            chunk = Chunk(
                id=f"{document.id}_chunk_{chunk_id}",
                document_id=document.id,
                text=chunk_text,
                metadata={
                    "chunker": "character",
                    "chunk_size": self.chunk_size,
                    "overlap": self.overlap,
                    "start_char": start,
                    "end_char": end,
                }
            )

            chunks.append(chunk)

            # Move start position with overlap
            start = end - self.overlap
            chunk_id += 1

            # Prevent infinite loop
            if start >= len(text):
                break

        return chunks