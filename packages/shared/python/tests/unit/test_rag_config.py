import pytest

from shared.types import RagConfig


def test_rag_config_defaults():
    cfg = RagConfig()
    assert cfg.rag_type == "vector"
    assert cfg.chunking_strategy == "sentence"
    assert cfg.embedding_model == "nomic-embed-text"
    assert cfg.chunk_size == 1000
    assert cfg.chunk_overlap == 200
    assert cfg.top_k == 8
    assert cfg.chunk_size > 0


def test_rag_config_mutation_safe():
    cfg = RagConfig()
    # mutate a few fields to ensure mutability
    cfg.rag_type = "graph"
    cfg.chunk_size = 512
    assert cfg.rag_type == "graph"
    assert cfg.chunk_size == 512


def test_rag_config_fields_exist():
    cfg = RagConfig()
    for field in [
        "workspace_id",
        "rag_type",
        "chunking_strategy",
        "embedding_model",
        "embedding_dim",
        "top_k",
        "retriever_type",
        "chunk_size",
        "chunk_overlap",
        "rerank_enabled",
        "rerank_model",
        "created_at",
        "updated_at",
    ]:
        assert hasattr(cfg, field)
