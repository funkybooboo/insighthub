import pytest

from src.infrastructure.rag.options import (
    get_chunking_options,
    get_default_chunking_algorithm,
    get_default_clustering_algorithm,
    get_default_embedding_algorithm,
    get_default_entity_extraction_algorithm,
    get_default_rag_type,
    get_default_relationship_extraction_algorithm,
    get_default_reranking_algorithm,
    get_embedding_options,
    get_graph_clustering_options,
    get_graph_entity_extraction_options,
    get_graph_relationship_extraction_options,
    get_rag_type_options,
    get_reranking_options,
    get_valid_rag_types,
    is_valid_chunking_algorithm,
    is_valid_rag_type,
)


def test_get_rag_type_options_returns_expected_types():
    options = get_rag_type_options()

    assert isinstance(options, list)
    assert len(options) == 3

    vector_rag = next((opt for opt in options if opt["value"] == "vector"), None)
    graph_rag = next((opt for opt in options if opt["value"] == "graph"), None)
    hybrid_rag = next((opt for opt in options if opt["value"] == "hybrid"), None)

    assert vector_rag is not None
    assert graph_rag is not None
    assert hybrid_rag is not None

    assert vector_rag["label"] == "Vector RAG"
    assert vector_rag["description"] == "Traditional vector similarity search with embeddings"

    assert graph_rag["label"] == "Graph RAG"
    assert graph_rag["description"] == "Knowledge graph-based retrieval with entity relationships"

    assert hybrid_rag["label"] == "Hybrid RAG"
    assert hybrid_rag["description"] == "Combines vector and graph retrieval for enhanced results"


def test_get_chunking_options_returns_expected_types():
    options = get_chunking_options()

    assert isinstance(options, list)
    assert len(options) > 0  # Expect at least one chunking option

    for opt in options:
        assert "value" in opt
        assert "label" in opt
        assert "description" in opt
        assert isinstance(opt["value"], str)
        assert isinstance(opt["label"], str)
        assert isinstance(opt["description"], str)


def test_get_embedding_options_returns_expected_types():
    options = get_embedding_options()

    assert isinstance(options, list)
    assert len(options) > 0  # Expect at least one embedding option

    for opt in options:
        assert "value" in opt
        assert "label" in opt
        assert "description" in opt
        assert isinstance(opt["value"], str)
        assert isinstance(opt["label"], str)
        assert isinstance(opt["description"], str)


def test_get_reranking_options_returns_expected_types():
    options = get_reranking_options()

    assert isinstance(options, list)
    assert len(options) > 0  # Expect at least one reranking option

    for opt in options:
        assert "value" in opt
        assert "label" in opt
        assert "description" in opt
        assert isinstance(opt["value"], str)
        assert isinstance(opt["label"], str)
        assert isinstance(opt["description"], str)


def test_get_graph_entity_extraction_options_returns_expected_types():
    options = get_graph_entity_extraction_options()

    assert isinstance(options, list)
    assert len(options) > 0  # Expect at least one entity extraction option

    for opt in options:
        assert "value" in opt
        assert "label" in opt
        assert "description" in opt
        assert isinstance(opt["value"], str)
        assert isinstance(opt["label"], str)
        assert isinstance(opt["description"], str)


def test_get_graph_relationship_extraction_options_returns_expected_types():
    options = get_graph_relationship_extraction_options()

    assert isinstance(options, list)
    assert len(options) > 0  # Expect at least one relationship extraction option

    for opt in options:
        assert "value" in opt
        assert "label" in opt
        assert "description" in opt
        assert isinstance(opt["value"], str)
        assert isinstance(opt["label"], str)
        assert isinstance(opt["description"], str)


def test_get_graph_clustering_options_returns_expected_types():
    options = get_graph_clustering_options()

    assert isinstance(options, list)
    assert len(options) > 0  # Expect at least one clustering option

    for opt in options:
        assert "value" in opt
        assert "label" in opt
        assert "description" in opt
        assert isinstance(opt["value"], str)
        assert isinstance(opt["label"], str)
        assert isinstance(opt["description"], str)


def test_get_default_rag_type_returns_expected_default():
    default_rag_type = get_default_rag_type()
    assert isinstance(default_rag_type, str)
    assert default_rag_type == "vector"


def test_get_default_chunking_algorithm_returns_expected_default():
    default_chunking_algorithm = get_default_chunking_algorithm()
    assert isinstance(default_chunking_algorithm, str)
    assert default_chunking_algorithm == "sentence"


def test_get_default_embedding_algorithm_returns_expected_default():
    default_embedding_algorithm = get_default_embedding_algorithm()
    assert isinstance(default_embedding_algorithm, str)
    assert default_embedding_algorithm == "nomic-embed-text"


def test_get_default_reranking_algorithm_returns_expected_default():
    default_reranking_algorithm = get_default_reranking_algorithm()
    assert isinstance(default_reranking_algorithm, str)
    assert default_reranking_algorithm == "none"


def test_get_default_entity_extraction_algorithm_returns_expected_default():
    default_entity_extraction_algorithm = get_default_entity_extraction_algorithm()
    assert isinstance(default_entity_extraction_algorithm, str)
    assert default_entity_extraction_algorithm == "spacy"


def test_get_default_relationship_extraction_algorithm_returns_expected_default():
    default_relationship_extraction_algorithm = get_default_relationship_extraction_algorithm()
    assert isinstance(default_relationship_extraction_algorithm, str)
    assert default_relationship_extraction_algorithm == "dependency-parsing"


def test_get_default_clustering_algorithm_returns_expected_default():
    default_clustering_algorithm = get_default_clustering_algorithm()
    assert isinstance(default_clustering_algorithm, str)
    assert default_clustering_algorithm == "leiden"


@pytest.mark.parametrize(
    "rag_type, expected_result",
    [
        ("vector", True),
        ("graph", True),
        ("hybrid", True),
        ("invalid", False),
        ("", False),
        (None, False),
    ],
)
def test_is_valid_rag_type_returns_correct_boolean(rag_type, expected_result):
    assert is_valid_rag_type(rag_type) == expected_result


def test_get_valid_rag_types_returns_expected_list():
    valid_types = get_valid_rag_types()
    assert isinstance(valid_types, list)
    assert "vector" in valid_types
    assert "graph" in valid_types
    assert "hybrid" in valid_types
    assert len(valid_types) == 3


@pytest.mark.parametrize(
    "chunking_algorithm, expected_result",
    [
        ("sentence", True),
        ("token", True),
        ("markdown", True),
        ("html", True),
        ("code", True),
        ("invalid", False),
        ("", False),
        (None, False),
    ],
)
def test_is_valid_chunking_algorithm_returns_correct_boolean(chunking_algorithm, expected_result):
    assert is_valid_chunking_algorithm(chunking_algorithm) == expected_result


# @pytest.mark.parametrize(
#     "embedding_algorithm, expected_result",
#     [
#         ("openai", True),
#         ("ollama", True),
#         ("huggingface", True),
#         ("nomic-embed-text", True),
#         ("invalid", False),
#         ("", False),
#         (None, False),
#     ],
# )
# def test_is_valid_embedding_algorithm_returns_correct_boolean(embedding_algorithm, expected_result):
#     assert is_valid_embedding_algorithm(embedding_algorithm) == expected_result
