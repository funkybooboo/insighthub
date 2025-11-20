"""
Tests for Result type contract.

These tests verify the behavior of the Result type (Ok and Err),
ensuring it provides a consistent API for error handling.
"""

import pytest

from shared.types.result import Ok, Err, Result


class TestOkContract:
    """
    Test the Ok type contract.
    
    Ok represents a successful result and should:
    - Report as Ok (not Err)
    - Allow unwrapping the value
    - Support mapping over the value
    - Be immutable (frozen)
    """

    def test_ok_is_ok(self):
        """Test that Ok reports as ok."""
        result = Ok(42)
        assert result.is_ok() is True
        assert result.is_err() is False

    def test_ok_unwrap_returns_value(self):
        """Test that Ok.unwrap() returns the contained value."""
        result = Ok("success")
        assert result.unwrap() == "success"

    def test_ok_unwrap_or_returns_value(self):
        """Test that Ok.unwrap_or() returns value, not default."""
        result = Ok(100)
        assert result.unwrap_or(0) == 100

    def test_ok_is_immutable(self):
        """Test that Ok is immutable (frozen dataclass)."""
        result = Ok(42)
        with pytest.raises(AttributeError):
            result.value = 100  # type: ignore

    def test_ok_with_different_types(self):
        """Test that Ok works with different value types."""
        # String
        result_str = Ok("hello")
        assert result_str.unwrap() == "hello"
        
        # Integer
        result_int = Ok(123)
        assert result_int.unwrap() == 123
        
        # Dictionary
        result_dict = Ok({"key": "value"})
        assert result_dict.unwrap() == {"key": "value"}
        
        # List
        result_list = Ok([1, 2, 3])
        assert result_list.unwrap() == [1, 2, 3]
        
        # None
        result_none = Ok(None)
        assert result_none.unwrap() is None

    def test_ok_map_transforms_value(self):
        """Test that Ok.map() transforms the contained value."""
        result = Ok(10)
        mapped = result.map(lambda x: x * 2)
        
        assert mapped.is_ok()
        assert mapped.unwrap() == 20

    def test_ok_map_preserves_ok_type(self):
        """Test that mapping over Ok returns Ok."""
        result = Ok("test")
        mapped = result.map(str.upper)
        
        assert isinstance(mapped, Ok)
        assert mapped.unwrap() == "TEST"

    def test_ok_equality(self):
        """Test that Ok instances with same value are equal."""
        result1 = Ok(42)
        result2 = Ok(42)
        result3 = Ok(100)
        
        assert result1 == result2
        assert result1 != result3


class TestErrContract:
    """
    Test the Err type contract.
    
    Err represents a failed result and should:
    - Report as Err (not Ok)
    - Raise on unwrap
    - Return default on unwrap_or
    - Not transform on map
    - Be immutable (frozen)
    """

    def test_err_is_err(self):
        """Test that Err reports as error."""
        result = Err("something went wrong")
        assert result.is_ok() is False
        assert result.is_err() is True

    def test_err_unwrap_raises(self):
        """Test that Err.unwrap() raises ValueError."""
        result = Err("error message")
        
        with pytest.raises(ValueError, match="Called unwrap on Err"):
            result.unwrap()

    def test_err_unwrap_or_returns_default(self):
        """Test that Err.unwrap_or() returns the default value."""
        result = Err("failed")
        assert result.unwrap_or(42) == 42
        assert result.unwrap_or("default") == "default"

    def test_err_is_immutable(self):
        """Test that Err is immutable (frozen dataclass)."""
        result = Err("error")
        with pytest.raises(AttributeError):
            result.error = "new error"  # type: ignore

    def test_err_with_different_error_types(self):
        """Test that Err works with different error types."""
        # String error
        result_str = Err("error message")
        assert result_str.error == "error message"
        
        # Integer error code
        result_int = Err(404)
        assert result_int.error == 404
        
        # Dictionary error
        result_dict = Err({"code": "INVALID", "message": "Bad request"})
        assert result_dict.error["code"] == "INVALID"

    def test_err_map_returns_self(self):
        """Test that Err.map() returns self unchanged."""
        result = Err("error")
        mapped = result.map(lambda x: x * 2)
        
        # Should still be an error with same error value
        assert mapped.is_err()
        assert mapped.error == "error"
        assert mapped is result  # Should be the same object

    def test_err_equality(self):
        """Test that Err instances with same error are equal."""
        result1 = Err("error")
        result2 = Err("error")
        result3 = Err("different")
        
        assert result1 == result2
        assert result1 != result3


