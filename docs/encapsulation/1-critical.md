# Critical Encapsulation Opportunities (TIER 1)

**Impact**: ~30 lines of boilerplate elimination
**RAG Compatibility**: All patterns work for both Vector and Graph RAG

---

## 1. Command Guard Helper

**Problem**: 6+ occurrences of identical "no workspace selected" check with same error message.

**Current Code**:
```python
# Repeated in every command that needs workspace
if not self.ctx.current_workspace_id:
    IO.print_error(
        "No workspace selected. This operation requires a workspace.\n"
        "Use 'workspace use <id>' to select a workspace first."
    )
    sys.exit(1)
workspace_id = self.ctx.current_workspace_id
```

**Solution**:
```python
class CommandGuards:
    """Reusable guard functions for CLI commands."""

    @staticmethod
    def require_workspace(ctx: AppContext, operation: str = "this operation") -> int:
        """Ensure workspace is selected or exit with error.

        Args:
            ctx: Application context
            operation: Operation name for error message

        Returns:
            Current workspace ID

        Exits:
            With code 1 if no workspace selected
        """
        if not ctx.current_workspace_id:
            IO.print_error(
                f"No workspace selected. {operation.capitalize()} requires a workspace.\n"
                f"Use 'workspace use <id>' to select a workspace first."
            )
            sys.exit(1)
        return ctx.current_workspace_id

# Usage - one line
workspace_id = CommandGuards.require_workspace(self.ctx, "document upload")
```

**Locations**:
- `src/domains/workspace/document/commands.py:23-27` (4 occurrences)
- `src/domains/workspace/chat/session/commands.py:31-35` (2 occurrences)

**Why Valuable**:
- Reduces 6+ × 7 lines = ~42 lines to 6 lines
- Consistent error messaging
- Makes intent clear: "this command requires workspace"
- Works for both RAG types

---

## 2. Pagination Value Object

**Problem**: Pagination parameters (`skip`, `limit`) repeated in 5+ methods with duplicated validation using exceptions.

**Current Code**:
```python
# Validation repeated in every repository method - uses exceptions
def get_sessions(self, workspace_id: int, skip: int = 0, limit: int = 50):
    if skip < 0:
        raise ValueError("skip must be non-negative")
    if limit <= 0 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    # Later: check if cacheable
    if skip == 0 and limit <= 50:
        # Try cache
        ...
```

**Solution** (errors as values):
```python
from returns.result import Result, Success, Failure
from typing import Optional

@dataclass(frozen=True)
class PaginationError:
    """Pagination validation error."""
    message: str
    field: str

@dataclass(frozen=True)
class Pagination:
    """Pagination parameters with validation."""

    skip: int
    limit: int
    max_limit: int = 100

    @staticmethod
    def create(
        skip: int = 0,
        limit: int = 50,
        max_limit: int = 100
    ) -> Result['Pagination', PaginationError]:
        """Create pagination with validation - errors as values.

        Args:
            skip: Number of items to skip
            limit: Maximum items per page
            max_limit: Maximum allowed limit

        Returns:
            Result with Pagination or PaginationError
        """
        if skip < 0:
            return Failure(PaginationError(
                message="skip must be non-negative",
                field="skip"
            ))

        if limit <= 0:
            return Failure(PaginationError(
                message="limit must be positive",
                field="limit"
            ))

        if limit > max_limit:
            return Failure(PaginationError(
                message=f"limit must not exceed {max_limit}",
                field="limit"
            ))

        return Success(Pagination(skip=skip, limit=limit, max_limit=max_limit))

    def is_cache_eligible(self) -> bool:
        """Check if results should be cached (first page, reasonable size)."""
        return self.skip == 0 and self.limit <= 50

    def offset_limit(self) -> tuple[int, int]:
        """Get SQL OFFSET and LIMIT values."""
        return self.skip, self.limit

# Usage - errors as values
result = Pagination.create(skip=request.skip, limit=request.limit)
if isinstance(result, Failure):
    return Failure(ValidationError(result.failure().message))

pagination = result.unwrap()
if pagination.is_cache_eligible():
    # Try cache
    ...
sessions = repository.get_sessions(workspace_id, *pagination.offset_limit())
```

**Locations**:
- `src/domains/workspace/chat/session/repositories.py` (multiple methods)
- `src/domains/workspace/chat/message/repositories.py` (multiple methods)

**Why Valuable**:
- Centralized validation logic
- Errors as values (no exceptions)
- Self-documenting cache eligibility rules
- Type-safe pagination instead of separate parameters
- Works for any paginated query (both RAG types)

---

## 3. PaginatedResult Value Object

**Problem**: `Tuple[List[T], int]` used for pagination with unclear semantics.

**Current Code**:
```python
# What does the int mean? Total count? Next page?
sessions, total = self.repository.get_sessions(workspace_id, skip, limit)

# Unclear intent
if len(sessions) < limit:
    # Last page?
    pass
```

**Solution**:
```python
@dataclass(frozen=True)
class PaginatedResult(Generic[T]):
    """Result of a paginated query."""

    items: List[T]
    total_count: int
    skip: int = 0
    limit: int = 50

    @property
    def has_next_page(self) -> bool:
        """Check if there are more items beyond current page."""
        return (self.skip + self.limit) < self.total_count

    @property
    def has_previous_page(self) -> bool:
        """Check if there are items before current page."""
        return self.skip > 0

    @property
    def current_page_size(self) -> int:
        """Number of items in current page."""
        return len(self.items)

    @property
    def total_pages(self) -> int:
        """Total number of pages (given current limit)."""
        return (self.total_count + self.limit - 1) // self.limit

# Usage - clear and explicit
result = repository.get_sessions(workspace_id, pagination)
if result.has_next_page:
    IO.print(f"Showing {result.current_page_size} of {result.total_count} sessions")
```

**Locations**:
- `src/domains/workspace/chat/session/orchestrator.py:78`
- `src/domains/workspace/chat/message/orchestrator.py:66`

**Why Valuable**:
- Self-documenting - clear what each field means
- Helpful properties for pagination logic
- Type-safe instead of unnamed tuple
- Works for any paginated query (both RAG types)
