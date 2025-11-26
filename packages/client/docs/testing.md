# Testing Documentation

## Overview

The InsightHub client uses a comprehensive testing strategy combining unit tests, integration tests, and visual regression testing through Storybook.

## Testing Stack

- **Test Runner**: Vitest
- **Testing Library**: React Testing Library
- **Mocking**: MSW (Mock Service Worker) for API mocking
- **Visual Testing**: Storybook
- **Coverage**: Vitest Coverage (v8)

## Running Tests

### Using Taskfile (Recommended)

```bash
# Run all tests once
task test

# Run tests in watch mode
task test:watch

# Run tests with coverage report
task test:coverage

# Run tests with UI
task test:ui

# Run Storybook for visual testing
task storybook
```

### Using Bun directly

```bash
# Run all tests
bun run test:run

# Watch mode
bun run test

# Coverage
bun run test:coverage

# UI mode
bun run test:ui
```

## Test Organization

```
packages/client/
--- src/
|   --- components/
|   |   --- auth/
|   |   |   --- LoginForm.tsx
|   |   |   --- LoginForm.test.tsx         # Component tests
|   |   |   --- LoginForm.stories.tsx      # Storybook stories
|   |   --- workspace/
|   |   |   --- WorkspaceSelector.tsx
|   |   |   --- WorkspaceSelector.test.tsx
|   |   |   --- WorkspaceSelector.stories.tsx
|   --- store/
|   |   --- slices/
|   |       --- authSlice.ts
|   |       --- authSlice.test.ts          # Redux tests
|   --- services/
|   |   --- api.ts
|   |   --- api.test.ts                    # API service tests
|   --- lib/
|       --- validation.ts
|       --- validation.test.ts             # Utility tests
```

## Writing Tests

### Component Tests

Use React Testing Library for component tests. Focus on user interactions and behavior, not implementation details.

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/users-event';
import { Provider } from 'react-redux';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
    it('should render correctly', () => {
        render(
            <Provider store={store}>
                <MyComponent />
            </Provider>
        );

        expect(screen.getByText('Hello')).toBeInTheDocument();
    });

    it('should handle users interactions', async () => {
        render(<MyComponent />);

        const button = screen.getByRole('button');
        await userEvent.click(button);

        await waitFor(() => {
            expect(screen.getByText('Clicked')).toBeInTheDocument();
        });
    });
});
```

### Redux Slice Tests

Test reducers and actions in isolation:

```typescript
import { describe, it, expect } from 'vitest';
import reducer, { increment, decrement } from './counterSlice';

describe('counterSlice', () => {
    it('should handle initial state', () => {
        expect(reducer(undefined, { type: 'unknown' })).toEqual({
            value: 0,
        });
    });

    it('should handle increment', () => {
        const actual = reducer({ value: 0 }, increment());
        expect(actual.value).toBe(1);
    });
});
```

### API Service Tests

Use MSW to mock HTTP requests:

```typescript
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { apiService } from './api';

const server = setupServer(
    http.get('/api/data', () => {
        return HttpResponse.json({ data: 'test' });
    })
);

beforeAll(() => server.listen());
afterAll(() => server.close());
afterEach(() => server.resetHandlers());

describe('API Service', () => {
    it('should fetch data', async () => {
        const data = await apiService.getData();
        expect(data).toEqual({ data: 'test' });
    });

    it('should handle errors', async () => {
        server.use(
            http.get('/api/data', () => {
                return new HttpResponse(null, { status: 500 });
            })
        );

        await expect(apiService.getData()).rejects.toThrow();
    });
});
```

### Validation Utility Tests

Test pure functions with various inputs:

```typescript
import { describe, it, expect } from 'vitest';
import { validateEmail } from './validation';

describe('validateEmail', () => {
    it('should accept valid emails', () => {
        expect(validateEmail('test@example.com').valid).toBe(true);
    });

    it('should reject invalid emails', () => {
        const result = validateEmail('invalid');
        expect(result.valid).toBe(false);
        expect(result.error).toBe('Invalid email format');
    });
});
```

## Storybook Stories

Create stories for all components to enable visual testing and documentation:

```typescript
import type { Meta, StoryObj } from '@storybook/react';
import MyComponent from './MyComponent';

const meta: Meta<typeof MyComponent> = {
    title: 'Components/MyComponent',
    component: MyComponent,
    parameters: {
        layout: 'centered',
    },
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    args: {
        text: 'Hello World',
    },
};

