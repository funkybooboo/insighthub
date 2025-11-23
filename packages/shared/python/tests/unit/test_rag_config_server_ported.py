from shared.types import RagConfig


def test_rag_type_default_ported() -> None:
    cfg = RagConfig()
    assert cfg.rag_type == "vector"


def test_chunking_strategy_default_ported() -> None:
    cfg = RagConfig()
    assert cfg.chunking_strategy == "sentence"


def test_chunk_size_is_positive_ported() -> None:
    cfg = RagConfig()
    assert isinstance(cfg.chunk_size, int)
    assert cfg.chunk_size > 0


def test_chunk_overlap_is_valid_ported() -> None:
    cfg = RagConfig()
    assert isinstance(cfg.chunk_overlap, int)
    assert cfg.chunk_overlap >= 0
    assert cfg.chunk_overlap < cfg.chunk_size


def test_rag_top_k_is_positive_ported() -> None:
    cfg = RagConfig()
    assert isinstance(cfg.top_k, int)
    assert cfg.top_k > 0
