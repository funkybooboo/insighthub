# Testing Guide

This guide documents all the testing tools and approaches used in the InsightHub project.

## Table of Contents

- [Quick Start](#quick-start)
- [Client Testing](#client-testing)
  - [Unit Tests (Vitest)](#unit-tests-vitest)
  - [E2E Tests (Playwright)](#e2e-tests-playwright)
  - [Component Stories (Storybook)](#component-stories-storybook)
- [Server Testing](#server-testing)
  - [Unit Tests (Pytest)](#unit-tests-pytest)
  - [API Tests (Bruno)](#api-tests-bruno)
- [Coverage Reports](#coverage-reports)

---

## Quick Start

### Run All Tests

```bash
# Client tests (from packages/client)
cd packages/client
task test              # Unit tests
task test:e2e          # E2E tests
task storybook         # Visual component testing

# Server tests (from packages/server)
cd packages/server
task test              # Unit tests
task test:api          # API tests (requires Bruno CLI)
```

---

## Client Testing

### Unit Tests (Vitest)

**Framework**: Vitest + React Testing Library

**What it tests**: Component logic, state management, utility functions

**Location**: `packages/client/src/**/*.test.tsx`

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
```

**Configuration**: `vitest.config.ts`

**Coverage Thresholds**:
- Lines: 80%
- Functions: 80%
- Branches: 80%
- Statements: 80%

**Current Stats**: 319 tests passing across 12 test files

**Example Test Files**:
- `src/components/auth/LoginForm.test.tsx`
- `src/components/chat/ChatSidebar.test.tsx`
- `src/store/slices/chatSlice.test.ts`

---

### E2E Tests (Playwright)

**Framework**: Playwright

**What it tests**: Full user workflows across the application

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

# Run in headed mode (see the browser)
task test:e2e:headed
# or: npx playwright test --headed

# Run specific test file
npx playwright test e2e/auth/signup.spec.ts

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
- User signup flow (`e2e/auth/signup.spec.ts`)
- User login flow (`e2e/auth/login.spec.ts`)
- Create new conversation (`e2e/chat/new-conversation.spec.ts`)

**Setup**:
```bash
# Install Playwright browsers (first time only)
npx playwright install
```

---

### Component Stories (Storybook)

**Framework**: Storybook

**What it tests**: Visual component documentation and manual testing

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
- Authentication Components:
  - `LoginForm.stories.tsx` - Login form states
  - `SignupForm.stories.tsx` - Signup form validation
  - `UserMenu.stories.tsx` - User menu variations
- Chat Components:
  - `ChatSidebar.stories.tsx` - Session management UI
  - `ChatInput.stories.tsx` - Message input states
  - `ChatMessages.stories.tsx` - Message display
- Upload Components:
  - `FileUpload.stories.tsx` - File upload states

**Addons Enabled**:
- Docs (auto-generated documentation)
- Interactions (test user interactions)
- Links (navigation between stories)
- Essentials (controls, actions, viewport)

---

## Server Testing

### Unit Tests (Pytest)

**Framework**: Pytest

**What it tests**: API endpoints, business logic, data models, LLM providers

**Location**: `packages/server/tests/**/*.py`

**Commands**:
```bash
cd packages/server

# Run all tests with coverage
task test
# or: poetry run pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# Run only unit tests (fast)
task test-unit
# or: poetry run pytest tests/unit/ -v

# Run only integration tests (requires Docker)
task test-integration
# or: poetry run pytest tests/integration/ -v -s

# Run tests in watch mode
task test-watch
# or: poetry run ptw tests/
```

**Configuration**: `pyproject.toml` (pytest section)

**Test Categories**:
- **Unit Tests** (`tests/unit/`):
  - `test_api.py` - API endpoint tests
  - `test_llm_providers.py` - LLM provider mocking
  - `test_rate_limiter.py` - Rate limiting logic
- **Integration Tests** (`tests/integration/`):
  - Uses testcontainers for database testing
  - Requires Docker to be running

**Coverage Reports**:
- Terminal output: Shows missing lines
- HTML report: `htmlcov/index.html`

---

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
├── environments/
│   └── local.bru           # Local environment config
├── Auth/                   # Authentication tests
│   ├── Signup_Success.bru
│   ├── Login_Success.bru
│   └── ...
├── Chat/                   # Chat API tests
│   ├── Send_Message_Success.bru
│   ├── Send_Message_Rate_Limit.bru
│   └── ...
├── Documents/              # File upload tests
│   ├── Upload_PDF_Success.bru
│   ├── Upload_File_Too_Large.bru
│   └── ...
└── System/                 # System health tests
    └── Health_Check.bru
```

**Test Scenarios**:
- ✅ User signup and login
- ✅ Authentication flows
- ✅ Document upload (PDF, TXT)
- ✅ File validation (size limits, types)
- ✅ Chat message sending
- ✅ Rate limiting
- ✅ Health checks

**GUI Alternative**:
You can also use the [Bruno desktop app](https://www.usebruno.com/) to:
- Run tests interactively
- View request/response details
- Debug API calls
- Edit test collections

---

## Coverage Reports

### Client Coverage

View coverage after running:
```bash
cd packages/client
task test:coverage
```

Reports generated:
- Terminal: Summary table
- HTML: `coverage/index.html` (open in browser)
- LCOV: `coverage/lcov.info` (for CI tools)

### Server Coverage

View coverage after running:
```bash
cd packages/server
task test
```

Reports generated:
- Terminal: Summary with missing lines
- HTML: `htmlcov/index.html` (open in browser)

---

## Best Practices

### When to Use Each Testing Approach

| Test Type | Use When | Examples |
|-----------|----------|----------|
| **Unit Tests** | Testing isolated component/function logic | Redux actions, utilities, form validation |
| **E2E Tests** | Testing complete user workflows | Signup → Login → Create Chat → Send Message |
| **Storybook** | Visual component documentation | Button states, form layouts, loading states |
| **API Tests** | Testing backend endpoints directly | Auth endpoints, file uploads, error handling |

### Writing New Tests

**Unit Tests**:
```typescript
// packages/client/src/components/MyComponent.test.tsx
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

test('should render correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
});
```

**E2E Tests**:
```typescript
// packages/client/e2e/my-flow.spec.ts
import { test, expect } from '@playwright/test';

test('should complete workflow', async ({ page }) => {
    await page.goto('/');
    await page.click('button');
    await expect(page).toHaveURL('/success');
});
```

**Storybook Stories**:
```typescript
// packages/client/src/components/MyComponent.stories.tsx
import type { Meta, StoryObj } from '@storybook/react-vite';
import MyComponent from './MyComponent';

const meta: Meta<typeof MyComponent> = {
    title: 'Components/MyComponent',
    component: MyComponent,
};

export default meta;
export const Default: StoryObj<typeof MyComponent> = {};
```

**Bruno API Tests**:
```bruno
# packages/server/bruno/MyEndpoint/Test_Case.bru
meta {
  name: Test Case Name
  type: http
}

get {
  url: {{base_url}}/api/endpoint
}

assert {
  res.status: eq 200
}
```

---

## Continuous Integration

All tests run automatically in CI:
- ✅ Client unit tests (`task test`)
- ✅ Client linting (`task lint`)
- ✅ Client type checking (TypeScript)
- ✅ Client build (`task build`)
- ✅ Server unit tests (`task test`)
- ✅ Server linting (`task lint`)
- ✅ Server type checking (`task type-check`)

E2E and API tests should be run manually or in separate CI jobs since they require running services.

---

## Troubleshooting

### Common Issues

**Vitest: "Cannot find module"**
```bash
# Clear cache and reinstall
rm -rf node_modules
bun install
```

**Playwright: "Browser not found"**
```bash
# Install browsers
npx playwright install
```

**Bruno: "bru: command not found"**
```bash
# Install Bruno CLI
npm install -g @usebruno/cli
```

**API tests failing: "Connection refused"**
```bash
# Make sure server is running
cd packages/server
task server
```

---

## Additional Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- [Storybook Documentation](https://storybook.js.org/)
- [Bruno Documentation](https://docs.usebruno.com/)
- [Pytest Documentation](https://docs.pytest.org/)
