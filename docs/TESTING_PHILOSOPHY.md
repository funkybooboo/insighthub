# Testing Philosophy: Contracts First

Core Principle
- Test the interface contract, not implementation details. Interface tests live in the shared library; server tests focus on integration and orchestration.

Where tests live
- Shared library tests (contracts): verify interfaces defined in shared (DocumentRepository, UserRepository, ChatSessionRepository, ChatMessageRepository, StatusRepository) including abstractness and signatures. Do not instantiate or call concrete implementations.
- Server tests (integration): verify API endpoints, service orchestration, and error handling. Avoid testing concrete storage or repository implementations.

Examples
- Good: contract-like test for interface existence and signatures
  - test_document_repository_signature.py uses inspect.signature to validate parameter names and return types.

- Bad: testing internal implementation in server tests
  - Avoid calling InMemoryBlobStorage directly in server tests.

What makes a good test
- Tests contracts, not details: validates that the interface defines the expected API.
- Tests behavior that matters to users via service-level flows, not implementation specifics.
- Tests remain robust to implementation changes.

Action items
- Move or remove tests that exercise implementation details from server tests.
- Keep only interface contract tests in shared, and integration/service tests in server.
