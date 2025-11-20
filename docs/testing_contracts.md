# Testing Contracts

This project distinguishes between interface contracts and implementation details. Tests should verify what a component promises to do (its API), not how it does it.

## Where tests live

- Shared library tests (contracts): test the interfaces defined in the shared package without touching concrete implementations. Target repositories:
  - DocumentRepository
  - UserRepository
  - ChatSessionRepository
  - ChatMessageRepository
  - StatusRepository
- Server tests (integration and service wiring): verify behavior at boundaries, API responses, and orchestration, without asserting details of concrete implementations.

## What to test in the shared contracts

- Abstractness: verify that interface classes are abstract.
- Method presence: verify all required abstract methods exist on the interface.
- Signatures: verify parameter names, default values, and return annotations reflect the intended contract.
- No implementation details: do not instantiate concrete implementations or call concrete methods.

## How to write signature-based tests (examples)

- Use inspect.signature to inspect method parameters and return annotations.
- Verify parameter names and default values, and ensure return annotations reference the correct type names.
- Verify abstract methods are flagged as __isabstractmethod__.

Example pattern (pseudocode):

```python
import inspect
from shared.repositories.document import DocumentRepository

sig = inspect.signature(DocumentRepository.create)
assert [p.name for p in sig.parameters.values() if p.name != 'self'] == [
    'user_id','filename','file_path','file_size','mime_type','content_hash','chunk_count','rag_collection']
assert getattr(DocumentRepository.create, '__isabstractmethod__', False) is True
```

## Running contract tests

- Run contract tests in the shared package:
  - `pytest packages/shared/python/tests/unit/test_document_repository_signature.py`
  - `pytest packages/shared/python/tests/unit/test_user_repository_signature.py`
  - `pytest packages/shared/python/tests/unit/test_chat_session_repository_signature.py`
  - `pytest packages/shared/python/tests/unit/test_chat_message_repository_signature.py`
  - `pytest packages/shared/python/tests/unit/test_status_repository_signature.py`

## Notes

- If you introduce new interfaces in shared, add corresponding signature tests here.
- If a test touches a type that may not exist in all environments (e.g. optional dependencies), guard the test accordingly.
