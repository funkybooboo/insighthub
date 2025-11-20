# Error Handling Guide

This guide explains when to use **exceptions**, **Result types**, and **Option types** in the InsightHub codebase.

## Quick Decision Tree

```
Is this an expected, recoverable condition?
├─ YES: Use Result or Option
│   ├─ Can return None? → Use Option[T]
│   └─ Has error details? → Use Result[T, E]
│
└─ NO: Use Exception
    ├─ Programming error (bug)
    ├─ System failure (out of memory, disk full)
    └─ Unrecoverable error
```

## Use Option[T] When

**Option represents a value that may or may not exist.**

### Good Uses:
- Finding a record that might not exist
- Accessing an optional configuration value
- Getting the first/last element of a possibly empty collection
- Parsing that may or may not succeed (when error details don't matter)

### Examples:

```python
# Good: Finding a user that might not exist
def find_user_by_email(email: str) -> Option[User]:
    user = db.query(User).filter_by(email=email).first()
    return from_nullable(user)

# Usage
result = find_user_by_email("test@example.com")
if result.is_some():
    user = result.unwrap()
    print(f"Found: {user.name}")
else:
    print("User not found")

# Good: Getting an optional config value
def get_config(key: str) -> Option[str]:
    value = os.getenv(key)
    return from_nullable(value)

# Usage with default
api_url = get_config("API_URL").unwrap_or("http://localhost:5000")

# Good: First element of collection
def first(items: list[T]) -> Option[T]:
    if len(items) > 0:
        return Some(items[0])
    return Nothing()
```

## Use Result[T, E] When

**Result represents an operation that can succeed or fail with details about why it failed.**

### Good Uses:
- Operations that can fail for known reasons
- Validation that needs to report specific errors
- API calls that return error codes/messages
- File operations that need error details
- Database operations where you need to know what went wrong

### Examples:

```python
# Good: Operation with detailed error
def parse_document(file_path: str) -> Result[Document, str]:
    try:
        content = read_file(file_path)
        return Ok(Document(content=content))
    except FileNotFoundError:
        return Err(f"File not found: {file_path}")
    except PermissionError:
        return Err(f"Permission denied: {file_path}")
    except Exception as e:
        return Err(f"Failed to parse: {str(e)}")

# Usage
result = parse_document("paper.pdf")
if result.is_ok():
    doc = result.unwrap()
    process(doc)
else:
    logger.error(f"Parse failed: {result.error}")
    return error_response(result.error)

# Good: Validation with specific errors
def validate_workspace(name: str, user_id: int) -> Result[None, str]:
    if len(name) < 3:
        return Err("Workspace name must be at least 3 characters")
    if len(name) > 100:
        return Err("Workspace name must be less than 100 characters")
    if not is_user_allowed(user_id):
        return Err("User does not have permission to create workspace")
    return Ok(None)

# Usage
result = validate_workspace(name, user_id)
if result.is_err():
    return {"error": result.error}, 400

# Good: Repository operations
def update_document_status(doc_id: int, status: str) -> Result[Document, str]:
    doc = db.query(Document).get(doc_id)
    if not doc:
        return Err(f"Document {doc_id} not found")
    
    doc.status = status
    db.commit()
    return Ok(doc)
```

## Use Exceptions When

**Exceptions are for unexpected, exceptional conditions that indicate bugs or system failures.**

### Good Uses:
- Programming errors (assertions, invariant violations)
- System failures (out of memory, disk full)
- Critical errors that can't be recovered from
- Framework/library errors that you can't control

### Examples:

```python
# Good: Programming error
def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Division by zero - caller should check before calling")
    return a / b

# Good: Invariant violation
def process_chunks(doc: Document):
    if not doc.chunks:
        raise ValueError("Document must have chunks before processing")
    # ... process chunks

# Good: Critical system error (let it bubble up)
def initialize_database():
    # If this fails, the app can't run - let exception propagate
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

# Good: Framework error (can't use Result here)
@app.route("/users/<int:user_id>")
def get_user(user_id: int):
    # Flask expects exceptions for 404, not Result
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())
```

## Bad Examples (Don't Do This)

```python
# BAD: Using None instead of Option
def find_user(user_id: int) -> User | None:
    # Ambiguous - None could mean "not found" or "error"
    return db.query(User).get(user_id)

# GOOD: Use Option for clarity
def find_user(user_id: int) -> Option[User]:
    user = db.query(User).get(user_id)
    return from_nullable(user)

# BAD: Using exceptions for expected conditions
def get_user(user_id: int) -> User:
    user = db.query(User).get(user_id)
    if not user:
        raise ValueError("User not found")  # Expected condition!
    return user

# GOOD: Use Result for expected failures
def get_user(user_id: int) -> Result[User, str]:
    user = db.query(User).get(user_id)
    if not user:
        return Err("User not found")
    return Ok(user)

# BAD: Using Result for programming errors
def calculate(value: int) -> Result[int, str]:
    if value < 0:
        return Err("Value must be positive")  # This is a bug!
    return Ok(value * 2)

# GOOD: Use assertion/exception for programming errors
def calculate(value: int) -> int:
    assert value >= 0, "Value must be positive"
    return value * 2

# BAD: Catching and returning Result for system errors
def read_file(path: str) -> Result[str, str]:
    try:
        with open(path) as f:
            return Ok(f.read())
    except MemoryError:  # System error!
        return Err("Out of memory")

# GOOD: Let system errors propagate
def read_file(path: str) -> Result[str, str]:
    try:
        with open(path) as f:
            return Ok(f.read())
    except FileNotFoundError:
        return Err(f"File not found: {path}")
    # MemoryError will propagate - can't recover from it
```

## Converting Between Types

```python
from shared.types import Option, Result, from_nullable

# Option to Result
def option_to_result(opt: Option[T], error: E) -> Result[T, E]:
    if opt.is_some():
        return Ok(opt.unwrap())
    return Err(error)

# Result to Option (discards error details)
def result_to_option(result: Result[T, E]) -> Option[T]:
    if result.is_ok():
        return Some(result.unwrap())
    return Nothing()

# Nullable to Option
user: User | None = db.query(User).first()
opt_user: Option[User] = from_nullable(user)

# Option to Nullable (for legacy code)
user: User | None = opt_user.unwrap_or(None)
```

## Summary Table

| Situation | Use | Reason |
|-----------|-----|--------|
| Value might not exist | `Option[T]` | Explicit "no value" |
| Operation can fail (need error details) | `Result[T, E]` | Explicit error handling |
| Programming error | `Exception` | Indicates a bug |
| System failure | `Exception` | Can't recover |
| Database record not found | `Option[T]` or `Result[T, E]` | Expected condition |
| Validation failure | `Result[T, E]` | Need error message |
| Config value missing | `Option[T]` | Use default if missing |
| API call failed | `Result[T, E]` | Need status/error |
| Invariant violated | `Exception` | Programming error |

## Benefits of This Approach

1. **Explicit error handling**: Caller knows function can fail
2. **Type safety**: Compiler enforces error checking
3. **No silent failures**: Can't forget to check for errors
4. **Better than None**: Clear intent, no ambiguity
5. **Composable**: Can chain operations with `map`, `and_then`
6. **Self-documenting**: Return type shows possible outcomes

## Migration Strategy

When updating existing code:

1. Start with public APIs and work inward
2. Keep backward compatibility by catching Result/Option at boundaries
3. Update tests to verify Result/Option behavior
4. Document why you chose Result vs Option vs Exception
