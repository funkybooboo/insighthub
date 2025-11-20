""Interface tests for DocumentRepository definition."""

import inspect

from shared.repositories.document import DocumentRepository


def test_document_repository_is_abstract_class() -> None:
    assert inspect.isclass(DocumentRepository)
    assert inspect.isabstract(DocumentRepository)


def test_document_repository_abstract_methods_are_defined() -> None:
    abstract_methods = [
        "create",
        "get_by_id",
        "get_by_user",
        "get_by_content_hash",
        "update",
        "delete",
    ]
    for name in abstract_methods:
        assert hasattr(DocumentRepository, name), f"Missing method {name} on DocumentRepository"
        method = getattr(DocumentRepository, name)
        assert getattr(method, "__isabstractmethod__", False) is True
