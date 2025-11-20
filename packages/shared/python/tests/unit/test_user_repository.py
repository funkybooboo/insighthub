""Interface tests for UserRepository definition."""

import inspect

from shared.repositories.user import UserRepository


def test_user_repository_is_abstract_class() -> None:
    assert inspect.isclass(UserRepository)
    assert inspect.isabstract(UserRepository)


def test_user_repository_abstract_methods_are_defined() -> None:
    abstract_methods = [
        "create",
        "get_by_id",
        "get_by_username",
        "get_by_email",
        "get_all",
        "update",
        "delete",
    ]
    for name in abstract_methods:
        assert hasattr(UserRepository, name), f"Missing method {name} on UserRepository"
        method = getattr(UserRepository, name)
        assert getattr(method, "__isabstractmethod__", False) is True
