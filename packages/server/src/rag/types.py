"""
Common type definitions for RAG system
"""

from collections.abc import Callable
from typing import TypeAlias

# Metadata dictionary type - more permissive
MetadataValue: TypeAlias = str | int | float | bool | list[str] | None
Metadata: TypeAlias = dict[str, MetadataValue]

# Document type - union of text and metadata
Document: TypeAlias = dict[str, str | Metadata]

# Vector type
Vector: TypeAlias = list[float]

# Search result type
SearchResult: TypeAlias = dict[str, str | float | Metadata]

# Stats dictionary type - can include None values
Stats: TypeAlias = dict[str, int | float | str | None]

# LLM Generator callable type
LLMGenerator: TypeAlias = Callable[[str, str], str]

# JSON-like value type (recursive)
JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]

# Chunk type - returned by chunker
Chunk: TypeAlias = dict[str, str | Metadata]
