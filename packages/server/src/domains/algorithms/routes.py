"""Algorithms routes for listing available RAG algorithms."""

from flask import Blueprint, jsonify

from src.infrastructure.logger import create_logger
from src.infrastructure.rag.steps.general.chunking.factory import get_available_chunkers
from src.infrastructure.rag.steps.general.parsing.factory import ParserFactory
from src.infrastructure.rag.steps.vector_rag.embedding.factory import get_available_embedders
from src.infrastructure.rag.steps.vector_rag.reranking.factory import get_available_rerankers
from src.infrastructure.rag.steps.vector_rag.vector_stores.factory import (
    get_available_vector_stores,
)

logger = create_logger(__name__)

algorithms_bp = Blueprint("algorithms", __name__, url_prefix="/api/algorithms")


@algorithms_bp.route("/vector", methods=["GET"])
def get_vector_algorithms() -> tuple[dict, int]:
    """
    Get available algorithms for Vector RAG.

    Returns list of available implementations from factories.
    """
    return (
        jsonify(
            {
                "embedding_algorithms": get_available_embedders(),
                "chunking_algorithms": get_available_chunkers(),
                "rerank_algorithms": get_available_rerankers(),
                "vector_stores": get_available_vector_stores(),
                "parsing_algorithms": ParserFactory.get_available_parsers(),
            }
        ),
        200,
    )


@algorithms_bp.route("/graph", methods=["GET"])
def get_graph_algorithms() -> tuple[dict, int]:
    """
    Get available algorithms for Graph RAG.

    TODO: Implement entity extraction, relationship extraction, and clustering
    interfaces, then discover implementations automatically.

    For now, returns placeholder values.
    """
    # TODO: Discover from EntityExtractor, RelationshipExtractor, ClusteringAlgorithm interfaces
    return (
        jsonify(
            {
                "entity_extraction_algorithms": [
                    {
                        "value": "spacy",
                        "label": "SpaCy NER",
                        "description": "Named entity recognition using SpaCy",
                    },
                    {
                        "value": "llm",
                        "label": "LLM-based",
                        "description": "Entity extraction using LLM",
                    },
                ],
                "relationship_extraction_algorithms": [
                    {
                        "value": "dependency-parsing",
                        "label": "Dependency Parsing",
                        "description": "Extract relationships via dependency parsing",
                    },
                    {
                        "value": "llm",
                        "label": "LLM-based",
                        "description": "Relationship extraction using LLM",
                    },
                ],
                "clustering_algorithms": [
                    {
                        "value": "leiden",
                        "label": "Leiden",
                        "description": "Leiden community detection algorithm",
                    },
                    {
                        "value": "louvain",
                        "label": "Louvain",
                        "description": "Louvain community detection algorithm",
                    },
                ],
            }
        ),
        200,
    )
