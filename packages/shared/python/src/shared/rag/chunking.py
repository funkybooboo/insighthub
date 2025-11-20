"""Character-based text chunking implementation."""

from typing import List

from shared.interfaces.vector.chunker import Chunker
from shared.types.document import Chunk, Document


class CharacterChunker(Chunker):
    """
    Splits documents into fixed-size character chunks.
    
    Simple and fast, but may break sentences at boundaries.
    Good for:
    - Code and technical documents
    - When semantic boundaries are less important
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 0):
        """
        Initialize character chunker.

        Args:
            chunk_size: Target chunk size in characters
            overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Split document into character-based chunks.

        Args:
            document: Document to chunk

        Returns:
            List[Chunk]: List of character chunks
        """
        # TODO: Implement character-based chunking
        # TODO: Handle overlap correctly
        # TODO: Add metadata (position, chunk count, etc.)
        
        # Simple implementation for now
        text = document.content
        chunks = []
        
        for i in range(0, len(text), self.chunk_size - self.overlap):
            end_pos = min(i + self.chunk_size, len(text))
            chunk_text = text[i:end_pos]
            
            chunk = Chunk(
                id=f"{document.id}_chunk_{i // self.chunk_size}",
                document_id=document.id,
                text=chunk_text,
                metadata={
                    "chunk_index": i // self.chunk_size,
                    "start_char": i,
                    "end_char": end_pos,
                    "chunk_strategy": "character",
                    "char_count": len(chunk_text),
                }
            )
            chunks.append(chunk)
        
        return chunks