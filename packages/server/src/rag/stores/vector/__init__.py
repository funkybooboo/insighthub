"""
Vector store implementations
"""

from src.rag.stores.vector.base import VectorStore
from src.rag.stores.vector.qdrant import QdrantVectorStore

# Optional import for Pinecone
try:
    from src.rag.stores.vector.pinecone import PineconeVectorStore

    _has_pinecone = True
except ImportError:
    _has_pinecone = False

__all__ = [
    "VectorStore",
    "QdrantVectorStore",
]

# Add PineconeVectorStore to exports if available
if _has_pinecone:
    __all__.append("PineconeVectorStore")
