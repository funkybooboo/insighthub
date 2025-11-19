"""Common type definitions used across the RAG system."""

from typing import Union

# Primitive types allowed in metadata
PrimitiveValue = Union[str, int, float, bool, None]

# Metadata values can be primitives or lists of primitives
MetadataValue = Union[PrimitiveValue, list[PrimitiveValue]]
