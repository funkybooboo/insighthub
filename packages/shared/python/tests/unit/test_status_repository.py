""Interface tests for StatusRepository definition."""

import inspect

from shared.repositories.status import StatusRepository


def test_status_repository_is_abstract_class() -> None:
    assert inspect.isclass(StatusRepository)
    assert inspect.isabstract(StatusRepository)


def test_status_repository_abstract_methods_are_defined() -> None:
    abstract_methods = [
        "update_document_status",
        "update_workspace_status",
    ]
    for name in abstract_methods:
        assert hasattr(StatusRepository, name), f"Missing method {name} on StatusRepository"
        method = getattr(StatusRepository, name)
        assert getattr(method, "__isabstractmethod__", False) is True