export const Loading: Story = {
    args: {
        text: 'Hello World',
        isLoading: true,
    },
};
```

## Test Coverage

### Current Coverage

Run `task test:coverage` to generate a coverage report.

Coverage goals:

- **Statements**: > 80%
- **Branches**: > 75%
- **Functions**: > 80%
- **Lines**: > 80%

### Coverage Reports

Coverage reports are generated in:

- `coverage/` directory (HTML report)
- Console output (summary)

View HTML report:

```bash
task test:coverage
open coverage/index.html
```

## Best Practices

### DO

1. **Test user behavior**, not implementation details
2. **Use semantic queries** (`getByRole`, `getByLabelText`, etc.)
3. **Test accessibility** by using ARIA roles and labels
4. **Mock external dependencies** (API calls, localStorage)
5. **Clean up after tests** (clear localStorage, reset mocks)
6. **Use meaningful test descriptions** that explain what is being tested
7. **Test error states** and edge cases
8. **Keep tests isolated** - each test should run independently

### DON'T

1. **Don't test implementation details** (internal state, private methods)
2. **Don't query by class names or element types** - use semantic queries
3. **Don't test third-party libraries** - assume they work
4. **Don't make tests depend on each other** - each test should be independent
5. **Don't skip cleanup** - always clear state between tests
6. **Don't test trivial code** - focus on complex logic and user interactions

## Common Testing Patterns

### Testing Forms

```typescript
it('should submit form with valid data', async () => {
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await userEvent.type(emailInput, 'test@example.com');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(submitButton);

    await waitFor(() => {
        expect(screen.getByText(/success/i)).toBeInTheDocument();
    });
});
```

### Testing Async Operations

```typescript
it('should load data on mount', async () => {
    vi.mocked(apiService.getData).mockResolvedValue({ data: 'test' });

    render(<DataComponent />);

    // Initially shows loading
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Wait for data to load
    await waitFor(() => {
        expect(screen.getByText('test')).toBeInTheDocument();
    });
});
```

### Testing Redux Connected Components

```typescript
function createTestStore(preloadedState = {}) {
    return configureStore({
        reducer: {
            auth: authReducer,
        },
        preloadedState,
    });
}

it('should display users info from Redux', () => {
    const store = createTestStore({
        auth: {
            user: { username: 'testuser' },
            isAuthenticated: true,
        },
    });

    render(
        <Provider store={store}>
            <UserMenu />
        </Provider>
    );

    expect(screen.getByText('testuser')).toBeInTheDocument();
});
```

### Testing Error States

```typescript
it('should display error message on failure', async () => {
    vi.mocked(apiService.getData).mockRejectedValue(
        new Error('Failed to fetch')
    );

    render(<DataComponent />);

    await waitFor(() => {
        expect(screen.getByText(/failed to fetch/i)).toBeInTheDocument();
    });
});
```

## Debugging Tests

### Run specific test file

```bash
bun run test src/components/auth/LoginForm.test.tsx
```

### Run specific test

```bash
bun run test -t "should submit form"
```

### Debug with UI

```bash
task test:ui
```

### Add debug output

```typescript
import { screen } from '@testing-library/react';

it('debugging test', () => {
    render(<MyComponent />);

    // Print DOM tree
    screen.debug();

    // Print specific element
    screen.debug(screen.getByRole('button'));
});
```

## Continuous Integration

Tests run automatically on:

- Every push to remote
- Every pull request
- Before deployment

See `.github/workflows/client-ci.yml` for CI configuration.

## Troubleshooting

### Tests timeout

Increase timeout in vitest.config.ts:

```typescript
export default defineConfig({
    test: {
        testTimeout: 10000, // 10 seconds
    },
});
```

### Act warnings

Wrap state updates in `waitFor`:

```typescript
await waitFor(() => {
    expect(screen.getByText('Updated')).toBeInTheDocument();
});
```

### localStorage issues

Clear localStorage in beforeEach:

```typescript
beforeEach(() => {
    localStorage.clear();
});
```

### Mock not working

Ensure mocks are set up before tests run:

```typescript
vi.mock('./api', () => ({
    apiService: {
        getData: vi.fn(),
    },
}));
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [MSW Documentation](https://mswjs.io/)
- [Storybook Documentation](https://storybook.js.org/)
