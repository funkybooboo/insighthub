# Cypress Test Coverage for InsightHub

This document maps all user flows from `/docs/client-user-flows.md` to their corresponding Cypress tests.

## Test Coverage Summary

### 1. User Authentication

| User Flow                              | Test File               | Test Case                                                    | Status  |
| -------------------------------------- | ----------------------- | ------------------------------------------------------------ | ------- |
| User Login                             | 01-authentication.cy.ts | should successfully log in with valid credentials            | Covered |
| User Login - Invalid Credentials       | 01-authentication.cy.ts | should show error with invalid credentials                   | Covered |
| User Login - Validation                | 01-authentication.cy.ts | should show validation errors for empty fields               | Covered |
| User Login - Redirect if authenticated | 01-authentication.cy.ts | should redirect to main page if already logged in            | Covered |
| User Signup                            | 01-authentication.cy.ts | should successfully sign up with valid data                  | Covered |
| User Signup - Username exists          | 01-authentication.cy.ts | should show error when username already exists               | Covered |
| User Signup - Email exists             | 01-authentication.cy.ts | should show error when email already exists                  | Covered |
| User Signup - Password validation      | 01-authentication.cy.ts | should validate password strength                            | Covered |
| User Logout                            | 01-authentication.cy.ts | should successfully log out                                  | Covered |
| User Logout - Protected routes         | 01-authentication.cy.ts | should require login to access protected routes after logout | Covered |
| Get Current User Profile               | 01-authentication.cy.ts | should display user profile information                      | Covered |
| Get Current User Profile - Theme       | 01-authentication.cy.ts | should apply user theme preference                           | Covered |
| Update User Profile                    | 01-authentication.cy.ts | should successfully update profile information               | Covered |
| Update User Profile - Validation       | 01-authentication.cy.ts | should show error for invalid email format                   | Covered |
| Update User Preferences - Theme        | 01-authentication.cy.ts | should toggle theme preference                               | Covered |
| Change User Password                   | 01-authentication.cy.ts | should successfully change password                          | Covered |
| Change User Password - Invalid current | 01-authentication.cy.ts | should show error for incorrect current password             | Covered |
| Change User Password - Mismatch        | 01-authentication.cy.ts | should show error when passwords do not match                | Covered |

### 2. Default RAG Configuration Management

| User Flow                                 | Test File                     | Test Case                                        | Status  |
| ----------------------------------------- | ----------------------------- | ------------------------------------------------ | ------- |
| Fetch Default RAG Config                  | 05-settings-management.cy.ts  | should display current default RAG configuration | Covered |
| Fetch Default RAG Config - Initialization | 02-workspace-management.cy.ts | should pre-populate form with default RAG config | Covered |
| Save Default RAG Config - Vector          | 05-settings-management.cy.ts  | should update Vector RAG configuration           | Covered |
| Save Default RAG Config - Graph           | 05-settings-management.cy.ts  | should update Graph RAG configuration            | Covered |
| Save Default RAG Config - Validation      | 05-settings-management.cy.ts  | should validate RAG configuration values         | Covered |
| Save Default RAG Config - Usage           | 05-settings-management.cy.ts  | should use updated config for new workspaces     | Covered |

### 3. Workspace Management

| User Flow                                | Test File                     | Test Case                                                      | Status  |
| ---------------------------------------- | ----------------------------- | -------------------------------------------------------------- | ------- |
| List Workspaces                          | 02-workspace-management.cy.ts | should display list of workspaces                              | Covered |
| List Workspaces - Status badges          | 02-workspace-management.cy.ts | should show workspace status badges                            | Covered |
| Select Active Workspace                  | 02-workspace-management.cy.ts | should select and activate a workspace                         | Covered |
| Select Active Workspace - UI update      | 02-workspace-management.cy.ts | should update UI when switching workspaces                     | Covered |
| Create New Workspace - Default config    | 02-workspace-management.cy.ts | should successfully create a workspace with default RAG config | Covered |
| Create New Workspace - Custom config     | 02-workspace-management.cy.ts | should create workspace with custom RAG configuration          | Covered |
| Create New Workspace - Validation        | 02-workspace-management.cy.ts | should show validation errors for invalid workspace name       | Covered |
| Create New Workspace - Pre-populate      | 02-workspace-management.cy.ts | should pre-populate form with default RAG config               | Covered |
| View Workspace Details                   | 02-workspace-management.cy.ts | should display workspace details page                          | Covered |
| View Workspace Details - Stats           | 02-workspace-management.cy.ts | should show document and session counts                        | Covered |
| View Workspace Details - Status          | 02-workspace-management.cy.ts | should show workspace status with loading indicator            | Covered |
| Edit Workspace Details                   | 02-workspace-management.cy.ts | should successfully update workspace name and description      | Covered |
| Edit Workspace Details - RAG config lock | 02-workspace-management.cy.ts | should not allow editing RAG config after provisioning         | Covered |
| Edit Workspace Details - Validation      | 02-workspace-management.cy.ts | should show validation error for empty workspace name          | Covered |
| Delete Workspace                         | 02-workspace-management.cy.ts | should successfully delete a workspace                         | Covered |
| Delete Workspace - Confirmation          | 02-workspace-management.cy.ts | should show confirmation dialog before deleting                | Covered |
| Delete Workspace - Actions disabled      | 02-workspace-management.cy.ts | should disable all workspace actions during deletion           | Covered |
| Workspace Status Updates - Provisioning  | 02-workspace-management.cy.ts | should update workspace status from provisioning to ready      | Covered |

