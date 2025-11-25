# Cypress E2E Tests for InsightHub

This directory contains end-to-end tests for the InsightHub client application using Cypress.

## Directory Structure

```
cypress/
+-- e2e/                           # E2E test specifications
|   +-- 01-authentication.cy.ts    # User authentication tests
|   +-- 02-workspace-management.cy.ts # Workspace CRUD and management tests
|   +-- 03-document-management.cy.ts  # Document upload and processing tests
|   +-- 04-chat-interaction.cy.ts     # Chat and RAG interaction tests
|   +-- 05-settings-management.cy.ts  # Settings and preferences tests
+-- fixtures/                      # Test data and mock files
|   +-- users.json                # User credentials for testing
|   +-- workspaces.json           # Workspace configurations
|   +-- test-document.txt         # Sample document for upload tests
+-- support/                       # Cypress support files
|   +-- commands.ts               # Custom Cypress commands
|   +-- e2e.ts                    # E2E configuration and setup
```

## Running Tests

### Prerequisites

1. Ensure the backend server is running:

    ```bash
    cd packages/server
    poetry run python -m src.api
    ```

2. Ensure all required services are running (Ollama, Qdrant, PostgreSQL):
    ```bash
    docker compose up
    ```

### Run Tests Interactively

Open Cypress Test Runner:

```bash
cd packages/client
bun run cypress
```

This opens the Cypress UI where you can:

- Select which tests to run
- See real-time test execution
- Debug failing tests
- Take screenshots and videos

### Run Tests in Headless Mode

Run all tests in headless mode:

```bash
bun run cypress:headless
```

Run tests in specific browsers:

```bash
bun run cypress:chrome
bun run cypress:firefox
bun run cypress:edge
```

### Run Tests with Auto-Start Dev Server

Automatically start the dev server and run tests:

```bash
bun run e2e              # Opens Cypress UI
bun run e2e:headless     # Runs tests in headless mode
```

## Test Structure

### Test Files

Tests are organized by feature area and numbered for execution order:

1. **01-authentication.cy.ts** - Authentication flows
    - User login
    - User signup
    - User logout
    - Profile management
    - Password change
    - Theme preferences

2. **02-workspace-management.cy.ts** - Workspace operations
    - List workspaces
    - Create workspace
    - Edit workspace
    - Delete workspace
    - Select active workspace
    - Default RAG configuration

3. **03-document-management.cy.ts** - Document operations
    - Upload documents
    - List documents
    - Delete documents
    - Document processing status
    - Real-time status updates

4. **04-chat-interaction.cy.ts** - Chat functionality
    - Send chat messages
    - Stream responses
    - Cancel streaming
    - Chat session management
    - RAG enhancement prompt
    - Context display

5. **05-settings-management.cy.ts** - Settings and preferences
    - Profile settings
    - Theme preferences
    - Default RAG configuration
    - Password change
    - Settings persistence

### Custom Commands

Custom Cypress commands are defined in `cypress/support/commands.ts`:

```typescript
// Authentication
cy.login(username, password);
cy.logout();
cy.signup(username, email, password, fullName);

// Workspace
cy.createWorkspace(name, description, ragConfig);
cy.selectWorkspace(workspaceName);

// Documents
cy.uploadDocument(filePath, workspaceId);

// Chat
cy.sendChatMessage(message);

// Status polling
cy.waitForDocumentStatus(documentId, status, timeout);
cy.waitForWorkspaceStatus(workspaceId, status, timeout);

// Utilities
cy.clearLocalStorage();
```

## Test Configuration

Configuration is defined in `cypress.config.ts`:

```typescript
{
  baseUrl: 'http://localhost:5173',
  viewportWidth: 1280,
  viewportHeight: 720,
  defaultCommandTimeout: 10000,
  requestTimeout: 10000,
  responseTimeout: 10000,
  env: {
    apiUrl: 'http://localhost:8000/api',
    testUsername: 'testuser',
    testPassword: 'TestPassword123!',
    testEmail: 'testuser@example.com'
  },
  retries: {
    runMode: 2,  // Retry failed tests twice in CI
    openMode: 0  // No retries in interactive mode
  }
}
```

### Environment Variables

You can override environment variables in several ways:

1. In `cypress.config.ts`:

    ```typescript
    env: {
        apiUrl: 'http://localhost:8000/api';
    }
    ```

2. Via command line:

    ```bash
    cypress run --env apiUrl=http://localhost:8000/api
    ```

3. Via `cypress.env.json` (not checked into git):
    ```json
    {
        "testUsername": "customuser",
        "testPassword": "CustomPassword123!"
    }
    ```

## Test Data

### Fixtures

Test data is stored in `cypress/fixtures/`:

