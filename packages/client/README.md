# InsightHub Client

React frontend for the InsightHub RAG system, providing a modern chatbot interface for querying academic papers and Wikipedia content.

## Features

- **Real-time Chat**: WebSocket-based streaming responses with token-by-token display
- **Document Management**: Upload and manage PDF/text documents
- **Conversation Memory**: Persistent chat sessions with context preservation
- **Dual RAG Support**: Interface for both Vector RAG and Graph RAG (when available)
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

```bash
# Development
bun run dev          # Start Vite dev server with HMR
bun run build        # Build for production
bun run preview      # Preview production build

# Code Quality
bun run lint         # Run ESLint
bun run format       # Format code with Prettier
bun run format:check # Check formatting without fixing

# Testing
bun run test         # Run tests (when available)
```

## Project Structure

```
packages/client/
├── src/
│   ├── components/          # React components
│   │   ├── auth/           # Authentication components
│   │   ├── chat/           # Chat interface components
│   │   │   ├── ChatBot.tsx      # Main chat component
│   │   │   ├── ChatInput.tsx    # Message input
│   │   │   ├── ChatMessages.tsx # Message display
│   │   │   └── ChatSidebar.tsx  # Session management
│   │   ├── ui/             # Reusable UI components
│   │   └── upload/         # Document upload components
│   ├── lib/                # Utilities and helpers
│   │   ├── utils.ts        # General utilities
│   │   └── chatStorage.ts  # Local storage helpers
│   ├── services/           # API and external service integrations
│   │   ├── api.ts          # REST API client
│   │   └── socket.ts       # WebSocket/Socket.IO client
│   ├── store/              # Redux state management
│   │   ├── slices/         # Redux slices
│   │   │   ├── authSlice.ts
│   │   │   └── chatSlice.ts
│   │   ├── hooks.ts        # Typed hooks
│   │   └── index.ts        # Store configuration
│   ├── types/              # TypeScript type definitions
│   │   └── chat.ts         # Chat-related types
│   ├── App.tsx             # Main application component
│   ├── main.tsx            # Application entry point
│   └── vite-env.d.ts       # Vite type definitions
├── public/                 # Static assets
├── index.html              # HTML template
└── package.json            # Dependencies and scripts
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

```bash
# Run tests
bun run test

# Run tests in watch mode
bun run test --watch

# Run tests with coverage
bun run test --coverage
```

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