### 4. Chat Session Management

| User Flow                  | Test File                 | Test Case                            | Status  |
| -------------------------- | ------------------------- | ------------------------------------ | ------- |
| Create New Chat Session    | 04-chat-interaction.cy.ts | should create a new chat session     | Covered |
| Select Active Chat Session | 04-chat-interaction.cy.ts | should switch between chat sessions  | Covered |
| Delete Chat Session        | 04-chat-interaction.cy.ts | should delete a chat session         | Covered |
| List Chat Sessions         | 04-chat-interaction.cy.ts | should display list of chat sessions | Covered |

### 5. Document Management

| User Flow                                    | Test File                    | Test Case                                                  | Status  |
| -------------------------------------------- | ---------------------------- | ---------------------------------------------------------- | ------- |
| Upload Document                              | 03-document-management.cy.ts | should successfully upload a text document                 | Covered |
| Upload Document - Progress                   | 03-document-management.cy.ts | should show upload progress                                | Covered |
| Upload Document - Invalid type               | 03-document-management.cy.ts | should show error for unsupported file type                | Covered |
| Upload Document - Multiple files             | 03-document-management.cy.ts | should allow multiple file uploads                         | Covered |
| Upload Document - Disabled during processing | 03-document-management.cy.ts | should disable upload button while workspace is processing | Covered |
| Document Processing Status                   | 03-document-management.cy.ts | should show document status progression                    | Covered |
| Document Processing Status - Spinner         | 03-document-management.cy.ts | should show loading spinner during processing              | Covered |
| Document Processing Status - Real-time       | 03-document-management.cy.ts | should update status in real-time via WebSocket            | Covered |
| List Documents in Workspace                  | 03-document-management.cy.ts | should display all documents in the workspace              | Covered |
| List Documents in Workspace - Count          | 03-document-management.cy.ts | should show document count                                 | Covered |
| List Documents in Workspace - Refresh        | 03-document-management.cy.ts | should refresh document list when switching workspaces     | Covered |
| List Documents in Workspace - Empty state    | 03-document-management.cy.ts | should show empty state when no documents exist            | Covered |
| Delete Document                              | 03-document-management.cy.ts | should successfully delete a document                      | Covered |
| Delete Document - Confirmation               | 03-document-management.cy.ts | should show confirmation dialog before deleting            | Covered |
| Delete Document - Count update               | 03-document-management.cy.ts | should update document count after deletion                | Covered |
| Delete Document - Vector removal             | 03-document-management.cy.ts | should remove document vectors from RAG system             | Covered |
| Document Metadata Display                    | 03-document-management.cy.ts | should display document filename, upload date, and size    | Covered |

### 6. Chat Interaction

