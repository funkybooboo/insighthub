from shared.types import RagConfig


def test_rag_config_identity_and_equality():
    a = RagConfig()
    b = RagConfig()
    assert a == b
    assert a is not b
