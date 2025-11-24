# InsightHub Client

React frontend for the InsightHub dual RAG system, providing a modern interface for querying academic papers and documents with real-time chat capabilities.

## Features

### User Experience

- **Workspace Management**: Create and manage isolated workspaces with custom RAG configurations
- **Real-time Chat**: WebSocket-based streaming responses with token-by-token display
- **Document Management**: Upload and manage PDF/text documents with real-time processing status
- **Conversation Memory**: Persistent chat sessions with full context preservation
- **User Authentication**: Secure JWT-based login/signup with profile management
- **Theme Support**: Light/dark mode with persistent user preferences
- **Responsive Design**: Mobile-friendly interface optimized for all screen sizes

### RAG Integration

- **Dual RAG Support**: Interface for both Vector RAG and Graph RAG systems
- **Intelligent Enhancement**: Automatic prompts for context improvement (upload documents, fetch Wikipedia)
- **Real-time Status**: Live updates on document processing and workspace provisioning
- **Source Attribution**: Display of source documents/chunks used in RAG responses
- **Chat Locking**: Intelligent UI locking during processing operations

### Development Features

- **TypeScript**: Full type safety throughout the application
- **Component Testing**: Comprehensive unit and integration tests
- **Storybook**: Interactive component documentation
- **Hot Reload**: Fast development with Vite HMR
- **Code Quality**: ESLint, Prettier, and automated formatting

## Tech Stack

### Core Framework

- **React 19** with TypeScript for modern component development
- **Vite** for fast development and optimized builds
- **TailwindCSS** for utility-first styling

### State Management

- **Redux Toolkit** for global application state
- **React Query** for server state management and caching
- **Local Storage** for client-side data persistence

### Communication

- **Socket.IO Client** for real-time WebSocket communication
- **Axios** for REST API calls with interceptors

### Development & Testing

- **Vitest** for fast unit testing
- **React Testing Library** for component testing
- **MSW (Mock Service Worker)** for API mocking
- **Storybook** for component development and documentation
- **Playwright** for end-to-end testing

## Development Setup

### Prerequisites

- Node.js 18+ or Bun runtime
- Backend server running (see `packages/server/`)

### Installation

```bash
cd packages/client

# Install dependencies
bun install

# Start development server
bun run dev
```

The development server will start at `http://localhost:5173`.

### Available Scripts

We use **Taskfile** for task automation (requires Task CLI):

```bash
# Development
task dev             # Start Vite dev server with HMR
task build           # Build for production
task preview         # Preview production build locally

# Code Quality
task lint            # Run ESLint
task format          # Format code with Prettier
task format-check    # Check formatting without fixing
task check           # Run all checks (format, lint, test, build)

# Testing
task test            # Run all unit tests
task test:watch      # Run tests in watch mode
task test:coverage   # Run tests with coverage report
task test:ui         # Run tests with Vitest UI

# Component Documentation
task storybook       # Run Storybook dev server
task storybook:build # Build Storybook for production

# Security
task audit           # Audit dependencies for vulnerabilities
task scan            # Run Trivy security scan
task security        # Run all security checks

# Cleanup
task clean           # Remove generated files and node_modules
```

You can also use Bun directly:

```bash
bun run dev          # Development server
bun run build        # Production build
bun run test:run     # Run tests
# etc.
```

## Project Structure

