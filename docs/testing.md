# Testing Guide

Comprehensive testing strategy and guide for the InsightHub dual RAG system, covering unit tests, integration tests, E2E tests, and API testing.

## Table of Contents

- [Quick Start](#quick-start)
- [Testing Philosophy](#testing-philosophy)
- [Client Testing](#client-testing)
  - [Unit Tests (Vitest)](#unit-tests-vitest)
  - [E2E Tests (Playwright)](#e2e-tests-playwright)
  - [Component Stories (Storybook)](#component-stories-storybook)
- [Server Testing](#server-testing)
  - [Unit Tests (Pytest)](#unit-tests-pytest)
  - [Integration Tests (Testcontainers)](#integration-tests-testcontainers)
  - [API Tests (Bruno)](#api-tests-bruno)
- [Worker Testing](#worker-testing)
- [Coverage Reports](#coverage-reports)
- [Continuous Integration](#continuous-integration)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Run All Tests

```bash
# Client tests (from packages/client)
cd packages/client
task test              # Unit tests (438 tests passing)
task test:e2e          # E2E tests
task storybook         # Component documentation

# Server tests (from packages/server)
cd packages/server
task test              # Unit and integration tests
task test:api          # API tests (Bruno)

# Worker tests (from packages/workers)
cd packages/workers/{worker}
task test              # Worker-specific tests
```

### Test Categories Overview

| Test Type | Framework | Purpose | Location |
|------------|------------|---------|----------|
| Unit Tests | Vitest/Pytest | Test components in isolation | `src/**/*.test.*` |
| Integration Tests | Testcontainers | Test component interactions | `tests/integration/` |
| E2E Tests | Playwright | Test user workflows | `e2e/**/*.spec.ts` |
| API Tests | Bruno | Test REST endpoints | `bruno/**/*.bru` |
| Component Stories | Storybook | Visual documentation | `src/**/*.stories.*` |

---

## Testing Philosophy

### Core Principles

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Real over Mock**: Use dummy implementations instead of mocks when possible
3. **Fast Feedback**: Unit tests should execute in under 100ms
4. **Comprehensive Coverage**: Test happy paths, edge cases, and error conditions
5. **Maintainability**: Tests should be as maintainable as production code

### Testing Pyramid

```
    E2E Tests (Few)
       ^
  Integration Tests (Some)
       ^
    Unit Tests (Many)
```

- **Unit Tests**: 70% - Test individual functions and components
- **Integration Tests**: 20% - Test component interactions
- **E2E Tests**: 10% - Test complete user workflows

---

## Client Testing

### Unit Tests (Vitest)

**Framework**: Vitest + React Testing Library + MSW

**What it tests**: Component logic, state management, utility functions, API client behavior

**Location**: `packages/client/src/**/*.test.{ts,tsx}`

**Commands**:
```bash
cd packages/client

# Run all unit tests
task test
# or: bun run test:run

# Run tests in watch mode (re-runs on file changes)
task test:watch
# or: bun run test

# Run tests with coverage report
task test:coverage
# or: bun run test:coverage

# Run tests with interactive UI
task test:ui
# or: bun run test:ui

# Run specific test file
bun run test:run src/components/auth/LoginForm.test.tsx
```

**Configuration**: `vitest.config.ts`

**Key Features**:
- **MSW Integration**: Mock API responses for consistent testing
- **React Testing Library**: Test components from user perspective
- **Coverage Reporting**: Detailed coverage with v8
- **TypeScript Support**: Full type checking in tests

**Coverage Thresholds**:
- Lines: > 80%
- Functions: > 80%
- Branches: > 75%
- Statements: > 80%

**Current Stats**: 438 tests passing across 17 test files

**Test Categories**:
- Component tests: 200+ tests
- Redux slice tests: 100+ tests
- Service/utility tests: 100+ tests
- Storybook stories: 50+ stories

**Example Test Structure**:
```typescript
// src/components/auth/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { store } from '../../store';
import LoginForm from './LoginForm';

const renderWithProvider = (component: React.ReactElement) => {
  return render(
    <Provider store={store}>
      {component}
    </Provider>
  );
};

describe('LoginForm', () => {
  test('renders login form correctly', () => {
    renderWithProvider(<LoginForm />);
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('shows validation errors for empty fields', async () => {
    renderWithProvider(<LoginForm />);
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    await userEvent.click(submitButton);
    
    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
  });

  test('submits form with valid credentials', async () => {
    renderWithProvider(<LoginForm />);
    
    await userEvent.type(screen.getByLabelText(/email/i), 'test@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/login successful/i)).toBeInTheDocument();
    });
  });
});
```

### E2E Tests (Playwright)

**Framework**: Playwright

**What it tests**: Complete user workflows across the entire application

**Location**: `packages/client/e2e/**/*.spec.ts`

**Commands**:
```bash
cd packages/client

# Run all E2E tests (headless)
task test:e2e
# or: npx playwright test

# Run with interactive UI mode (recommended for development)
task test:e2e:ui
# or: npx playwright test --ui

# Run in headed mode (see browser actions)
task test:e2e:headed
# or: npx playwright test --headed

# Run specific test file
npx playwright test e2e/auth/signup.spec.ts

# Run tests in debug mode
npx playwright test --debug

# View test report
npx playwright show-report
```

**Configuration**: `playwright.config.ts`

**Browser Coverage**:
- Chromium (Desktop Chrome)
- Firefox
- WebKit (Safari)
- Mobile Chrome
- Mobile Safari

**Example Test Scenarios**:
```typescript
// e2e/auth/complete-user-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Authentication Flow', () => {
  test('should complete signup to chat workflow', async ({ page }) => {
    // Navigate to application
    await page.goto('http://localhost:3000');
    
    // Signup flow
    await page.click('text=Sign Up');
    await page.fill('[data-testid="username-input"]', 'testuser');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'password123');
    await page.click('[data-testid="signup-button"]');
    
    // Should redirect to main app
    await expect(page).toHaveURL(/\/workspaces/);
    
    // Create workspace
    await page.click('text=Create New Workspace');
    await page.fill('[data-testid="workspace-name"]', 'Test Workspace');
    await page.click('[data-testid="create-workspace-btn"]');
    
    // Wait for workspace to be ready
    await expect(page.locator('[data-testid="workspace-status"]')).toContainText('ready');
    
    // Upload document
    await page.setInputFiles('[data-testid="file-input"]', 'test-files/sample.pdf');
    await expect(page.locator('[data-testid="document-status"]')).toContainText('processing');
    
    // Wait for processing to complete
    await expect(page.locator('[data-testid="document-status"]')).toContainText('ready', { timeout: 30000 });
    
    // Send chat message
    await page.fill('[data-testid="chat-input"]', 'What is this document about?');
    await page.click('[data-testid="send-button"]');
    
    // Should receive response
    await expect(page.locator('[data-testid="chat-response"]')).toBeVisible({ timeout: 10000 });
  });
});
```

### Component Stories (Storybook)

**Framework**: Storybook

**What it provides**: Visual component documentation and interactive testing

**Location**: `packages/client/src/**/*.stories.tsx`

**Commands**:
```bash
cd packages/client

# Run Storybook dev server (opens at http://localhost:6006)
task storybook
# or: bun run storybook

# Build static Storybook (for deployment)
task storybook:build
# or: bun run build-storybook
```

**Configuration**: `.storybook/main.ts`

**Available Stories**:
- **Authentication Components**:
  - `LoginForm.stories.tsx` - Login form states and interactions
  - `SignupForm.stories.tsx` - Signup form validation
  - `UserMenu.stories.tsx` - User menu variations

- **Chat Components**:
  - `ChatSidebar.stories.tsx` - Session management UI
  - `ChatInput.stories.tsx` - Message input states
  - `ChatMessages.stories.tsx` - Message display variations

- **Upload Components**:
  - `FileUpload.stories.tsx` - File upload states and progress

**Example Story Structure**:
```typescript
// src/components/chat/ChatInput.stories.tsx
import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn } from '@storybook/test';
import ChatInput from './ChatInput';

const meta: Meta<typeof ChatInput> = {
  title: 'Components/Chat/ChatInput',
  component: ChatInput,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    onSendMessage: fn(),
    placeholder: 'Type your message...',
    disabled: false,
  },
};

export const Disabled: Story = {
  args: {
    ...Default.args,
    disabled: true,
  },
};

export const WithPlaceholder: Story = {
  args: {
    ...Default.args,
    placeholder: 'Ask about your documents...',
  },
};
```

---

## Server Testing

### Unit Tests (Pytest)

**Framework**: Pytest with dummy implementations

**What it tests**: API endpoints, business logic, data models, LLM providers

**Location**: `packages/server/tests/unit/*.py`

**Commands**:
```bash
cd packages/server

# Run all tests with coverage
task test
# or: poetry run pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# Run only unit tests (fast)
task test:unit
# or: poetry run pytest tests/unit/ -v

# Run tests in watch mode
task test:watch
# or: poetry run ptw tests/

# Run specific test file
poetry run pytest tests/unit/test_document_service.py -v
```

**Configuration**: `pyproject.toml` (pytest section)

**Testing Philosophy**: Use dummy implementations, not mocks

```python
# Example: Dummy implementation for testing
class DummyEmbeddings(EmbeddingModel):
    """Dummy embeddings that return fixed vectors for testing."""
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in texts]
    
    def get_dimension(self) -> int:
        return 3

# In tests
def test_vector_rag_add_documents():
    dummy_store = InMemoryVectorStore()
    dummy_embeddings = DummyEmbeddings()
    dummy_chunker = CharacterChunker(chunk_size=10)
    
    rag = VectorRag(
        vector_store=dummy_store,
        embedding_model=dummy_embeddings,
        chunker=dummy_chunker
    )
    
    count = rag.add_documents([{"text": "test document"}])
    assert count > 0
```

**Test Categories**:
- **Service Tests**: Business logic in domain services
- **Repository Tests**: Data access layer (with in-memory implementations)
- **API Tests**: Route handlers and request/response processing
- **Utility Tests**: Helper functions and validators

### Integration Tests (Testcontainers)

**Framework**: Pytest + Testcontainers

**What it tests**: Component interactions with real external services

**Location**: `packages/server/tests/integration/*.py`

**Commands**:
```bash
cd packages/server

# Run only integration tests (requires Docker)
task test:integration
# or: poetry run pytest tests/integration/ -v -s
```

**Testcontainers Used**:
- **PostgreSQL Container**: Real database for integration tests
- **Qdrant Container**: Real vector database
- **RabbitMQ Container**: Real message queue
- **MinIO Container**: Real object storage

**Example Integration Test**:
```python
# tests/integration/test_document_endpoints.py
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.qdrant import QdrantContainer

@pytest.fixture(scope="function")
def postgres_container():
    """Spin up temporary PostgreSQL container for test."""
    with PostgresContainer("postgres:16") as container:
        yield container

@pytest.fixture(scope="function")
def qdrant_container():
    """Spin up temporary Qdrant container for test."""
    with QdrantContainer("qdrant/qdrant:latest") as container:
        yield container

def test_document_upload_integration(postgres_container, qdrant_container):
    """Test document upload with real database and vector store."""
    # Use real services running in Docker
    store = QdrantVectorStore(
        host=qdrant_container.get_container_host_ip(),
        port=qdrant_container.get_exposed_port(6333),
        collection_name="test_collection"
    )
    
    # Test actual database operations
    store.add(vectors=[[0.1, 0.2]], ids=["1"], metadata=[{"test": "data"}])
    results = store.search(query_vector=[0.1, 0.2], top_k=1)
    assert len(results) == 1
```

### API Tests (Bruno)

**Framework**: Bruno (API testing tool)

**What it tests**: REST API endpoints, authentication, file uploads, chat functionality

**Location**: `packages/server/bruno/**/*.bru`

**Prerequisites**:
```bash
# Install Bruno CLI globally
npm install -g @usebruno/cli
```

**Commands**:
```bash
cd packages/server

# Make sure server is running first!
task server  # In one terminal

# Run Bruno API tests (in another terminal)
task test:api
# or: bru run --env local bruno/

# Run with verbose output
task test:api:verbose
# or: bru run --env local --verbose bruno/
```

**Collection Structure**:
```
bruno/
- environments/
|   - local.bru           # Local environment config
- Auth/                   # Authentication tests
|   - Signup_Success.bru
|   - Login_Success.bru
|   - Login_Invalid_Credentials.bru
- Chat/                   # Chat API tests
|   - Send_Message_Success.bru
|   - Send_Message_Rate_Limit.bru
- Documents/              # File upload tests
|   - Upload_PDF_Success.bru
|   - Upload_File_Too_Large.bru
- Workspaces/             # Workspace management tests
|   - Create_Workspace_Success.bru
|   - Delete_Workspace_Success.bru
- System/                 # System health tests
    - Health_Check.bru
```

**Example Bruno Test**:
```bruno
# bruno/Documents/Upload_PDF_Success.bru
meta {
  name: Upload PDF Success
  type: http
  seq: 1
}

post {
  url: {{base_url}}/api/workspaces/{{workspace_id}}/documents/upload
  body: multipart
  formData: {
    "file": {
      type: file
      src: test-files/sample.pdf
    }
  }
  headers: {
    Authorization: Bearer {{auth_token}}
    Content-Type: multipart/form-data
  }
}

assert {
  res.status: eq 200
  res.body.document.id: exists
  res.body.document.filename: eq "sample.pdf"
}
```

**Test Scenarios Covered**:
- [x] User signup and login flows
- [x] Authentication and authorization
- [x] Document upload (PDF, TXT) with validation
- [x] Workspace CRUD operations
- [x] Chat message sending and streaming
- [x] Rate limiting and error handling
- [x] Health checks and system status

---

## Worker Testing

### Worker Unit Tests

**Location**: `packages/workers/{worker}/tests/*.py`

**Commands**:
```bash
cd packages/workers/{worker}

# Run worker tests
task test
# or: poetry run pytest tests/ -v
```

**Test Focus**:
- Event handling logic
- Document processing workflows
- Error handling and recovery
- Integration with RAG components

**Example Worker Test**:
```python
# packages/workers/parser/tests/test_parser.py
import pytest
from src.main import parse_document
from shared.types import Document

def test_parse_pdf_document():
    """Test PDF document parsing."""
    # Test with sample PDF content
    result = parse_document({
        'file_path': 'test-files/sample.pdf',
        'workspace_id': 'test-workspace',
        'document_id': 'test-doc'
    })
    
    assert isinstance(result, Document)
    assert len(result.text) > 0
    assert result.metadata['source'] == 'test-files/sample.pdf'

def test_parse_text_document():
    """Test text document parsing."""
    result = parse_document({
        'file_path': 'test-files/sample.txt',
        'workspace_id': 'test-workspace',
        'document_id': 'test-doc'
    })
    
    assert isinstance(result, Document)
    assert 'sample text content' in result.text.lower()
```

---

## Coverage Reports

### Client Coverage

**View Coverage**:
```bash
cd packages/client
task test:coverage
```

**Reports Generated**:
- **Terminal**: Summary table with coverage percentages
- **HTML**: `coverage/index.html` (open in browser for detailed view)
- **LCOV**: `coverage/lcov.info` (for CI tools)

**Coverage Analysis**:
- Per-file coverage breakdown
- Uncovered line highlighting
- Branch coverage analysis
- Function coverage tracking

### Server Coverage

**View Coverage**:
```bash
cd packages/server
task test
```

**Reports Generated**:
- **Terminal**: Summary with missing lines
- **HTML**: `htmlcov/index.html` (open in browser)
- **XML**: For CI integration

**Coverage Targets**:
- **Unit Tests**: > 80% line coverage
- **Integration Tests**: > 70% line coverage
- **Combined**: > 75% overall coverage

---

## Continuous Integration

### GitHub Actions Workflows

**Client CI** (`.github/workflows/client-ci.yml`):
```yaml
- Checkout code
- Setup Node.js/Bun
- Install dependencies
- Run linting (ESLint)
- Run type checking (TypeScript)
- Run unit tests (Vitest)
- Build application
- Upload coverage reports
```

**Server CI** (`.github/workflows/server-ci.yml`):
```yaml
- Checkout code
- Setup Python
- Install dependencies (Poetry)
- Run linting (Ruff)
- Run type checking (MyPy)
- Run unit tests (Pytest)
- Upload coverage reports
```

### Quality Gates

**All Tests Must Pass**:
- Unit tests: 100% pass rate
- Coverage thresholds met
- No critical security vulnerabilities
- Build successful

**Code Quality Checks**:
- Linting with no errors
- Type checking with no issues
- Code formatting compliance
- Dependency vulnerability scan

---

## Best Practices

### Test Organization

**File Structure**:
```
src/
- components/
|   - ComponentName.tsx
|   - ComponentName.test.tsx
|   - ComponentName.stories.tsx
|   - index.ts
- services/
    - service.ts
    - service.test.ts
```

**Naming Conventions**:
- Test files: `*.test.{ts,tsx}` or `*.spec.py`
- Test descriptions: Should be human-readable and specific
- Story files: `*.stories.{ts,tsx}`

### Writing Effective Tests

**AAA Pattern**:
- **Arrange**: Set up test data and conditions
- **Act**: Execute the function/method being tested
- **Assert**: Verify the expected outcome

**Test Coverage**:
- **Happy Path**: Expected behavior with valid inputs
- **Edge Cases**: Boundary conditions and unusual inputs
- **Error Cases**: Invalid inputs and error conditions

**Example Test Structure**:
```typescript
describe('ComponentName', () => {
  describe('when rendered with default props', () => {
    test('should display correctly', () => {
      // Arrange
      const props = { /* default props */ };
      
      // Act
      render(<ComponentName {...props} />);
      
      // Assert
      expect(screen.getByTestId('component')).toBeInTheDocument();
    });
  });
  
  describe('when user interacts with it', () => {
    test('should handle click events', async () => {
      // Arrange
      const onClickMock = vi.fn();
      render(<ComponentName onClick={onClickMock} />);
      
      // Act
      await userEvent.click(screen.getByRole('button'));
      
      // Assert
      expect(onClickMock).toHaveBeenCalledTimes(1);
    });
  });
});
```

### Mock vs Dummy Implementation

**Prefer Dummy Implementations**:
```python
# Good: Dummy implementation
class DummyVectorStore(VectorStore):
    def add(self, vectors, ids, metadata=None):
        return True
    
    def search(self, query_vector, top_k=10):
        return [SearchResult(id="1", score=0.9, metadata={"test": "data"})]

# Avoid: Mock objects
def test_with_mock():
    with patch('src.vector_store.VectorStore') as mock:
        mock.return_value.search.return_value = [...]
        # Test logic
```

---

## Troubleshooting

### Common Issues

**Vitest Issues**:
```bash
# "Cannot find module" errors
rm -rf node_modules bun.lockb
bun install

# Cache issues
bun run test --run --no-cache
```

**Playwright Issues**:
```bash
# "Browser not found" errors
npx playwright install

# Timeout issues
npx playwright test --timeout=60000
```

**Pytest Issues**:
```bash
# Import errors in tests
poetry install --no-dev
poetry install

# Test discovery issues
poetry run pytest --collect-only
```

**Bruno Issues**:
```bash
# "bru: command not found"
npm install -g @usebruno/cli

# Connection refused during API tests
# Make sure server is running
cd packages/server && task server
```

### Debug Mode

**Enable Debug Logging**:
```bash
# Client
DEBUG=vitest:* bun run test

# Server
export PYTEST_DEBUG=1
poetry run pytest tests/unit -v -s
```

### Performance Issues

**Slow Tests**:
- Use dummy implementations instead of real services
- Optimize test data size
- Run tests in parallel where possible

**Memory Issues**:
- Clean up resources in test teardown
- Use pytest fixtures for proper setup/teardown
- Limit concurrent test execution

---

## Additional Resources

### Documentation
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react/)
- [Playwright Documentation](https://playwright.dev/)
- [Storybook Documentation](https://storybook.js.org/)
- [Bruno Documentation](https://docs.usebruno.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Testcontainers Documentation](https://testcontainers-python.readthedocs.io/)

### Tools and Extensions
- **VS Code Extensions**:
  - Vitest
  - Playwright Test for VSCode
  - Thunder Client (API testing)
  - Coverage Gutters

- **Browser Extensions**:
  - React Developer Tools
  - Redux DevTools

This comprehensive testing strategy ensures the reliability and maintainability of the InsightHub dual RAG system across all components and integration points.