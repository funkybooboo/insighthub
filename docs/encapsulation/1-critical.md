# Critical Encapsulation Opportunities (TIER 1)

**Impact**: ~350 lines of boilerplate elimination
**RAG Compatibility**: All patterns work for both Vector and Graph RAG

---

## 1. Cache Key Centralization

**Problem**: 15+ magic strings for cache keys with inconsistent patterns (mix of colons and underscores).

**Current Code**:
```python
# Inconsistent patterns scattered across data access layers
cache_key = f"insighthub:workspace:{workspace_id}"
cache_key = f"workspace_{workspace_id}_config"
cache_key = f"session:{session_id}:messages"
```

**Solution**:
```python
class CacheKeys:
    """Centralized cache key generation."""

    NAMESPACE = "insighthub"

    @classmethod
    def workspace(cls, workspace_id: int) -> str:
        """Cache key for workspace entity."""
        return f"{cls.NAMESPACE}:workspace:{workspace_id}"

    @classmethod
    def workspace_config(cls, workspace_id: int) -> str:
        """Cache key for workspace RAG config."""
        return f"{cls.NAMESPACE}:workspace:{workspace_id}:config"

    @classmethod
    def chat_session(cls, session_id: int) -> str:
        """Cache key for chat session entity."""
        return f"{cls.NAMESPACE}:session:{session_id}"

    @classmethod
    def chat_session_messages(cls, session_id: int) -> str:
        """Cache key for session messages list."""
        return f"{cls.NAMESPACE}:session:{session_id}:messages"

    @classmethod
    def document(cls, document_id: int) -> str:
        """Cache key for document entity."""
        return f"{cls.NAMESPACE}:document:{document_id}"

# Usage
cache_key = CacheKeys.workspace_config(workspace_id)
```

**Locations**:
- `src/domains/workspace/data_access.py:41, 74, 196`
- `src/domains/workspace/chat/session/data_access.py:41, 109`
- All data access layers

**Why Valuable**:
- Single source of truth for cache key format
- Enforces consistent colon-separated pattern
- Easy to find all cache keys
- Easy to add pattern-based invalidation later
- Works for both RAG types

---

## 2. Validation Chaining Helper

**Problem**: 40+ occurrences of identical validation check-and-return pattern.

**Current Code**:
```python
# Repeated 40+ times across validation functions
result = validate_positive_id(workspace_id)
if isinstance(result, Failure):
    return Failure(result.failure())
workspace_id = result.unwrap()

result = validate_non_empty_name(request.name)
if isinstance(result, Failure):
    return Failure(result.failure())
validated_name = result.unwrap()

result = validate_rag_type(request.rag_type)
if isinstance(result, Failure):
    return Failure(result.failure())
```

**Solution**:
```python
def chain_validations(*validators: Callable[[T], Result[T, E]]) -> Callable[[T], Result[T, E]]:
    """Chain multiple validators, short-circuiting on first failure.

    Args:
        *validators: Validation functions that take value and return Result

    Returns:
        Combined validator function
    """
    def validate(value: T) -> Result[T, E]:
        for validator in validators:
            result = validator(value)
            if isinstance(result, Failure):
                return result
        return Success(value)
    return validate

# Usage - clean and declarative
validate_workspace_request = chain_validations(
    validate_positive_id,
    validate_non_empty_name,
    validate_rag_type
)

result = validate_workspace_request(request)
if isinstance(result, Failure):
    return result
```

**Locations**:
- `src/domains/default_rag_config/validation.py:129-135`
- `src/domains/workspace/chat/session/validation.py:26-28, 69-71, 101-103, 117-119, 133-140`
- `src/domains/workspace/document/validation.py:81-83, 134-140`
- `src/domains/workspace/chat/message/validation.py:19-20, 50-51, 55-56`

**Why Valuable**:
- Eliminates 40+ × 4 lines = ~160 lines of boilerplate
- Declarative validation composition
- Easier to see all validation rules at a glance
- Not RAG-specific

---

## 3. Command Guard Helper

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

## 4. Pagination Value Object

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

## 5. PaginatedResult Value Object

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
