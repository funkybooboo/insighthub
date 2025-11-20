""Interface signature tests for DocumentRepository."""

import inspect

from shared.repositories.document import DocumentRepository
from shared.models.document import Document


def test_document_repository_signature_create():
    sig = inspect.signature(DocumentRepository.create)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names == [
        "user_id",
        "filename",
        "file_path",
        "file_size",
        "mime_type",
        "content_hash",
        "chunk_count",
        "rag_collection",
    ]
    assert sig.parameters["chunk_count"].default is None
    assert sig.parameters["rag_collection"].default is None
    ret = sig.return_annotation
    assert ret is not inspect._empty
    assert "Document" in str(ret)
    assert getattr(DocumentRepository.create, "__isabstractmethod__", False) is True


def test_document_repository_signature_get_by_id():
    sig = inspect.signature(DocumentRepository.get_by_id)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names == ["document_id"]
    ret = sig.return_annotation
    assert ret is not inspect._empty
    assert "Document" in str(ret)
    assert getattr(DocumentRepository.get_by_id, "__isabstractmethod__", False) is True


def test_document_repository_signature_get_by_user():
    sig = inspect.signature(DocumentRepository.get_by_user)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names == ["user_id", "skip", "limit"]
    ret = sig.return_annotation
    assert ret is not inspect._empty
    assert "Document" in str(ret)
    assert getattr(DocumentRepository.get_by_user, "__isabstractmethod__", False) is True


def test_document_repository_signature_get_by_content_hash():
    sig = inspect.signature(DocumentRepository.get_by_content_hash)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names == ["content_hash"]
    ret = sig.return_annotation
    assert ret is not inspect._empty
    assert "Document" in str(ret)
    assert getattr(DocumentRepository.get_by_content_hash, "__isabstractmethod__", False) is True


def test_document_repository_signature_update_and_delete():
    sig_update = inspect.signature(DocumentRepository.update)
    names = [p.name for i, p in enumerate(list(sig_update.parameters.values())) if i > 0]
    assert names[0] == "document_id"
    assert names[1] == "kwargs"
    ret = sig_update.return_annotation
    assert ret is not inspect._empty
    assert "Document" in str(ret)
    assert getattr(DocumentRepository.update, "__isabstractmethod__", False) is True

    sig_delete = inspect.signature(DocumentRepository.delete)
    names = [p.name for i, p in enumerate(list(sig_delete.parameters.values())) if i > 0]
    assert names == ["document_id"]
    ret = sig_delete.return_annotation
    assert ret is not inspect._empty
    assert "bool" in str(ret)
    assert getattr(DocumentRepository.delete, "__isabstractmethod__", False) is True
