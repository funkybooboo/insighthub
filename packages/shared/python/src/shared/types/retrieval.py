"""Retrieval result types for RAG pipelines."""

from dataclasses import dataclass

from shared.types.common import PayloadDict


@dataclass
class RetrievalResult:
    """
    Standardized retrieval result used across vector and graph retrieval.

    Fields:
        id: ID of the returned object (chunk id, node id, vector id, etc.)
        score: Normalized relevance score (higher = more relevant)
        source: String describing source modality ('vector', 'graph', 'doc', etc.)
        payload: Payload dictionary (text snippet, node properties, provenance, etc.)
    """

    id: str
    score: float
    source: str
    payload: PayloadDict
