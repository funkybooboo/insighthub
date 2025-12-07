"""Token-based document chunker implementation."""

import re

from src.infrastructure.rag.steps.general.chunking.document_chunker import Chunker
from src.infrastructure.types.document import Chunk, Document


class TokenDocumentChunker(Chunker):
    """
    Splits text into chunks based on token count.

    Uses simple whitespace-based tokenization to approximate token boundaries.
    Configurable chunk size and overlap measured in tokens.
    """

    # Simple token pattern - splits on whitespace and punctuation
    TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]")

    def __init__(self, chunk_size: int, overlap: int) -> None:
        """
        Initialize token chunker.

        Args:
            chunk_size: Target number of tokens per chunk
            overlap: Number of tokens to overlap between chunks
        """
        self._chunk_size = chunk_size
        self._overlap = overlap

    def _tokenize(self, text: str) -> list[str]:
        """
        Tokenize text into tokens.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        return self.TOKEN_PATTERN.findall(text)

    def chunk(self, document: Document) -> list[Chunk]:
        """
        Split a document into chunks based on token count.

        Args:
            document: The document to chunk

        Returns:
            List of text chunks with metadata
        """
        text = document.content
        if not text or not text.strip():
            return []

        tokens = self._tokenize(text)
        if not tokens:
            return []

        chunks: list[Chunk] = []
        chunk_index = 0
        start_idx = 0

        while start_idx < len(tokens):
            # Calculate end index
            end_idx = min(start_idx + self._chunk_size, len(tokens))

            # Extract chunk tokens and reconstruct text
            chunk_tokens = tokens[start_idx:end_idx]
            chunk_text = self._reconstruct_text(chunk_tokens)

            # Create chunk
            chunk = Chunk(
                id=f"{document.id}_chunk_{chunk_index}",
                document_id=document.id,
                text=chunk_text,
                metadata={
                    "chunk_index": str(chunk_index),
                    "token_count": str(len(chunk_tokens)),
                    "start_token": str(start_idx),
                    "end_token": str(end_idx),
                },
            )
            chunks.append(chunk)

            # Move to next chunk with overlap
            start_idx = end_idx - self._overlap
            chunk_index += 1

            # Prevent infinite loop if overlap >= chunk_size
            if start_idx >= len(tokens) or (end_idx == len(tokens) and start_idx >= end_idx):
                break

        return chunks

    def _reconstruct_text(self, tokens: list[str]) -> str:
        """
        Reconstruct text from tokens with appropriate spacing.

        Args:
            tokens: List of tokens

        Returns:
            Reconstructed text
        """
        if not tokens:
            return ""

        result = []
        for i, token in enumerate(tokens):
            if i == 0:
                result.append(token)
            elif token in ".,!?;:)]}":
                # Don't add space before punctuation
                result.append(token)
            elif i > 0 and tokens[i - 1] in "([{":
                # Don't add space after opening brackets
                result.append(token)
            else:
                result.append(" " + token)

        return "".join(result)

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

        tokens = self._tokenize(text)
        token_count = len(tokens)

        # Account for overlap in estimation
        effective_chunk_size = self._chunk_size - self._overlap
        if effective_chunk_size <= 0:
            effective_chunk_size = self._chunk_size

        # Estimate based on token count
        estimated = (token_count + effective_chunk_size - 1) // effective_chunk_size
        return max(1, estimated)
