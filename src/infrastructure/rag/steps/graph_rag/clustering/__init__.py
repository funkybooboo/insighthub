"""Community detection (clustering) implementations for Graph RAG.

This package provides interfaces and implementations for detecting communities
in knowledge graphs as part of the Graph RAG pipeline.
"""

from src.infrastructure.rag.steps.graph_rag.clustering.base import CommunityDetector
from src.infrastructure.rag.steps.graph_rag.clustering.factory import CommunityDetectorFactory

__all__ = [
    "CommunityDetector",
    "CommunityDetectorFactory",
]
