"""Code-based document chunker implementation."""

import re
from typing import TypedDict

from src.infrastructure.rag.steps.general.chunking.document_chunker import Chunker
from src.infrastructure.types.document import Chunk, Document


class CodeBlock(TypedDict):
    """Represents a code block (function, class, etc.)."""

    type: str
    name: str
    start: int
    end: int | None
    indent: int


class CodeDocumentChunker(Chunker):
    """
    Splits code into chunks based on structural boundaries.

    Attempts to split on function/class definitions and maintains code structure.
    Supports multiple programming languages through pattern matching.
    """

    # Patterns for different code structures
    FUNCTION_PATTERN = re.compile(
        r"^\s*(?:def|function|func|fn|async\s+def|public|private|protected)\s+(\w+)\s*\([^)]*\)\s*[:{]",
        re.MULTILINE,
    )

    CLASS_PATTERN = re.compile(r"^\s*(?:class|interface|struct|enum|trait)\s+(\w+)", re.MULTILINE)

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

    def _find_code_blocks(self, text: str) -> list[CodeBlock]:
        """
        Find code blocks (functions, classes, etc.) in text.

        Args:
            text: Code text to parse

        Returns:
            List of all code blocks with type and position
        """
        blocks: list[CodeBlock] = []

        # Find classes
        for match in self.CLASS_PATTERN.finditer(text):
            # Extract indentation (count spaces/tabs, not including newlines)
            matched_text = match.group(0)
            # Remove leading newlines first, then count spaces
            indent_text = matched_text.lstrip("\n")
            indent = len(indent_text) - len(indent_text.lstrip(" \t"))
            blocks.append(
                {
                    "type": "class",
                    "name": match.group(1),
                    "start": match.start(),
                    "end": None,
                    "indent": indent,
                }
            )

        # Find functions
        for match in self.FUNCTION_PATTERN.finditer(text):
            # Extract indentation (count spaces/tabs, not including newlines)
            matched_text = match.group(0)
            # Remove leading newlines first, then count spaces
            indent_text = matched_text.lstrip("\n")
            indent = len(indent_text) - len(indent_text.lstrip(" \t"))
            blocks.append(
                {
                    "type": "function",
                    "name": match.group(1),
                    "start": match.start(),
                    "end": None,
                    "indent": indent,
                }
            )

        # Sort by start position
        blocks.sort(key=lambda x: x["start"])

        # Determine end positions based on indentation
        # Blocks extend until the next block at the same or lower indentation
        for i in range(len(blocks)):
            current_indent = blocks[i]["indent"]
            end_pos = len(text)
            for j in range(i + 1, len(blocks)):
                if blocks[j]["indent"] <= current_indent:
                    end_pos = blocks[j]["start"]
                    break
            blocks[i]["end"] = end_pos

        return blocks

    def _get_top_level_blocks(self, blocks: list[CodeBlock]) -> list[CodeBlock]:
        """
        Filter blocks to keep only top-level ones (not nested inside other blocks).

        Args:
            blocks: List of all code blocks

        Returns:
            List of top-level blocks only
        """
        filtered_blocks: list[CodeBlock] = []
        for block in blocks:
            # Check if this block is nested inside another block
            is_nested = False
            for other in blocks:
                if other is block:
                    continue
                # At this point, end should never be None as it's set in _find_code_blocks
                assert other["end"] is not None
                assert block["end"] is not None
                if (
                    other["start"] < block["start"] < other["end"]
                    and other["indent"] < block["indent"]
                ):
                    is_nested = True
                    break
            if not is_nested:
                filtered_blocks.append(block)

        return filtered_blocks

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

        all_blocks = self._find_code_blocks(text)

        # Filter to get only top-level blocks for chunking
        blocks = self._get_top_level_blocks(all_blocks)

        # If no code blocks found, fall back to line-based chunking
        if not blocks:
            return self._chunk_by_lines(document)

        chunks: list[Chunk] = []
        chunk_index = 0
        current_chunk = ""
        current_metadata: dict = {}

        for block in blocks:
            # At this point, end should never be None as it's set in _find_code_blocks
            assert block["end"] is not None
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
                # First, save any pending current_chunk
                if current_chunk:
                    chunk = self._create_chunk(
                        document.id, chunk_index, current_chunk, current_metadata
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_chunk = ""

                # Now split the large block into chunks
                lines = block_content.split("\n")
                temp_chunk = ""

                for line in lines:
                    if len(temp_chunk) + len(line) + 1 > self._chunk_size and temp_chunk:
                        # temp_chunk is full, save it as a chunk
                        chunk = self._create_chunk(
                            document.id,
                            chunk_index,
                            temp_chunk,
                            {"code_type": block["type"], "code_name": block["name"]},
                        )
                        chunks.append(chunk)
                        chunk_index += 1
                        temp_chunk = line
                    else:
                        if temp_chunk:
                            temp_chunk += "\n" + line
                        else:
                            temp_chunk = line

                # Save the remaining temp_chunk content
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
