""Utility helpers for interface contract tests."""

import inspect
from typing import Any


def assert_abstract(cls: type, methods: list[str]) -> None:
    for name in methods:
        assert hasattr(cls, name), f"Missing method {name} on {cls.__name__}"
        method = getattr(cls, name)
        assert getattr(method, "__isabstractmethod__", False) is True


def get_signature(cls: type, method_name: str) -> inspect.Signature:
    return inspect.signature(getattr(cls, method_name))


def _param_names(sig: inspect.Signature) -> list[str]:
    return [p.name for i, p in enumerate(list(sig.parameters.values())) if i > 0]


def assert_signature_matches(
    cls: type,
    method_name: str,
    expected_param_names: list[str],
    expected_return_contains: str | None = None,
) -> None:
    sig = get_signature(cls, method_name)
    params = _param_names(sig)
    assert params == expected_param_names, (
        f"{cls.__name__}.{method_name} params mismatch: {params} != {expected_param_names}"
    )
    if expected_return_contains:
        ret = sig.return_annotation
        assert ret is not inspect._empty, f"Missing return annotation for {cls.__name__}.{method_name}"
        ret_str = str(ret)
        assert expected_return_contains in ret_str, (
            f"Return annotation for {cls.__name__}.{method_name} should mention {expected_return_contains}"
        )
