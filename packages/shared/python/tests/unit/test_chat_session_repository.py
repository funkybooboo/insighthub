"""Interface tests for ChatSessionRepository definition."""

import inspect

from shared.repositories.chat import ChatSessionRepository


def test_chat_session_repository_is_abstract_class() -> None:
    assert inspect.isclass(ChatSessionRepository)
    assert inspect.isabstract(ChatSessionRepository)


def test_chat_session_repository_abstract_methods_are_defined() -> None:
    abstract_methods = [
        "create",
        "get_by_id",
        "get_by_user",
        "update",
        "delete",
    ]
    for name in abstract_methods:
        assert hasattr(ChatSessionRepository, name), f"Missing method {name} on ChatSessionRepository"
        method = getattr(ChatSessionRepository, name)
        assert getattr(method, "__isabstractmethod__", False) is True
