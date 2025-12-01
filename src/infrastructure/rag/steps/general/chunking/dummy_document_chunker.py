"""Dummy document chunker for testing."""

from src.infrastructure.rag.steps.general.chunking.document_chunker import Chunker
from src.infrastructure.types.document import Chunk, Document


class DummyDocumentChunker(Chunker):
    """Dummy document chunker that creates simple chunks for testing."""

    def __init__(self, chunk_size: int = 1000) -> None:
        """Initialize with chunk size."""
        self._chunk_size = chunk_size

    def chunk(self, document: Document) -> list[Chunk]:
        """Split document into fixed-size chunks."""
        chunks: list[Chunk] = []
        text = document.content or ""
        if not text.strip():
            return chunks

        # Simple character-based chunking
        for i in range(0, len(text), self._chunk_size):
            chunk_text = text[i : i + self._chunk_size]
            chunk_id = f"{document.id}_chunk_{i // self._chunk_size}"

            chunk = Chunk(
                id=chunk_id,
                document_id=document.id,
                text=chunk_text,
                metadata={
                    "chunk_index": i // self._chunk_size,
                    "start_offset": i,
                    "end_offset": min(i + self._chunk_size, len(text)),
                },
            )
            chunks.append(chunk)

        return chunks

    def estimate_chunk_count(self, document: Document) -> int:
        """Estimate number of chunks."""
        text = document.content or ""
        if not text.strip():
            return 0
        return (len(text) + self._chunk_size - 1) // self._chunk_size