- **users.json** - User credentials for testing
- **workspaces.json** - Workspace configurations for different RAG types
- **test-document.txt** - Sample document for upload testing

Access fixtures in tests:

```typescript
cy.fixture('users').then((users) => {
    cy.login(users.testUser.username, users.testUser.password);
});
```

## Best Practices

### 1. Use data-testid Attributes

Add `data-testid` attributes to UI elements for reliable selection:

```tsx
<button data-testid="login-button">Login</button>
```

Access in tests:

```typescript
cy.get('[data-testid="login-button"]').click();
```

### 2. Use Testing Library Queries

Prefer Testing Library queries for accessibility:

```typescript
cy.findByRole('button', { name: /login/i }).click();
cy.findByLabelText(/username/i).type('testuser');
```

### 3. Wait for Assertions

Use assertions instead of arbitrary waits:

```typescript
// Bad
cy.wait(5000);

// Good
cy.contains('Workspace created').should('be.visible');
cy.get('[data-testid="status-badge"]').should('contain.text', 'ready');
```

### 4. Clean Up Test Data

Always clean up test data between tests:

```typescript
beforeEach(() => {
    cy.clearLocalStorage();
    cy.login();
});
```

### 5. Handle Asynchronous Operations

Use custom commands for operations that take time:

```typescript
// Wait for document processing
cy.waitForDocumentStatus(documentId, 'ready', 120000);

// Wait for workspace provisioning
cy.waitForWorkspaceStatus(workspaceId, 'ready', 60000);
```

## Debugging Tests

### Interactive Debugging

1. Use `.debug()` to pause execution:

    ```typescript
    cy.get('[data-testid="chat-messages"]').debug();
    ```

2. Use `.pause()` to pause and step through:

    ```typescript
    cy.pause();
    cy.get('[data-testid="chat-input"]').type('test');
    ```

3. View console logs:
    - Open browser DevTools during test execution
    - Check console for application logs

### Screenshots and Videos

Cypress automatically captures:

- Screenshots on test failure (saved to `cypress/screenshots/`)
- Videos of test runs in headless mode (saved to `cypress/videos/`)

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
    e2e:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v3

            - name: Setup Bun
              uses: oven-sh/setup-bun@v1

            - name: Install dependencies
              run: bun install
              working-directory: packages/client

            - name: Start services
              run: docker compose up -d

            - name: Run E2E tests
              run: bun run e2e:headless
              working-directory: packages/client

            - name: Upload screenshots
              if: failure()
              uses: actions/upload-artifact@v3
              with:
                  name: cypress-screenshots
                  path: packages/client/cypress/screenshots

            - name: Upload videos
              if: always()
              uses: actions/upload-artifact@v3
              with:
                  name: cypress-videos
                  path: packages/client/cypress/videos
```

## Troubleshooting

### Tests Fail Due to Timeouts

Increase timeout values in `cypress.config.ts`:

```typescript
{
  defaultCommandTimeout: 15000,
  requestTimeout: 15000,
  responseTimeout: 15000
}
```

Or in specific tests:

```typescript
cy.get('[data-testid="bot-message"]', { timeout: 60000 }).should('exist');
```

### WebSocket Connection Issues

Ensure the backend server is running and WebSocket connections are allowed:

1. Check that the API server is running on `http://localhost:8000`
2. Verify WebSocket endpoint is accessible
3. Check browser console for connection errors

### Document Processing Stuck

If documents get stuck in processing status:

1. Check that all worker services are running (parser, chunker, embedder, indexer)
2. Verify Qdrant is accessible
3. Check worker logs for errors
4. Increase timeout values in tests

### Authentication Failures

If login tests fail:

1. Verify test user exists in the database
2. Check that credentials in `fixtures/users.json` match database
3. Ensure JWT token is being stored correctly
4. Check for CORS issues

## Coverage

These E2E tests cover all major user flows documented in `/home/nate/projects/insighthub/docs/client-user-flows.md`:

- User Authentication (Login, Signup, Logout, Profile, Preferences)
- Workspace Management (CRUD operations, RAG configuration)
- Document Management (Upload, Processing, Status updates)
- Chat Interaction (Messaging, Streaming, RAG enhancement)
- Settings Management (Profile, Theme, RAG defaults, Password)

## Contributing

When adding new features to the client:

1. Add corresponding E2E tests to the appropriate test file
2. Update custom commands if new reusable actions are needed
3. Add fixtures for new test data
4. Update this README with any new testing patterns
5. Ensure tests follow the existing structure and best practices

## Additional Resources

- [Cypress Documentation](https://docs.cypress.io/)
- [Testing Library Cypress](https://testing-library.com/docs/cypress-testing-library/intro/)
- [Cypress Best Practices](https://docs.cypress.io/guides/references/best-practices)
- [InsightHub User Flows](../../docs/client-user-flows.md)
