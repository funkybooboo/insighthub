"""HTML-based document chunker implementation."""

import re

from src.infrastructure.rag.steps.general.chunking.document_chunker import Chunker
from src.infrastructure.types.document import Chunk, Document


class HtmlDocumentChunker(Chunker):
    """
    Splits HTML text into chunks based on structural elements.

    Attempts to split on block-level HTML elements (div, p, section, article, etc.)
    and maintains document structure. Strips HTML tags while preserving text content.
    """

    # Block-level HTML elements to split on
    BLOCK_ELEMENTS = re.compile(
        r"<(div|p|section|article|header|footer|main|aside|nav|h[1-6])[^>]*>(.*?)</\1>",
        re.DOTALL | re.IGNORECASE,
    )

    # Pattern to remove HTML tags
    HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

    def __init__(self, chunk_size: int, overlap: int) -> None:
        """
        Initialize HTML chunker.

        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self._chunk_size = chunk_size
        self._overlap = overlap

    def _strip_html_tags(self, html: str) -> str:
        """
        Remove HTML tags from text while preserving content.

        Args:
            html: HTML text

        Returns:
            Plain text with HTML tags removed
        """
        # Remove HTML tags
        text = self.HTML_TAG_PATTERN.sub("", html)
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_elements(self, text: str) -> list[dict]:
        """
        Extract block-level HTML elements.

        Args:
            text: HTML text to parse

        Returns:
            List of elements with tag name and content
        """
        elements = []
        matches = list(self.BLOCK_ELEMENTS.finditer(text))

        if not matches:
            # No block elements found, treat entire text as one element
            clean_text = self._strip_html_tags(text)
            if clean_text:
                return [{"tag": "div", "content": clean_text, "start": 0}]
            return []

        # Track processed positions to handle nested elements
        processed_ranges: list[tuple[int, int]] = []

        for match in matches:
            start, end = match.span()

            # Skip if this range overlaps with already processed range (nested element)
            is_nested = False
            for proc_start, proc_end in processed_ranges:
                if start >= proc_start and end <= proc_end:
                    is_nested = True
                    break

            if not is_nested:
                tag = match.group(1).lower()
                content = self._strip_html_tags(match.group(2))

                if content:
                    elements.append({"tag": tag, "content": content, "start": start})
                    processed_ranges.append((start, end))

        # If no elements were extracted, fall back to stripping all tags
        if not elements:
            clean_text = self._strip_html_tags(text)
            if clean_text:
                elements = [{"tag": "div", "content": clean_text, "start": 0}]

        return elements

    def chunk(self, document: Document) -> list[Chunk]:
        """
        Split an HTML document into chunks based on structure.

        Args:
            document: The document to chunk

        Returns:
            List of text chunks with metadata
        """
        text = document.content
        if not text or not text.strip():
            return []

        elements = self._extract_elements(text)
        if not elements:
            return []

        chunks: list[Chunk] = []
        chunk_index = 0
        current_chunk = ""
        current_tag = ""

        for element in elements:
            element_content = element["content"]
            element_tag = element["tag"]

            # If element content fits in chunk_size
            if len(element_content) <= self._chunk_size:
                # Check if adding this element exceeds chunk_size
                if len(current_chunk) + len(element_content) > self._chunk_size and current_chunk:
                    # Save current chunk
                    chunk = self._create_chunk(
                        document.id, chunk_index, current_chunk, {"html_tag": current_tag}
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_chunk = ""

                # Add element to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + element_content
                else:
                    current_chunk = element_content
                    current_tag = element_tag
            else:
                # Element is too large, split by sentences or paragraphs
                sentences = re.split(r"(?<=[.!?])\s+", element_content)
                for sentence in sentences:
                    if not sentence.strip():
                        continue

                    if len(current_chunk) + len(sentence) > self._chunk_size and current_chunk:
                        chunk = self._create_chunk(
                            document.id, chunk_index, current_chunk, {"html_tag": current_tag}
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                        current_chunk = sentence
                        current_tag = element_tag
                    else:
                        if current_chunk:
                            current_chunk += " " + sentence
                        else:
                            current_chunk = sentence
                            current_tag = element_tag

        # Add remaining content
        if current_chunk:
            chunk = self._create_chunk(
                document.id, chunk_index, current_chunk, {"html_tag": current_tag}
            )
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

        # Strip HTML to get actual text length
        clean_text = self._strip_html_tags(text)
        text_length = len(clean_text)

        # Rough estimation based on chunk_size
        effective_chunk_size = self._chunk_size - self._overlap
        if effective_chunk_size <= 0:
            effective_chunk_size = self._chunk_size

        estimated = (text_length + effective_chunk_size - 1) // effective_chunk_size
        return max(1, estimated)
