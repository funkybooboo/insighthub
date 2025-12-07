"""Markdown-based document chunker implementation."""

import re

from src.infrastructure.rag.steps.general.chunking.document_chunker import Chunker
from src.infrastructure.types.document import Chunk, Document


class MarkdownDocumentChunker(Chunker):
    """
    Splits Markdown text into chunks based on structural boundaries.

    Attempts to split on headings (# headers) and maintains document structure.
    Falls back to paragraph-based splitting if no headers are found.
    """

    # Markdown heading pattern
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    # Paragraph split pattern (double newlines)
    PARAGRAPH_PATTERN = re.compile(r"\n\n+")

    def __init__(self, chunk_size: int, overlap: int) -> None:
        """
        Initialize markdown chunker.

        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self._chunk_size = chunk_size
        self._overlap = overlap

    def _split_by_headings(self, text: str) -> list[dict]:
        """
        Split text by markdown headings.

        Args:
            text: Markdown text to split

        Returns:
            List of sections with heading level and content
        """
        sections = []
        matches = list(self.HEADING_PATTERN.finditer(text))

        if not matches:
            # No headings found, return entire text as one section
            return [{"level": 0, "title": "", "content": text, "start": 0}]

        # Add content before first heading if any
        if matches[0].start() > 0:
            sections.append(
                {
                    "level": 0,
                    "title": "",
                    "content": text[: matches[0].start()].strip(),
                    "start": 0,
                }
            )

        # Process each heading
        for i, match in enumerate(matches):
            level = len(match.group(1))
            title = match.group(2).strip()
            start = match.start()

            # Find content until next heading
            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(text)

            content = text[start:end].strip()

            sections.append({"level": level, "title": title, "content": content, "start": start})

        return sections

    def chunk(self, document: Document) -> list[Chunk]:
        """
        Split a Markdown document into chunks based on structure.

        Args:
            document: The document to chunk

        Returns:
            List of text chunks with metadata
        """
        text = document.content
        if not text or not text.strip():
            return []

        sections = self._split_by_headings(text)
        chunks: list[Chunk] = []
        chunk_index = 0
        current_chunk = ""
        current_metadata: dict = {}

        for section in sections:
            section_content = section["content"]

            # If section fits in chunk_size, add it directly
            if len(section_content) <= self._chunk_size:
                # Check if adding this section exceeds chunk_size
                if len(current_chunk) + len(section_content) > self._chunk_size and current_chunk:
                    # Save current chunk
                    chunk = self._create_chunk(
                        document.id, chunk_index, current_chunk, current_metadata
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_chunk = ""

                # Add section to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + section_content
                else:
                    current_chunk = section_content

                current_metadata = {
                    "heading_level": str(section["level"]),
                    "heading_title": section["title"],
                }
            else:
                # Section is too large, split it by paragraphs
                paragraphs = self.PARAGRAPH_PATTERN.split(section_content)
                for para in paragraphs:
                    if not para.strip():
                        continue

                    if len(current_chunk) + len(para) > self._chunk_size and current_chunk:
                        chunk = self._create_chunk(
                            document.id, chunk_index, current_chunk, current_metadata
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                        current_chunk = para
                    else:
                        if current_chunk:
                            current_chunk += "\n\n" + para
                        else:
                            current_chunk = para

                    current_metadata = {
                        "heading_level": str(section["level"]),
                        "heading_title": section["title"],
                    }

        # Add remaining content
        if current_chunk:
            chunk = self._create_chunk(document.id, chunk_index, current_chunk, current_metadata)
            chunks.append(chunk)

        return chunks

    def _create_chunk(self, doc_id: str, chunk_index: int, text: str, metadata: dict) -> Chunk:
        """Create a chunk with metadata."""
        return Chunk(
            id=f"{doc_id}_chunk_{chunk_index}",
            document_id=doc_id,
            text=text,
            metadata={
                "chunk_index": str(chunk_index),
                "char_count": str(len(text)),
                **metadata,
            },
        )

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

        # Rough estimation based on chunk_size
        effective_chunk_size = self._chunk_size - self._overlap
        if effective_chunk_size <= 0:
            effective_chunk_size = self._chunk_size

        estimated = (text_length + effective_chunk_size - 1) // effective_chunk_size
        return max(1, estimated)
