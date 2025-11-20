""Interface signature tests for UserRepository."""

import inspect
from typing import get_args, get_origin

from shared.repositories.user import UserRepository
from shared.models.user import User


def test_user_repository_signature_create():
    sig = inspect.signature(UserRepository.create)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names == ["username", "email", "password", "full_name"]
    assert sig.parameters["full_name"].default is None
    ret = sig.return_annotation
    assert ret is User or ret == User or ret == User | None
    assert getattr(UserRepository.create, "__isabstractmethod__", False) is True


def test_user_repository_signature_get_by_id():
    sig = inspect.signature(UserRepository.get_by_id)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names == ["user_id"]
    ret = sig.return_annotation
    assert ret is User or ret == User or ret == User | None
    assert getattr(UserRepository.get_by_id, "__isabstractmethod__", False) is True


def test_user_repository_signature_get_by_username():
    sig = inspect.signature(UserRepository.get_by_username)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names == ["username"]
    ret = sig.return_annotation
    assert ret is User or ret == User or ret == User | None
    assert getattr(UserRepository.get_by_username, "__isabstractmethod__", False) is True


def test_user_repository_signature_get_by_email():
    sig = inspect.signature(UserRepository.get_by_email)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names == ["email"]
    ret = sig.return_annotation
    assert ret is User or ret == User or ret == User | None
    assert getattr(UserRepository.get_by_email, "__isabstractmethod__", False) is True


def test_user_repository_signature_get_all():
    sig = inspect.signature(UserRepository.get_all)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names == ["skip", "limit"]
    ret = sig.return_annotation
    origin = get_origin(ret)
    args = get_args(ret)
    assert origin in (list, list.__class__, None)
    assert args and args[0] is User
    assert getattr(UserRepository.get_all, "__isabstractmethod__", False) is True


def test_user_repository_signature_update():
    sig = inspect.signature(UserRepository.update)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names[0] == "user_id"
    assert names[1] == "kwargs"
    ret = sig.return_annotation
    assert ret is User or ret == User or ret == User | None
    assert getattr(UserRepository.update, "__isabstractmethod__", False) is True


def test_user_repository_signature_delete():
    sig = inspect.signature(UserRepository.delete)
    names = [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]
    assert names == ["user_id"]
    ret = sig.return_annotation
    assert ret is bool or ret == bool
    assert getattr(UserRepository.delete, "__isabstractmethod__", False) is True