class TestResultTypeUsage:
    """
    Test Result type usage patterns.
    
    These tests verify that Result can be used properly
    in real-world scenarios.
    """

    def test_result_type_alias(self):
        """Test that Result type alias works correctly."""
        def divide(a: int, b: int) -> Result[float, str]:
            if b == 0:
                return Err("Division by zero")
            return Ok(a / b)
        
        # Test success case
        result_ok = divide(10, 2)
        assert result_ok.is_ok()
        assert result_ok.unwrap() == 5.0
        
        # Test error case
        result_err = divide(10, 0)
        assert result_err.is_err()
        assert result_err.error == "Division by zero"

    def test_result_with_is_ok_pattern(self):
        """Test using Result with is_ok() pattern."""
        def process(value: int) -> Result[str, str]:
            if value > 0:
                return Ok(f"Processed: {value}")
            return Err("Value must be positive")
        
        result = process(42)
        if result.is_ok():
            message = result.unwrap()
            assert message == "Processed: 42"
        else:
            pytest.fail("Should not reach here")

    def test_result_with_is_err_pattern(self):
        """Test using Result with is_err() pattern."""
        def validate(text: str) -> Result[str, str]:
            if len(text) < 3:
                return Err("Text too short")
            return Ok(text.upper())
        
        result = validate("ab")
        if result.is_err():
            error = result.error
            assert error == "Text too short"
        else:
            pytest.fail("Should not reach here")

    def test_result_chaining_with_map(self):
        """Test chaining operations with map."""
        result = Ok(10).map(lambda x: x * 2).map(lambda x: x + 5).map(str)
        
        assert result.is_ok()
        assert result.unwrap() == "25"

    def test_result_early_return_pattern(self):
        """Test early return pattern with Result."""
        def fetch_user(user_id: int) -> Result[dict, str]:
            if user_id <= 0:
                return Err("Invalid user ID")
            if user_id == 999:
                return Err("User not found")
            return Ok({"id": user_id, "name": "John"})
        
        def get_user_name(user_id: int) -> str:
            result = fetch_user(user_id)
            if result.is_err():
                return f"Error: {result.error}"
            
            user = result.unwrap()
            return user["name"]
        
        assert get_user_name(1) == "John"
        assert get_user_name(0) == "Error: Invalid user ID"
        assert get_user_name(999) == "Error: User not found"

    def test_result_unwrap_or_default_pattern(self):
        """Test using unwrap_or for default values."""
        def try_parse_int(text: str) -> Result[int, str]:
            try:
                return Ok(int(text))
            except ValueError:
                return Err(f"Cannot parse '{text}' as integer")
        
        # Success case
        assert try_parse_int("42").unwrap_or(0) == 42
        
        # Error case with default
        assert try_parse_int("abc").unwrap_or(0) == 0
        assert try_parse_int("xyz").unwrap_or(-1) == -1

    def test_result_replaces_none_pattern(self):
        """
        Test that Result is better than returning None.
        
        With None: unclear if None means "not found" or "error"
        With Result: explicit Ok/Err makes intent clear
        """
        # Old pattern (ambiguous)
        def find_old(items: list, target) -> int | None:
            try:
                return items.index(target)
            except ValueError:
                return None  # Not found? Or error?
        
        # New pattern (explicit)
        def find_new(items: list, target) -> Result[int, str]:
            try:
                return Ok(items.index(target))
            except ValueError:
                return Err("Item not found")
        
        items = [1, 2, 3]
        
        # With Result, intent is clear
        result = find_new(items, 5)
        assert result.is_err()
        assert result.error == "Item not found"
        
        result = find_new(items, 2)
        assert result.is_ok()
        assert result.unwrap() == 1


class TestResultTypeContract:
    """
    Test the Result type contract at a high level.
    
    These tests verify the fundamental properties that
    any Result-like type should have.
    """

    def test_result_is_either_ok_or_err(self):
        """Test that a Result is always either Ok or Err, never both."""
        ok_result = Ok(42)
        assert ok_result.is_ok() and not ok_result.is_err()
        
        err_result = Err("error")
        assert err_result.is_err() and not err_result.is_ok()

    def test_result_types_are_distinct(self):
        """Test that Ok and Err are distinct types."""
        ok_result = Ok(42)
        err_result = Err("error")
        
        assert type(ok_result) != type(err_result)
        assert isinstance(ok_result, Ok)
        assert isinstance(err_result, Err)

    def test_result_preserves_type_information(self):
        """Test that Result preserves type information of contained value."""
        string_result: Ok[str] = Ok("hello")
        int_result: Ok[int] = Ok(42)
        
        assert isinstance(string_result.unwrap(), str)
        assert isinstance(int_result.unwrap(), int)
