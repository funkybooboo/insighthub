"""
Tests for the hello world module.
"""

import pytest
from src.hello import greet


def test_greet_returns_greeting() -> None:
    """Test that greet returns a proper greeting message."""
    result = greet("Alice")
    assert result == "Hello, Alice!"


def test_greet_with_world() -> None:
    """Test that greet works with 'World'."""
    result = greet("World")
    assert result == "Hello, World!"


def test_greet_empty_name_raises_error() -> None:
    """Test that greet raises ValueError for empty name."""
    with pytest.raises(ValueError, match="Name cannot be empty"):
        greet("")


def test_greet_with_punctuation() -> None:
    """Test that greet handles punctuation characters."""
    result = greet("O'Brien")
    assert result == "Hello, O'Brien!"
