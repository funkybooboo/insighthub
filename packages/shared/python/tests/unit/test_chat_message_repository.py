"""Interface tests for ChatMessageRepository definition."""

import inspect

from shared.repositories.chat import ChatMessageRepository


def test_chat_message_repository_is_abstract_class() -> None:
    assert inspect.isclass(ChatMessageRepository)
    assert inspect.isabstract(ChatMessageRepository)


def test_chat_message_repository_abstract_methods_are_defined() -> None:
    abstract_methods = ["create", "get_by_id", "get_by_session", "delete"]
    for name in abstract_methods:
        assert hasattr(ChatMessageRepository, name), f"Missing method {name} on ChatMessageRepository"
        method = getattr(ChatMessageRepository, name)
        assert getattr(method, "__isabstractmethod__", False) is True
