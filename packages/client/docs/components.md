# Component Documentation

This document provides detailed information about React 19 components in the InsightHub client application.

## Table of Contents

- [Component Architecture](#component-architecture)
- [Chat Components](#chat-components)
- [Document Management Components](#document-management-components)
- [UI Components](#ui-components)
- [Component Guidelines](#component-guidelines)
- [React 19 Features](#react-19-features)

## Component Architecture

The application follows a modular component architecture with clear separation of concerns:

```
src/components/
- auth/              # Authentication components
- chat/              # Chat interface components
- ui/                # Reusable UI components
- upload/            # Document upload components
```

## Chat Components

### ChatBot

**Location**: `src/components/chat/ChatBot.tsx`

Main chat interface component that orchestrates the entire chat experience.

**Props**:

```typescript
interface ChatBotProps {
    sessionId?: string; // Optional session ID to resume
}
```

**Features**:

- Real-time message streaming via Socket.IO
- Conversation session management
- Typing indicators
- Sound notifications on message completion
- Error handling and retry logic

**State Management**:

- Uses Redux Toolkit for global chat state
- Local state for current message input
- Ref for accumulating streaming tokens

**WebSocket Events**:

- `chat_chunk`: Receives streaming tokens
- `chat_complete`: Message completion event
- `error`: Error notifications

**React 19 Features**:

- Uses `useTransition` for smooth streaming UI updates
- Concurrent rendering support with React 18 features
- Automatic batching for performance optimization

### ChatMessages

**Location**: `src/components/chat/ChatMessages.tsx`

Displays the conversation history with proper formatting and styling.

**Props**:

```typescript
interface ChatMessagesProps {
    messages: ChatMessage[];
    isTyping: boolean;
}
```

**Features**:

- Auto-scrolling to latest message
- Message role-based styling
- Markdown rendering for assistant messages
- Typing indicator animation
- Source citation display with links

### ChatInput

**Location**: `src/components/chat/ChatInput.tsx`

Input component for composing and sending chat messages.

**Props**:

```typescript
interface ChatInputProps {
    onSendMessage: (message: string) => void;
    disabled?: boolean;
    placeholder?: string;
}
```

**Features**:

- Multi-line text input with auto-resize
- Enter to send, Shift+Enter for new line
- Character limit indicator
- Send button with loading state
- File attachment support (planned)

### ChatSidebar

**Location**: `src/components/chat/ChatSidebar.tsx`

Sidebar component for managing chat sessions.

**Props**:

```typescript
interface ChatSidebarProps {
    sessions: ChatSession[];
    currentSessionId?: string;
    onSelectSession: (sessionId: string) => void;
    onNewSession: () => void;
    onDeleteSession: (sessionId: string) => void;
}
```

**Features**:

- Session list with search and filter
- Create new session
- Delete session with confirmation
- Session title auto-generation from first message
- Session sorting by last activity

## Document Management Components

### DocumentUpload

**Location**: `src/components/upload/DocumentUpload.tsx`

Component for uploading documents to the system.

**Props**:

```typescript
interface DocumentUploadProps {
    onUploadComplete: (document: Document) => void;
    acceptedFileTypes?: string[];
    maxFileSize?: number;
}
```

**Features**:

- Drag-and-drop file upload
- File type validation (PDF, DOCX, HTML, TXT)
- File size validation
- Upload progress indicator with percentage
- Multiple file selection
- Error handling with retry options

### DocumentList

**Location**: `src/components/upload/DocumentList.tsx`

Displays list of uploaded documents with management options.

**Props**:

```typescript
interface DocumentListProps {
    documents: Document[];
    onDelete: (documentId: string) => void;
    onDownload: (documentId: string) => void;
}
```

**Features**:

- Document listing with metadata (file size, type, status)
- Download document functionality
- Delete document with confirmation
- File size formatting (KB, MB)
- Date formatting with relative time
- Status badges (processing, completed, failed)

## UI Components

### Button

**Location**: `src/components/ui/Button.tsx`

Reusable button component with consistent styling and variants.

**Props**:

```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
}
```

**Features**:

- Multiple visual variants (primary, secondary, danger)
- Size variations (small, medium, large)
- Loading state with spinner
- Disabled state handling
- Full TypeScript support with proper forwarding

### Input

**Location**: `src/components/ui/Input.tsx`

Form input component with validation support.

**Props**:

```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    helperText?: string;
}
```

**Features**:

- Floating label animation
- Error state styling
- Helper text display
- Multiple input types (text, email, password)
- Accessibility attributes (ARIA labels)

### Modal

**Location**: `src/components/ui/Modal.tsx`

Modal dialog component for confirmations and forms.

**Props**:

```typescript
interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    children: React.ReactNode;
}
```

**Features**:

- Backdrop overlay with click-to-close
- Escape key to close
- Focus trap for accessibility
- Animated open/close transitions
- Custom header and footer support

## Component Guidelines

### TypeScript

All components must be fully typed:

```typescript
// GOOD: Fully typed component
interface UserCardProps {
  user: User;
  onEdit: (userId: string) => void;
}

export const UserCard: React.FC<UserCardProps> = ({ user, onEdit }) => {
  return (
    <div onClick={() => onEdit(user.id)}>
      {user.name}
    </div>
  );
};

// BAD: No types
export const UserCard = ({ user, onEdit }) => {
  return <div onClick={() => onEdit(user.id)}>{user.name}</div>;
};
```

### Component Naming

- Use PascalCase for component files and names
- Prefix boolean props with `is`, `has`, or `should`
- Use descriptive prop names
- Export components individually and as barrel exports

### State Management

- Use local state (`useState`) for component-specific state
- Use Redux Toolkit for global application state
- Use React Query for server state caching
- Proper dependency arrays in hooks

### Event Handlers

- Prefix event handler props with `on`
- Name handler functions with `handle` prefix
- Use proper event types

```typescript
interface Props {
  onClick: () => void;
  onSubmit: (data: FormData) => void;
}

const Component: React.FC<Props> = ({ onClick, onSubmit }) => {
  const handleClick = () => {
    // Do something
    onClick();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return <form onSubmit={handleSubmit}>...</form>;
};
```

### Error Boundaries

Wrap components that might fail with error boundaries:

```typescript
import { ErrorBoundary } from '@/components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      <ChatBot />
    </ErrorBoundary>
  );
}
```

### Accessibility

- Use semantic HTML elements
- Provide ARIA labels for interactive elements
- Ensure keyboard navigation works
- Test with screen readers

```tsx
// GOOD: Accessible button
<button
  onClick={handleClick}
  aria-label="Send message"
  disabled={isLoading}
>
  Send
</button>

// BAD: Inaccessible div
<div onClick={handleClick}>
  Send
</div>
```

### Performance

- Use `React.memo()` for expensive components
- Use `useMemo()` and `useCallback()` for expensive computations
- Lazy load components with `React.lazy()`
- Virtual scrolling for long lists (planned)

```typescript
// Memoized component
export const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{/* Expensive rendering */}</div>;
});

// Lazy loaded component
const ChatBot = React.lazy(() => import('./components/chats/ChatBot'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <ChatBot />
    </Suspense>
  );
}
```

## React 19 Features

### Concurrent Features

React 19 introduces new concurrent features that are utilized:

```typescript
// useTransition for smooth UI updates
const [isPending, startTransition] = useTransition();

const handleSubmit = () => {
    startTransition(() => {
        // Update state that might cause re-renders
        setMessages(newMessages);
    });
};

// useDeferredValue for non-critical updates
const [query, setQuery] = useState('');
const deferredQuery = useDeferredValue(query);
```

### Server Components

Support for React Server Components (future enhancement):

```typescript
// Server Component pattern
'use client';

export const ServerComponent = async ({ id }) => {
  const data = await fetchData(id);
  return <div>{data}</div>;
};
```

### Optimizations

- **Automatic Batching**: React 19 automatically batches state updates
- **Reduced Re-renders**: Improved diffing algorithm
- **Better Memory Usage**: More efficient component rendering
- **Concurrent Rendering**: Takes advantage of new concurrent features

## Testing

Write tests for all components:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('supports loading state', () => {
    render(<Button isLoading>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

## Styling

- Use TailwindCSS utility classes
- Create custom classes in `index.css` for reusable styles
- Follow mobile-first responsive design
- Use CSS-in-JS sparingly, prefer Tailwind utilities

```tsx
// GOOD: Tailwind utilities
<div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-md">
  <h2 className="text-lg font-semibold">Title</h2>
  <Button className="ml-auto">Action</Button>
</div>

// Custom styles for complex components
<div className="custom-chat-message">
  {/* Component content */}
</div>
```

## File Organization

```
components/
- chat/
|   - ChatBot.tsx          # Main component
|   - ChatMessages.tsx
|   - ChatInput.tsx
|   - ChatSidebar.tsx
|   - index.ts             # Barrel export
- ui/
|   - Button.tsx
|   - Input.tsx
|   - Modal.tsx
|   - index.ts
- upload/
    - DocumentUpload.tsx
    - DocumentList.tsx
    - index.ts
```

Use barrel exports for cleaner imports:

```typescript
// components/chats/index.ts
export { ChatBot } from './ChatBot';
export { ChatMessages } from './ChatMessages';
export { ChatInput } from './ChatInput';
export { ChatSidebar } from './ChatSidebar';

// Usage
import { ChatBot, ChatMessages } from '@/components/chats';
```

## Modern React Patterns

### Custom Hooks

Encapsulate component logic in custom hooks:

```typescript
// Custom hook for chats functionality
export const useChat = (sessionId: string) => {
    const [messages, setMessages] = useState([]);
    const [isTyping, setIsTyping] = useState(false);

    // Socket.IO integration
    useEffect(() => {
        // Connect and listen for events
    }, [sessionId]);

    return { messages, isTyping, sendMessage /* ... */ };
};
```

### Context Usage

Use React Context for deep component trees:

```typescript
// Theme context example
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | null>(null);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

This component architecture ensures maintainability, testability, and performance while leveraging React 19's latest features.