```
packages/client/
- src/
|   - components/              # React components
|   |   - auth/              # Authentication components
|   |   |   - LoginForm.tsx
|   |   |   - SignupForm.tsx
|   |   |   - UserMenu.tsx
|   |   - chat/              # Chat interface components
|   |   |   - ChatBot.tsx           # Main chat component
|   |   |   - ChatInput.tsx         # Message input component
|   |   |   - ChatMessages.tsx      # Message display component
|   |   |   - ChatSidebar.tsx       # Chat session sidebar
|   |   |   - MarkdownRenderer.tsx  # Markdown rendering
|   |   |   - TypingIndicator.tsx   # Loading animation
|   |   - settings/          # Settings components
|   |   |   - ProfileSettings.tsx
|   |   |   - RagConfigSettings.tsx
|   |   |   - ThemePreferences.tsx
|   |   |   - PasswordChangeForm.tsx
|   |   - upload/            # Document upload components
|   |   |   - FileUpload.tsx
|   |   |   - DocumentList.tsx
|   |   |   - DocumentManager.tsx
|   |   - workspace/         # Workspace management
|   |   |   - WorkspaceSelector.tsx
|   |   |   - WorkspaceSettings.tsx
|   |   - ui/                # Reusable UI components
|   |       - ThemeToggle.tsx
|   |       - Button.tsx
|   |       - StatusBadge.tsx
|   - pages/                 # Page-level components
|   |   - WorkspacesPage.tsx
|   |   - WorkspaceDetailPage.tsx
|   |   - SettingsPage.tsx
|   - services/              # API and external services
|   |   - api.ts             # REST API client
|   |   - socket.ts          # WebSocket/Socket.IO client
|   - store/                 # Redux state management
|   |   - slices/            # Redux slices
|   |   |   - authSlice.ts
|   |   |   - chatSlice.ts
|   |   |   - workspaceSlice.ts
|   |   |   - themeSlice.ts
|   |   - index.ts           # Store configuration
|   - types/                 # TypeScript type definitions
|   |   - chat.ts            # Chat-related types
|   |   - workspace.ts       # Workspace-related types
|   |   - api.ts             # API response types
|   - lib/                   # Utilities and helpers
|   |   - utils.ts           # General utilities
|   |   - chatStorage.ts     # Local storage helpers
|   |   - validation.ts      # Input validation
|   - hooks/                 # Custom React hooks
|   |   - useStatusUpdates.ts # WebSocket status hook
|   - test/                  # Test setup and utilities
|   |   - setup.ts           # Vitest configuration
|   |   - global-setup.ts    # Global test setup
|   - App.tsx                # Main application component
|   - main.tsx               # Application entry point
|   - vite-env.d.ts          # Vite type definitions
- public/                    # Static assets
- .storybook/                # Storybook configuration
- docs/                      # Component documentation
- index.html                 # HTML template
- package.json               # Dependencies and scripts
- Taskfile.yml               # Task automation
- vite.config.ts             # Vite configuration
- vitest.config.ts           # Vitest configuration
- tsconfig.json              # TypeScript configuration
```

## Key Components

### ChatBot Component

The main chat interface that handles:

- Real-time message streaming via Socket.IO
- Conversation session management
- Typing indicators and sound notifications
- Error handling and connection management
- RAG context display with source attribution

### Socket Service

Manages WebSocket connections for real-time features:

- Connection lifecycle (connect/disconnect)
- Event handling (chunks, completions, errors)
- Message sending with session context
- Automatic reconnection logic

### Document Management

Components for uploading and managing documents:

- File upload with drag-and-drop support
- Document listing with real-time status updates
- Progress indicators and error handling
- Document deletion with confirmation

### Workspace Management

Workspace creation and management:

- Workspace creation with RAG configuration
- Real-time provisioning status updates
- Workspace switching and selection
- Workspace settings and deletion

## State Management

### Redux Store Structure

```typescript
interface RootState {
    auth: AuthState; // User authentication and profile
    chat: ChatState; // Chat sessions and messages
    workspace: WorkspaceState; // Workspaces and active workspace
    theme: ThemeState; // UI theme preferences
}
```

### Key Slices

**Auth Slice**: User authentication state

- Login/logout status
- User profile information
- JWT token management
- Default RAG configuration

**Chat Slice**: Chat messages and sessions

- Active chat session
- Message history
- Streaming status
- Enhancement prompt visibility

**Workspace Slice**: Workspace management

- List of workspaces
- Active workspace ID
- Workspace status updates
- RAG configuration

## API Integration

### REST API Endpoints

