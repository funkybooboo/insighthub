import datetime as _dt

from shared.types import RagConfig


def test_rag_config_defaults_fields_exist() -> None:
    cfg = RagConfig()
    # basic type expectations for essential fields
    assert isinstance(cfg.workspace_id, str)
    assert isinstance(cfg.rag_type, str)
    assert isinstance(cfg.chunking_strategy, str)
    assert isinstance(cfg.embedding_model, str)
    assert (cfg.embedding_dim is None) or isinstance(cfg.embedding_dim, int)
    assert isinstance(cfg.chunk_size, int)
    assert isinstance(cfg.chunk_overlap, int)
    assert isinstance(cfg.top_k, int)
    assert isinstance(cfg.rerank_enabled, bool)
    assert (cfg.rerank_model is None) or isinstance(cfg.rerank_model, str)
    assert (cfg.created_at is None) or isinstance(cfg.created_at, _dt.datetime)
    assert (cfg.updated_at is None) or isinstance(cfg.updated_at, _dt.datetime)


def test_rag_config_mutable_fields() -> None:
    cfg = RagConfig()
    cfg.rag_type = "graph"
    cfg.chunk_size = 256
    cfg.chunk_overlap = 10
    cfg.top_k = 5
    assert cfg.rag_type == "graph"
    assert cfg.chunk_size == 256
    assert cfg.chunk_overlap == 10
    assert cfg.top_k == 5
