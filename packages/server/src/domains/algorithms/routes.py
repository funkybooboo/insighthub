"""Algorithm options API routes."""

from flask import Blueprint, jsonify

from src.infrastructure.auth import require_auth

algorithms_bp = Blueprint("algorithms", __name__, url_prefix="/api")


# Algorithm registries - easily extensible
VECTOR_ALGORITHMS = {
    "embedding_algorithms": [
        {"value": "nomic-embed-text", "label": "Nomic Embed Text"},
        {"value": "all-MiniLM-L6-v2", "label": "MiniLM L6 v2"},
    ],
    "chunking_algorithms": [
        {"value": "sentence", "label": "Sentence-based"},
        {"value": "character", "label": "Character-based"},
    ],
    "rerank_algorithms": [
        {"value": "cross-encoder/ms-marco-MiniLM-L-6-v2", "label": "Cross-Encoder MiniLM"},
    ],
}

GRAPH_ALGORITHMS = {
    "entity_extraction_algorithms": [
        {"value": "ollama", "label": "Ollama LLM"},
        {"value": "spacy", "label": "SpaCy NER"},
    ],
    "relationship_extraction_algorithms": [
        {"value": "ollama", "label": "Ollama LLM"},
        {"value": "rule-based", "label": "Rule-based"},
    ],
    "clustering_algorithms": [
        {"value": "leiden", "label": "Leiden Algorithm"},
        {"value": "louvain", "label": "Louvain Algorithm"},
    ],
}


@algorithms_bp.route("/algorithms/vector", methods=["GET"])
@require_auth
def get_vector_algorithms():
    """
    Get available algorithms for Vector RAG.

    Returns:
        200: {
            "embedding_algorithms": [...],
            "chunking_algorithms": [...],
            "rerank_algorithms": [...]
        }
    """
    return jsonify(VECTOR_ALGORITHMS)


@algorithms_bp.route("/algorithms/graph", methods=["GET"])
@require_auth
def get_graph_algorithms():
    """
    Get available algorithms for Graph RAG.

    Returns:
        200: {
            "entity_extraction_algorithms": [...],
            "relationship_extraction_algorithms": [...],
            "clustering_algorithms": [...]
        }
    """
    return jsonify(GRAPH_ALGORITHMS)