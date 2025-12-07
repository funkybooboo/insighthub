# Polish & Consistency Opportunities (TIER 3)

**Impact**: Small quality-of-life improvements
**RAG Compatibility**: All patterns work for both Vector and Graph RAG

---

## 1. Optional String Normalization

**Problem**: 4 occurrences of "strip string, if empty set to None" pattern in validation code.

**Current Code**:
```python
# Repeated in validation files
if request.title:
    request.title = request.title.strip()
    if not request.title:
        request.title = None

if request.description:
    request.description = request.description.strip()
    if not request.description:
        request.description = None
```

**Solution**:
```python
@dataclass(frozen=True)
class StringValidationError:
    """String validation error."""
    message: str
    field: str
    max_length: int

def normalize_optional_string(
    value: Optional[str],
    field_name: str = "field",
    max_len: Optional[int] = None
) -> Result[Optional[str], StringValidationError]:
    """Normalize optional string: strip whitespace, convert empty to None.

    Args:
        value: String to normalize
        field_name: Name of field being validated (for error messages)
        max_len: Maximum allowed length (optional)

    Returns:
        Result with normalized string (or None if empty) or StringValidationError
    """
    if not value:
        return Success(None)

    normalized = value.strip()
    if not normalized:
        return Success(None)

    if max_len and len(normalized) > max_len:
        return Failure(StringValidationError(
            message=f"{field_name} exceeds maximum length of {max_len}",
            field=field_name,
            max_length=max_len
        ))

    return Success(normalized)

# Usage - errors as values
title_result = normalize_optional_string(request.title, "title", max_len=200)
if isinstance(title_result, Failure):
    return Failure(ValidationError(title_result.failure().message))
request.title = title_result.unwrap()

desc_result = normalize_optional_string(request.description, "description", max_len=1000)
if isinstance(desc_result, Failure):
    return Failure(ValidationError(desc_result.failure().message))
request.description = desc_result.unwrap()
```

**Locations**:
- `src/domains/workspace/chat/session/validation.py:30-40, 73-82`
- `src/domains/workspace/document/validation.py:86-91, 94-96`

**Why Valuable**:
- Consistent string normalization logic
- Built-in max length validation
- Errors as values (no exceptions)
- Clear field identification in errors
- Type-safe validation results

---

## 2. CLI Formatter for Optional Fields

**Problem**: Multiple different patterns for displaying optional fields in CLI output.

**Current Code**:
```python
# Inconsistent patterns across command files
print(f"Description: {response.description or '(not set)'}")
print(f"Title: {response.title if response.title else 'N/A'}")
if response.metadata:
    print(f"Metadata: {response.metadata}")
else:
    print("Metadata: (none)")
```

**Solution**:
```python
class CLIFormatter:
    """Formatting utilities for CLI output."""

    @staticmethod
    def optional(
        value: Optional[Any],
        label: str,
        placeholder: str = "(not set)"
    ) -> str:
        """Format optional field for CLI display.

        Args:
            value: Value to display (may be None or empty string)
            label: Field label
            placeholder: Text to show when value is absent

        Returns:
            Formatted string ready for printing
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            display = placeholder
        else:
            display = str(value)
        return f"{label}: {display}"

    @staticmethod
    def optional_list(
        items: Optional[List[Any]],
        label: str,
        placeholder: str = "(none)"
    ) -> str:
        """Format optional list for CLI display.

        Args:
            items: List to display (may be None or empty)
            label: Field label
            placeholder: Text to show when list is empty

        Returns:
            Formatted string ready for printing
        """
        if not items:
            display = placeholder
        else:
            display = ", ".join(str(item) for item in items)
        return f"{label}: {display}"

# Usage - consistent across all commands
IO.print(CLIFormatter.optional(response.description, "Description"))
IO.print(CLIFormatter.optional(response.title, "Title", placeholder="(untitled)"))
IO.print(CLIFormatter.optional_list(response.tags, "Tags"))
```

**Locations**:
- `src/domains/workspace/commands.py:146-148`
- `src/domains/workspace/chat/session/commands.py:54-56`
- All command files that display optional fields

**Why Valuable**:
- Consistent CLI output formatting
- Handles None and empty string uniformly
- Customizable placeholder text
- Cleaner command code
