from returns.result import Success

from src.domains.rag_options.orchestrator import RagOptionsOrchestrator
from src.domains.rag_options.service import RagOptionsService


def test_get_all_options_returns_success_with_all_options():
    # Arrange
    service = RagOptionsService()
    orchestrator = RagOptionsOrchestrator(service=service)

    # Act
    result = orchestrator.get_all_options()

    # Assert
    assert isinstance(result, Success)
    response = result.unwrap()

    assert response.rag_types is not None
    assert response.chunking_algorithms is not None
    assert response.embedding_algorithms is not None
    assert response.rerank_algorithms is not None
    assert response.entity_extraction_algorithms is not None
    assert response.relationship_extraction_algorithms is not None
    assert response.clustering_algorithms is not None

    # Optionally, check that there's at least one option for each category
    assert len(response.rag_types) > 0
    assert len(response.chunking_algorithms) > 0
    assert len(response.embedding_algorithms) > 0
    assert len(response.rerank_algorithms) > 0
    assert len(response.entity_extraction_algorithms) > 0
    assert len(response.relationship_extraction_algorithms) > 0
    assert len(response.clustering_algorithms) > 0