The client communicates with the following backend endpoints:

- **Authentication**: `/api/auth/*` - Login, signup, profile management
- **Workspaces**: `/api/workspaces/*` - Workspace CRUD operations
- **Documents**: `/api/workspaces/{id}/documents/*` - Document management
- **Chat**: `/api/workspaces/{id}/chat/*` - Chat session management

### WebSocket Events

Real-time communication via Socket.IO:

**Client to Server**:

- `chat_message`: Send user message
- `cancel_message`: Cancel streaming response

**Server to Client**:

- `chat_chunk`: Streaming response token
- `chat_complete`: Response completion
- `document_status`: Document processing updates
- `workspace_status`: Workspace provisioning updates
- `wikipedia_fetch_status`: Wikipedia fetch progress

## Development Guidelines

### Code Style

- **TypeScript**: Strict type checking enabled
- **ESLint**: React and TypeScript rules
- **Prettier**: Consistent code formatting
- **Component Naming**: PascalCase for components, camelCase for utilities

### Component Patterns

- **Functional Components**: Preferred over class components
- **Custom Hooks**: For reusable logic and state management
- **Props Interface**: Define types for all component props
- **Error Boundaries**: For error handling in component trees

### State Management

- **Local State**: `useState` for component-specific state
- **Global State**: Redux for app-wide state
- **Server State**: React Query for API data caching
- **Form State**: Formik or controlled components

### Testing Strategy

- **Unit Tests**: Test components and utilities in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test critical user flows
- **Mock Services**: Use MSW for API mocking

## Building for Production

```bash
# Build application for production
bun run build

# Preview production build locally
bun run preview

# Build artifacts are stored in the `dist/` directory
```

### Production Optimizations

- Code splitting and lazy loading
- Tree shaking for unused code elimination
- Asset optimization and compression
- Service worker for caching (future)

## Environment Variables

Create a `.env.local` file for local development:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:5000
VITE_SOCKET_URL=http://localhost:5000

# Feature Flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_SOUND_NOTIFICATIONS=true

# Application Settings
VITE_APP_NAME=InsightHub
VITE_APP_VERSION=1.0.0
```

## Testing

### Test Commands

```bash
# Unit Tests (Vitest)
task test                  # Run all unit tests
task test:watch            # Watch mode for development
task test:coverage         # Generate coverage report
task test:ui               # Interactive test UI

# E2E Tests (Playwright)
task test:e2e              # Run E2E tests
task test:e2e:ui           # Interactive UI mode
task test:e2e:headed       # Run with visible browser

# Component Documentation
task storybook             # Run Storybook dev server
task storybook:build       # Build static Storybook
```

### Test Coverage

**Current Stats**: 438 tests passing across 17 test files

**Coverage Areas**:

- Component tests: 200+ tests
- Redux slice tests: 100+ tests
- Service/utility tests: 100+ tests
- Storybook stories: 50+ stories

**Coverage Thresholds**:

- Lines: > 80%
- Functions: > 80%
- Branches: > 75%
- Statements: > 80%

## Docker Integration

The client is containerized and can be run via Docker Compose:

```bash
# From project root
docker compose up client-dev  # Development with hot reload
docker compose up client      # Production build
```

### Docker Features

- Multi-stage builds for optimization
- Hot reload in development
- Nginx serving for production
- Health checks and graceful shutdown

## Contributing

1. Follow existing code style and patterns
2. Add TypeScript types for new features
3. Update component documentation
4. Test changes in both development and production modes
5. Ensure responsive design works on mobile devices
6. Add tests for new components and features

## Troubleshooting

### Common Issues

```bash
# Hot reload not working
task restart-dev

# Type errors after dependency update
bun install --force

# Test failures
task test:ui  # Run tests interactively

# Build failures
task clean && bun install && task build
```

### Performance Tips

- Use React.memo for expensive components
- Implement virtual scrolling for long lists
- Optimize bundle size with code splitting
- Use Web Workers for heavy computations