| User Flow                                | Test File                 | Test Case                                                     | Status  |
| ---------------------------------------- | ------------------------- | ------------------------------------------------------------- | ------- |
| Send Chat Message                        | 04-chat-interaction.cy.ts | should successfully send a message and receive response       | Covered |
| Send Chat Message - Input disabled       | 04-chat-interaction.cy.ts | should disable input while waiting for response               | Covered |
| Send Chat Message - Streaming            | 04-chat-interaction.cy.ts | should stream bot response token by token                     | Covered |
| Send Chat Message - Enter key            | 04-chat-interaction.cy.ts | should handle Enter key to send message                       | Covered |
| Send Chat Message - Multiline            | 04-chat-interaction.cy.ts | should handle Shift+Enter for multiline input                 | Covered |
| Send Chat Message - Empty prevention     | 04-chat-interaction.cy.ts | should prevent sending empty messages                         | Covered |
| Cancel Chat Message Streaming - Button   | 04-chat-interaction.cy.ts | should cancel streaming response when cancel button clicked   | Covered |
| Cancel Chat Message Streaming - Keyboard | 04-chat-interaction.cy.ts | should handle Ctrl+C to cancel streaming                      | Covered |
| RAG Context Display                      | 04-chat-interaction.cy.ts | should display retrieved context with the response            | Covered |
| RAG Context Display - Scores             | 04-chat-interaction.cy.ts | should show relevance scores for retrieved chunks             | Covered |
| RAG Context Display - Expand/Collapse    | 04-chat-interaction.cy.ts | should expand and collapse context display                    | Covered |
| RAG Enhancement Prompt - No context      | 04-chat-interaction.cy.ts | should show enhancement prompt when no context found          | Covered |
| RAG Enhancement Prompt - Upload          | 04-chat-interaction.cy.ts | should allow document upload from enhancement prompt          | Covered |
| RAG Enhancement Prompt - Wikipedia       | 04-chat-interaction.cy.ts | should trigger Wikipedia fetch from enhancement prompt        | Covered |
| RAG Enhancement Prompt - Continue        | 04-chat-interaction.cy.ts | should continue without context when requested                | Covered |
| Chat Message Display - User              | 04-chat-interaction.cy.ts | should display user messages with correct styling             | Covered |
| Chat Message Display - Bot               | 04-chat-interaction.cy.ts | should display bot messages with correct styling              | Covered |
| Chat Message Display - Markdown          | 04-chat-interaction.cy.ts | should render markdown in bot responses                       | Covered |
| Chat Message Display - Timestamps        | 04-chat-interaction.cy.ts | should show timestamps for messages                           | Covered |
| Chat Message Display - Auto-scroll       | 04-chat-interaction.cy.ts | should auto-scroll to latest message                          | Covered |
| Multi-turn Conversations                 | 04-chat-interaction.cy.ts | should maintain conversation context across multiple messages | Covered |
| Chat with Vector RAG                     | 04-chat-interaction.cy.ts | should work with Vector RAG                                   | Covered |
| Chat with Graph RAG                      | 04-chat-interaction.cy.ts | should work with Graph RAG when configured                    | Covered |

### 7. Real-time Status Updates (WebSocket)

| User Flow                      | Test File                     | Test Case                                                 | Status  |
| ------------------------------ | ----------------------------- | --------------------------------------------------------- | ------- |
| Document Status Updates        | 03-document-management.cy.ts  | should update status in real-time via WebSocket           | Covered |
| Workspace Status Updates       | 02-workspace-management.cy.ts | should update workspace status from provisioning to ready | Covered |
| Chat Streaming Events          | 04-chat-interaction.cy.ts     | should stream bot response token by token                 | Covered |
| Wikipedia Fetch Status Updates | 04-chat-interaction.cy.ts     | should trigger Wikipedia fetch from enhancement prompt    | Covered |

## Coverage Statistics

- **Total User Flows**: 70+
- **Flows with Tests**: 70+
- **Coverage Percentage**: 100%

## Test Files Summary

| Test File                     | Number of Tests | Focus Area                                      |
| ----------------------------- | --------------- | ----------------------------------------------- |
| 01-authentication.cy.ts       | 18              | User authentication, profile, and preferences   |
| 02-workspace-management.cy.ts | 21              | Workspace CRUD operations and RAG configuration |
| 03-document-management.cy.ts  | 20              | Document upload, processing, and management     |
| 04-chat-interaction.cy.ts     | 26              | Chat interactions, streaming, RAG enhancement   |
| 05-settings-management.cy.ts  | 20              | Settings, preferences, and configuration        |

**Total Test Cases**: 105+

## Additional Test Categories

### Error Handling

- Authentication failures
- Network errors
- Validation errors
- Processing failures
- API failures

### Edge Cases

- Empty states
- Maximum file size
- Long messages
- Multiple concurrent operations
- Session persistence

### Accessibility

- Keyboard navigation
- ARIA labels
- Screen reader support
- Focus management

### Real-time Features

- WebSocket connections
- Status updates
- Chat streaming
- Document processing

## Running Specific Test Suites

```bash
# Run only authentication tests
bun run cypress --spec "cypress/e2e/01-authentication.cy.ts"

# Run only workspace tests
bun run cypress --spec "cypress/e2e/02-workspace-management.cy.ts"

# Run only document tests
bun run cypress --spec "cypress/e2e/03-document-management.cy.ts"

# Run only chats tests
bun run cypress --spec "cypress/e2e/04-chat-interaction.cy.ts"

# Run only settings tests
bun run cypress --spec "cypress/e2e/05-settings-management.cy.ts"
```

## Notes

1. All tests follow the user flows documented in `/docs/client-user-flows.md`
2. Tests use real backend services (not mocks) for integration testing
3. Custom commands provide reusable test utilities
4. Fixtures provide consistent test data
5. Tests handle asynchronous operations properly with appropriate timeouts
6. Real-time WebSocket updates are verified throughout the test suite

## Future Enhancements

- Add visual regression testing with Percy or Chromatic
- Add accessibility testing with axe-core
- Add performance testing with Lighthouse CI
- Add API contract testing
- Add mobile viewport testing
- Add cross-browser testing matrix
