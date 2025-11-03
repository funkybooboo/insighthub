"""
Storage backends for RAG systems

Organized by storage type:
- vector: Vector database backends (Qdrant, Pinecone)
- graph: Graph database backends (future)
"""

from src.rag.stores.vector import QdrantVectorStore, VectorStore

# Optional Pinecone import
try:
    from src.rag.stores.vector import PineconeVectorStore

    _has_pinecone = True
except ImportError:
    _has_pinecone = False

__all__ = [
    "VectorStore",
    "QdrantVectorStore",
]

if _has_pinecone:
    __all__.append("PineconeVectorStore")
