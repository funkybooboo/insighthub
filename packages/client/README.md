# InsightHub Client

React frontend for the InsightHub RAG system, providing a modern chatbot interface for querying academic papers and Wikipedia content.

## Features

- **Workspace Management**: Organize documents and chats into isolated workspaces with custom RAG configurations
- **Real-time Chat**: WebSocket-based streaming responses with token-by-token display
- **Document Management**: Upload and manage PDF/text documents per workspace
- **Conversation Memory**: Persistent chat sessions with context preservation
- **Dual RAG Support**: Interface for both Vector RAG and Graph RAG with configurable parameters
- **User Authentication**: Secure login/signup with JWT-based authentication
- **Theme Support**: Light/dark mode with user preferences
- **Input Validation**: Client-side validation for security and UX
- **Responsive Design**: Mobile-friendly interface built with TailwindCSS
- **TypeScript**: Full type safety throughout the application

## Tech Stack

- **React 19** with TypeScript
- **Vite** for fast development and building
- **TailwindCSS** for styling
- **Redux Toolkit** for state management
- **Socket.IO Client** for real-time communication
- **Axios** for REST API calls
- **React Query** for server state management
- **Vitest** for unit testing
- **React Testing Library** for component testing
- **MSW** for API mocking
- **Storybook** for component documentation

## Development Setup

### Prerequisites

- Node.js 18+
- Bun (recommended) or npm
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

We use **Taskfile** for task automation (requires Task CLI).

```bash
# Development
task dev             # Start Vite dev server with HMR
task build           # Build for production
task preview         # Preview production build

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
task storybook       # Run Storybook dev server
task storybook:build # Build Storybook for production

# Security
task audit           # Audit dependencies
task scan            # Run Trivy security scan
task security        # Run all security checks

# Cleanup
task clean           # Remove generated files and node_modules
```

You can also use Bun directly:

```bash
bun run dev
bun run test:run
# etc.
```

## Project Structure

```
packages/client/
+-- src/
|   +-- components/          # React components
|   |   +-- auth/           # Authentication components
|   |   |   +-- LoginForm.tsx/test.tsx/stories.tsx
|   |   |   +-- SignupForm.tsx/test.tsx/stories.tsx
|   |   |   +-- UserMenu.tsx/test.tsx/stories.tsx
|   |   +-- chat/           # Chat interface components
|   |   |   +-- ChatBot.tsx           # Main chat component
|   |   |   +-- ChatInput.tsx/test.tsx/stories.tsx
|   |   |   +-- ChatMessages.tsx/test.tsx/stories.tsx
|   |   |   +-- ChatSidebar.tsx/test.tsx/stories.tsx
|   |   |   +-- MarkdownRenderer.tsx  # Markdown display
|   |   |   +-- TypingIndicator.tsx   # Loading animation
|   |   +-- ui/             # Reusable UI components
|   |   |   +-- ThemeToggle.tsx
|   |   |   +-- button.tsx/stories.tsx
|   |   +-- upload/         # Document upload components
|   |   |   +-- FileUpload.tsx/test.tsx/stories.tsx
|   |   |   +-- DocumentList.tsx/test.tsx
|   |   |   +-- DocumentManager.tsx
|   |   +-- workspace/      # Workspace management
|   |   |   +-- WorkspaceSelector.tsx/test.tsx/stories.tsx
|   |   |   +-- WorkspaceSettings.tsx/stories.tsx
|   +-- lib/                # Utilities and helpers
|   |   +-- utils.ts        # General utilities
|   |   +-- chatStorage.ts/test.ts  # Local storage helpers
|   |   +-- validation.ts/test.ts   # Input validation
|   +-- services/           # API and external service integrations
|   |   +-- api.ts/test.ts  # REST API client (with MSW mocks)
|   |   +-- socket.ts/test.ts  # WebSocket/Socket.IO client
|   +-- store/              # Redux state management
|   |   +-- slices/         # Redux slices
|   |   |   +-- authSlice.ts/test.ts
|   |   |   +-- chatSlice.ts/test.ts
|   |   |   +-- themeSlice.ts/test.ts
|   |   |   +-- workspaceSlice.ts/test.ts
|   |   +-- hooks.ts        # Typed hooks
|   |   +-- index.ts        # Store configuration
|   +-- types/              # TypeScript type definitions
|   |   +-- chat.ts         # Chat-related types
|   |   +-- workspace.ts    # Workspace-related types
|   +-- stories/            # Storybook configuration
|   +-- test/               # Test setup
|   |   +-- setup.ts        # Vitest configuration
|   +-- App.tsx             # Main application component
|   +-- main.tsx            # Application entry point
|   +-- vite-env.d.ts       # Vite type definitions
+-- docs/                   # Documentation
|   +-- components.md       # Component documentation
|   +-- state-management.md # Redux documentation
|   +-- testing.md          # Testing guide
|   +-- workspace-feature.md # Workspace feature docs
+-- public/                 # Static assets
+-- .storybook/             # Storybook configuration
+-- index.html              # HTML template
+-- package.json            # Dependencies and scripts
+-- Taskfile.yml            # Task automation
+-- vitest.config.ts        # Vitest configuration
+-- vite.config.ts          # Vite configuration
```

