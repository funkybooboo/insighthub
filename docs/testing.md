# Testing Guide

Comprehensive testing infrastructure for the InsightHub RAG system.

## Quick Start

**Client**:
```bash
cd packages/client
bun run test              # Run all tests
bun run test:coverage     # With coverage
bun run storybook         # View component stories
```

**Server**:
```bash
cd packages/server
poetry run pytest                    # Run all tests
poetry run pytest --cov=src          # With coverage
```

**API Testing**: Open `packages/server/bruno` in Bruno client

## Overview

- **Client**: Vitest + Storybook | **Current**: 88 tests, 97.97% coverage
- **Server**: Pytest | **Current**: 27 test files (unit + integration)
- **API**: Bruno + OpenAPI 3.0 specification
- **Quality**: Zero `any` types, strict type checking enabled

## Client Testing (Vitest + Storybook)

**Files**: `packages/client/src/**/*.test.ts(x)`
**Coverage**: 97.97% (88 tests)

**What's Tested**:
- Services (`socket.ts`)
- Redux state (`authSlice.ts`, `chatSlice.ts`)
- Utilities (`chatStorage.ts`)

**Storybook**: `bun run storybook` - Visual component documentation
**Coverage Report**: View HTML at `packages/client/coverage/index.html`

## Server Testing (Pytest)

**Files**: `packages/server/tests/{unit,integration}/**/*.py`
**Structure**: 22 unit tests + 5 integration tests

**Test Markers**:
- `pytest -m unit` - Unit tests with mocks
- `pytest -m integration` - Integration tests with real services (testcontainers)
- `pytest -m database` - Requires PostgreSQL
- `pytest -m blob_storage` - Requires MinIO/S3

**Coverage Report**: View HTML at `packages/server/htmlcov/index.html`

## API Testing

**Bruno Collection**: `packages/server/bruno/`
- Install Bruno from https://www.usebruno.com
- Open collection, select `local` environment, run requests
- Tests for: Health, Auth, Documents, Chat

**OpenAPI Spec**: `packages/server/openapi.yaml`
- Complete API documentation in OpenAPI 3.0 format
- View with: `npx @redocly/cli preview-docs packages/server/openapi.yaml`

## Code Quality

**Client (TypeScript)**:
```bash
bun run build          # Type check + build
bun run lint           # ESLint
bun run format         # Prettier
```
- Strict mode enabled, zero `any` types

**Server (Python)**:
```bash
poetry run black src tests      # Format (100 chars)
poetry run ruff check src       # Lint
poetry run mypy src             # Type check
```
- Type hints required, minimal `type: ignore` usage

## Key Standards

- **Coverage Target**: 80%+ (Client: 97.97%)
- **Test Structure**: Arrange-Act-Assert pattern
- **Mocking**: External dependencies always mocked in unit tests
- **CI/CD**: Automated testing on all PRs via GitHub Actions

## Troubleshooting

| Issue | Solution |
|-------|----------|
| localStorage undefined | Check `vitest.config.ts` has `environment: 'happy-dom'` |
| Server modules not found | Run `poetry install` |
| Bruno tests fail | Ensure server running, check auth token in `local.bru` |
| Low coverage | Run with `--cov-report=term-missing` to find gaps |

## Summary

✅ **Client**: 88 tests, 97.97% coverage
✅ **Server**: 27 test files (unit + integration)
✅ **API**: Bruno collection + OpenAPI 3.0 spec
✅ **Quality**: Strict typing, no shortcuts
