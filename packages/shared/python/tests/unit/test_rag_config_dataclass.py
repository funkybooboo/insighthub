from datetime import datetime

from shared.types import RagConfig


def test_rag_config_defaults_and_mutable() -> None:
    cfg1 = RagConfig()
    cfg2 = RagConfig()
    # default config instances should be equal (same default values)
    assert cfg1 == cfg2


def test_rag_config_custom_values() -> None:
    cfg = RagConfig(
        workspace_id="w1",
        rag_type="graph",
        chunking_strategy="character",
        embedding_model="custom-model",
        embedding_dim=128,
        retriever_type="vector",
        chunk_size=512,
        chunk_overlap=128,
        top_k=12,
        rerank_enabled=True,
        rerank_model="rr",
        created_at=None,
        updated_at=None,
    )
    assert cfg.workspace_id == "w1"
    assert cfg.rag_type == "graph"
    assert cfg.chunking_strategy == "character"
    assert cfg.embedding_model == "custom-model"
    assert cfg.embedding_dim == 128
    assert cfg.chunk_size == 512
    assert cfg.chunk_overlap == 128
    assert cfg.top_k == 12
    assert cfg.rerank_enabled is True
    assert cfg.rerank_model == "rr"
    assert cfg.created_at is None
    assert cfg.updated_at is None


def test_rag_config_datetime_fields() -> None:
    now = datetime.utcnow()
    cfg = RagConfig(created_at=now, updated_at=now)
    assert cfg.created_at == now
    assert cfg.updated_at == now
