"""Code-based document chunker implementation."""

import re

from src.infrastructure.rag.steps.general.chunking.document_chunker import Chunker
from src.infrastructure.types.document import Chunk, Document


class CodeDocumentChunker(Chunker):
    """
    Splits code into chunks based on structural boundaries.

    Attempts to split on function/class definitions and maintains code structure.
    Supports multiple programming languages through pattern matching.
    """

    # Patterns for different code structures
    FUNCTION_PATTERN = re.compile(
        r"^(?:def|function|func|fn|async\s+def|public\s+|private\s+|protected\s+)?(\w+)\s*\([^)]*\)\s*[:{]",
        re.MULTILINE,
    )

    CLASS_PATTERN = re.compile(r"^(?:class|interface|struct|enum|trait)\s+(\w+)", re.MULTILINE)

    # Python decorators
    DECORATOR_PATTERN = re.compile(r"^@\w+", re.MULTILINE)

    # Comment blocks (various languages)
    COMMENT_BLOCK_PATTERN = re.compile(
        r"((?:^[ \t]*#.*\n)+|/\*.*?\*/|(?:^[ \t]*//.*\n)+)", re.MULTILINE | re.DOTALL
    )

    def __init__(self, chunk_size: int, overlap: int) -> None:
        """
        Initialize code chunker.

        Args:
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        self._chunk_size = chunk_size
        self._overlap = overlap

    def _find_code_blocks(self, text: str) -> list[dict]:
        """
        Find code blocks (functions, classes, etc.) in text.

        Args:
            text: Code text to parse

        Returns:
            List of code blocks with type and position
        """
        blocks = []

        # Find classes
        for match in self.CLASS_PATTERN.finditer(text):
            blocks.append(
                {"type": "class", "name": match.group(1), "start": match.start(), "end": None}
            )

        # Find functions
        for match in self.FUNCTION_PATTERN.finditer(text):
            blocks.append(
                {"type": "function", "name": match.group(1), "start": match.start(), "end": None}
            )

        # Sort by start position
        blocks.sort(key=lambda x: x["start"])  # type: ignore[arg-type, return-value]

        # Estimate end positions based on next block or end of file
        for i in range(len(blocks)):
            if i + 1 < len(blocks):
                blocks[i]["end"] = blocks[i + 1]["start"]
            else:
                blocks[i]["end"] = len(text)

        return blocks

    def _extract_code_section(self, text: str, start: int, end: int) -> str:
        """
        Extract a section of code and include relevant context.

        Args:
            text: Full code text
            start: Start position
            end: End position

        Returns:
            Extracted code section
        """
        # Look backwards to include decorators and comments
        actual_start = start
        lines_before = text[:start].split("\n")

        # Include decorators
        for i in range(len(lines_before) - 1, -1, -1):
            line = lines_before[i].strip()
            if line.startswith("@") or line.startswith("#") or line.startswith("//"):
                actual_start = len("\n".join(lines_before[:i])) + 1
            else:
                break

        return text[actual_start:end].strip()

    def chunk(self, document: Document) -> list[Chunk]:
        """
        Split a code document into chunks based on structure.

        Args:
            document: The document to chunk

        Returns:
            List of text chunks with metadata
        """
        text = document.content
        if not text or not text.strip():
            return []

        blocks = self._find_code_blocks(text)

        # If no code blocks found, fall back to line-based chunking
        if not blocks:
            return self._chunk_by_lines(document)

        chunks: list[Chunk] = []
        chunk_index = 0
        current_chunk = ""
        current_metadata: dict = {}

        for block in blocks:
            block_content = self._extract_code_section(text, block["start"], block["end"])

            # If block fits in chunk_size, add it
            if len(block_content) <= self._chunk_size:
                # Check if adding this block exceeds chunk_size
                if len(current_chunk) + len(block_content) > self._chunk_size and current_chunk:
                    # Save current chunk
                    chunk = self._create_chunk(
                        document.id, chunk_index, current_chunk, current_metadata
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_chunk = ""

                # Add block to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + block_content
                else:
                    current_chunk = block_content

                current_metadata = {"code_type": block["type"], "code_name": block["name"]}
            else:
                # Block is too large, split by lines
                lines = block_content.split("\n")
                temp_chunk = ""

                for line in lines:
                    if len(temp_chunk) + len(line) > self._chunk_size and temp_chunk:
                        if current_chunk:
                            chunk = self._create_chunk(
                                document.id, chunk_index, current_chunk, current_metadata
                            )
                            chunks.append(chunk)
                            chunk_index += 1

                        current_chunk = temp_chunk
                        temp_chunk = line
                    else:
                        if temp_chunk:
                            temp_chunk += "\n" + line
                        else:
                            temp_chunk = line

                if temp_chunk:
                    current_chunk = temp_chunk

                current_metadata = {"code_type": block["type"], "code_name": block["name"]}

        # Add remaining content
        if current_chunk:
            chunk = self._create_chunk(document.id, chunk_index, current_chunk, current_metadata)
            chunks.append(chunk)

        return chunks

    def _chunk_by_lines(self, document: Document) -> list[Chunk]:
        """
        Fallback: chunk code by lines when no structure is detected.

        Args:
            document: The document to chunk

        Returns:
            List of chunks
        """
        lines = document.content.split("\n")
        chunks: list[Chunk] = []
        chunk_index = 0
        current_chunk = ""

        for line in lines:
            if len(current_chunk) + len(line) > self._chunk_size and current_chunk:
                chunk = self._create_chunk(
                    document.id,
                    chunk_index,
                    current_chunk,
                    {"code_type": "lines", "code_name": ""},
                )
                chunks.append(chunk)
                chunk_index += 1
                current_chunk = line
            else:
                if current_chunk:
                    current_chunk += "\n" + line
                else:
                    current_chunk = line

        if current_chunk:
            chunk = self._create_chunk(
                document.id, chunk_index, current_chunk, {"code_type": "lines", "code_name": ""}
            )
            chunks.append(chunk)

        return chunks

    def _create_chunk(self, doc_id: str, chunk_index: int, text: str, metadata: dict) -> Chunk:
        """Create a chunk with metadata."""
        # Count lines in chunk
        line_count = len(text.split("\n"))

        return Chunk(
            id=f"{doc_id}_chunk_{chunk_index}",
            document_id=doc_id,
            text=text,
            metadata={
                "chunk_index": str(chunk_index),
                "char_count": str(len(text)),
                "line_count": str(line_count),
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
