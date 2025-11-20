"""Sentence-based chunking implementation."""

from .interface import Chunker
from shared.types import Chunk, Document


class SentenceChunker(Chunker):
    """Splits text into chunks based on sentence boundaries."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: Document) -> list[Chunk]:
        """Chunk the document into sentences."""
        # TODO: Implement actual sentence splitting logic (e.g. using nltk or spacy)
        text = document.content
        chunks = []
        
        # Dummy implementation
        for i in range(0, len(text), self.chunk_size):
            chunk_text = text[i : i + self.chunk_size]
            chunks.append(
                Chunk(
                    id=f"{document.id}_{i}",
                    document_id=document.id,
                    text=chunk_text,
                    metadata={"start": str(i), "end": str(i + len(chunk_text))},
                )
            )
            
        return chunks
