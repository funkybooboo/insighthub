"""
Behavior tests for Option type.

These tests verify the Option type (Some and Nothing) provides
a consistent API for nullable value handling.
"""

import pytest

from shared.types.option import Some, Nothing, Option


class TestSomeBehavior:
    """Test Some type input/output behavior."""

    def test_some_is_some(self) -> None:
        """Some reports as some, not nothing."""
        option = Some(42)

        assert option.is_some() is True
        assert option.is_nothing() is False

    def test_some_unwrap_returns_value(self) -> None:
        """Some.unwrap() returns the contained value."""
        option = Some("hello")

        assert option.unwrap() == "hello"

    def test_some_unwrap_or_returns_value_not_default(self) -> None:
        """Some.unwrap_or() returns value, ignoring default."""
        option = Some(100)

        assert option.unwrap_or(0) == 100

    def test_some_is_immutable(self) -> None:
        """Some is immutable (frozen dataclass)."""
        option = Some(42)

        with pytest.raises(AttributeError):
            option.value = 100  # type: ignore

    def test_some_with_none_value(self) -> None:
        """Some can contain None as a value."""
        option = Some(None)

        assert option.is_some() is True
        assert option.unwrap() is None

    def test_some_map_transforms_value(self) -> None:
        """Some.map() transforms the contained value."""
        option = Some(10)

        mapped = option.map(lambda x: x * 2)

        assert mapped.is_some()
        assert mapped.unwrap() == 20

    def test_some_map_changes_type(self) -> None:
        """Some.map() can change the contained type."""
        option = Some(42)

        mapped = option.map(str)

        assert mapped.unwrap() == "42"

    def test_some_equality(self) -> None:
        """Some instances with same value are equal."""
        assert Some(42) == Some(42)
        assert Some(42) != Some(100)
        assert Some("a") == Some("a")

    def test_some_with_different_types(self) -> None:
        """Some works with different value types."""
        assert Some("string").unwrap() == "string"
        assert Some(123).unwrap() == 123
        assert Some([1, 2, 3]).unwrap() == [1, 2, 3]
        assert Some({"key": "value"}).unwrap() == {"key": "value"}


class TestNothingBehavior:
    """Test Nothing type input/output behavior."""

    def test_nothing_is_nothing(self) -> None:
        """Nothing reports as nothing, not some."""
        option = Nothing()

        assert option.is_some() is False
        assert option.is_nothing() is True

    def test_nothing_unwrap_raises(self) -> None:
        """Nothing.unwrap() raises ValueError."""
        option = Nothing()

        with pytest.raises(ValueError, match="Called unwrap on Nothing"):
            option.unwrap()

    def test_nothing_unwrap_or_returns_default(self) -> None:
        """Nothing.unwrap_or() returns the default value."""
        option: Option[int] = Nothing()

        assert option.unwrap_or(42) == 42
        assert option.unwrap_or("default") == "default"

    def test_nothing_map_returns_nothing(self) -> None:
        """Nothing.map() returns Nothing unchanged."""
        option: Option[int] = Nothing()

        mapped = option.map(lambda x: x * 2)

        assert mapped.is_nothing()

    def test_nothing_equality(self) -> None:
        """All Nothing instances are equal."""
        assert Nothing() == Nothing()


class TestOptionUsagePatterns:
    """Test Option type usage patterns."""

    def test_option_replaces_none_check(self) -> None:
        """Option makes null handling explicit."""

        def find_user(user_id: int) -> Option[dict]:
            users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
            if user_id in users:
                return Some(users[user_id])
            return Nothing()

        # Found user
        result = find_user(1)
        assert result.is_some()
        assert result.unwrap()["name"] == "Alice"

        # Not found
        result = find_user(999)
        assert result.is_nothing()

    def test_option_with_is_some_pattern(self) -> None:
        """Using is_some() for conditional handling."""

        def get_config_value(key: str) -> Option[str]:
            config = {"host": "localhost", "port": "8080"}
            if key in config:
                return Some(config[key])
            return Nothing()

        result = get_config_value("host")
        if result.is_some():
            value = result.unwrap()
            assert value == "localhost"
        else:
            pytest.fail("Should have found host")

    def test_option_with_unwrap_or_pattern(self) -> None:
        """Using unwrap_or() for default values."""

        def get_setting(key: str) -> Option[int]:
            settings = {"timeout": 30}
            if key in settings:
                return Some(settings[key])
            return Nothing()

        # Existing setting
        assert get_setting("timeout").unwrap_or(60) == 30

        # Missing setting with default
        assert get_setting("retries").unwrap_or(3) == 3

    def test_option_map_chaining(self) -> None:
        """Chaining map operations on Option."""
        option = Some(10)

        result = option.map(lambda x: x * 2).map(lambda x: x + 5).map(str)

        assert result.is_some()
        assert result.unwrap() == "25"

    def test_nothing_map_chaining_short_circuits(self) -> None:
        """Map on Nothing short-circuits the chain."""
        option: Option[int] = Nothing()

        # None of these functions should be called
        result = option.map(lambda x: x * 2).map(lambda x: x + 5)

        assert result.is_nothing()


class TestOptionTypeContract:
    """Test fundamental Option type properties."""

    def test_option_is_either_some_or_nothing(self) -> None:
        """Option is always either Some or Nothing, never both."""
        some = Some(42)
        assert some.is_some() and not some.is_nothing()

        nothing: Option[int] = Nothing()
        assert nothing.is_nothing() and not nothing.is_some()

    def test_some_and_nothing_are_distinct_types(self) -> None:
        """Some and Nothing are distinct types."""
        some = Some(42)
        nothing = Nothing()

        assert type(some) != type(nothing)
        assert isinstance(some, Some)
        assert isinstance(nothing, Nothing)