## Key Components

### ChatBot Component

The main chat interface that handles:

- Real-time message streaming via Socket.IO
- Conversation session management
- Typing indicators and sound notifications
- Error handling and connection management

### Socket Service

Manages WebSocket connections for real-time features:

- Connection lifecycle (connect/disconnect)
- Event handling (chunks, completions, errors)
- Message sending with session context

### Document Management

Components for uploading and managing documents:

- File upload with drag-and-drop support
- Document listing and deletion
- Progress indicators and error handling

## State Management

Uses Redux Toolkit for global state:

- **Auth Slice**: User authentication state
- **Chat Slice**: Chat messages, sessions, and UI state

## API Integration

### REST API

- Document upload/download
- Session management
- User authentication

### WebSocket (Socket.IO)

- Real-time chat message streaming
- Connection status updates
- Error notifications

## Development Guidelines

### Code Style

- **TypeScript**: Strict type checking enabled
- **ESLint**: React and TypeScript rules
- **Prettier**: Consistent code formatting
- **Component Naming**: PascalCase for components, camelCase for utilities

### Component Patterns

- **Functional Components**: Preferred over class components
- **Custom Hooks**: For reusable logic
- **Props Interface**: Define types for component props
- **Error Boundaries**: For error handling in component trees

### State Management

- **Local State**: `useState` for component-specific state
- **Global State**: Redux for app-wide state
- **Server State**: React Query for API data

## Building for Production

```bash
# Build the application
bun run build

# The build artifacts will be stored in the `dist/` directory
```

## Environment Variables

Create a `.env.local` file for local development:

```bash
# API endpoints
VITE_API_BASE_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000

# Feature flags
VITE_ENABLE_DEBUG=true
```

## Testing

See [testing guide](../../docs/testing.md) for the complete testing guide.

### Quick Test Commands

```bash
# Unit Tests (Vitest)
task test                  # Run all unit tests
task test:watch            # Watch mode
task test:coverage         # With coverage report
task test:ui               # Interactive UI

# E2E Tests (Playwright)
task test:e2e              # Run E2E tests
task test:e2e:ui           # Interactive UI mode
task test:e2e:headed       # See browser in action

# Component Documentation (Storybook)
task storybook             # Run Storybook dev server (http://localhost:6006)
task storybook:build       # Build static Storybook
```

### Test Coverage

**Current Stats**: 438 tests passing across 17 test files

**Test Categories**:

- Component tests: 200+ tests
- Redux slice tests: 100+ tests
- Service/utility tests: 100+ tests
- Storybook stories: 50+ stories

**Coverage Thresholds**:

- Lines: > 80%
- Functions: > 80%
- Branches: > 75%
- Statements: > 80%

**Test Files**:

- Unit tests: `src/**/*.test.{ts,tsx}`
- Component tests: `src/components/**/*.test.tsx`
- Stories: `src/**/*.stories.tsx`

**Key Test Features**:

- MSW for API mocking
- React Testing Library for component testing
- Vitest for fast test execution
- Coverage reporting with v8

## Docker Integration

The client is containerized and can be run via Docker Compose:

```bash
# From project root
docker compose up client-dev  # Development with hot reload
docker compose up client      # Production build
```

## Contributing

1. Follow the existing code style and patterns
2. Add TypeScript types for new features
3. Update component documentation
4. Test changes in both development and production modes
5. Ensure responsive design works on mobile devices
