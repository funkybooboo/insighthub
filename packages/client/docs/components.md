# Component Documentation

This document provides detailed information about the React components in the InsightHub client application.

## Table of Contents

- [Component Architecture](#component-architecture)
- [Chat Components](#chat-components)
- [Document Management Components](#document-management-components)
- [UI Components](#ui-components)
- [Component Guidelines](#component-guidelines)

## Component Architecture

The application follows a modular component architecture with clear separation of concerns:

```
src/components/
├── auth/              # Authentication components
├── chat/              # Chat interface components
├── ui/                # Reusable UI components
└── upload/            # Document upload components
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

- Uses Redux for global chat state
- Local state for current message input
- Ref for accumulating streaming tokens

**WebSocket Events**:

- `chat_chunk`: Receives streaming tokens
- `chat_complete`: Message completion event
- `error`: Error notifications

**Example Usage**:

```tsx
import { ChatBot } from '@/components/chat/ChatBot';

function App() {
    return <ChatBot sessionId="session-123" />;
}
```

### ChatMessages

**Location**: `src/components/chat/ChatMessages.tsx`

Displays the conversation history with proper formatting and styling.

**Props**:

```typescript
interface ChatMessagesProps {
    messages: ChatMessage[];
    isTyping: boolean;
}

interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    metadata?: Record<string, any>;
}
```

**Features**:

- Auto-scrolling to latest message
- Message role-based styling
- Markdown rendering for assistant messages
- Typing indicator animation

**Example Usage**:

```tsx
import { ChatMessages } from '@/components/chat/ChatMessages';

function ChatContainer({ messages, isTyping }) {
    return <ChatMessages messages={messages} isTyping={isTyping} />;
}
```

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

- Multi-line text input
- Enter to send, Shift+Enter for new line
- Character limit indicator
- Send button with loading state

**Example Usage**:

```tsx
import { ChatInput } from '@/components/chat/ChatInput';

function ChatContainer({ handleSend }) {
    return <ChatInput onSendMessage={handleSend} placeholder="Ask a question..." />;
}
```

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

interface ChatSession {
    id: string;
    title: string;
    createdAt: Date;
    updatedAt: Date;
    messageCount: number;
}
```

**Features**:

- Session list with search/filter
- Create new session
- Delete session with confirmation
- Session title auto-generation

**Example Usage**:

```tsx
import { ChatSidebar } from '@/components/chat/ChatSidebar';

function App({ sessions, currentSessionId }) {
    return (
        <ChatSidebar
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSelectSession={handleSelectSession}
            onNewSession={handleNewSession}
            onDeleteSession={handleDeleteSession}
        />
    );
}
```

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
- File type validation
- File size validation
- Upload progress indicator
- Error handling

**Example Usage**:

```tsx
import { DocumentUpload } from '@/components/upload/DocumentUpload';

function DocumentManager() {
    return (
        <DocumentUpload
            onUploadComplete={handleUploadComplete}
            acceptedFileTypes={['.pdf', '.txt']}
            maxFileSize={16 * 1024 * 1024} // 16MB
        />
    );
}
```

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

interface Document {
    id: string;
    filename: string;
    fileSize: number;
    mimeType: string;
    createdAt: Date;
    chunkCount?: number;
}
```

**Features**:

- Document listing with metadata
- Download document
- Delete document with confirmation
- File size formatting
- Date formatting

**Example Usage**:

```tsx
import { DocumentList } from '@/components/upload/DocumentList';

function DocumentManager({ documents }) {
    return (
        <DocumentList documents={documents} onDelete={handleDelete} onDownload={handleDownload} />
    );
}
```

## UI Components

### Button

**Location**: `src/components/ui/Button.tsx`

Reusable button component with consistent styling.

**Props**:

```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
}
```

**Example Usage**:

```tsx
import { Button } from '@/components/ui/Button';

function Form() {
    return (
        <>
            <Button variant="primary" size="md">
                Submit
            </Button>
            <Button variant="secondary" size="sm" isLoading>
                Loading...
            </Button>
        </>
    );
}
```

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

**Example Usage**:

```tsx
import { Input } from '@/components/ui/Input';

function Form() {
    return (
        <Input
            label="Email"
            type="email"
            error={errors.email}
            helperText="We'll never share your email"
        />
    );
}
```

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

**Example Usage**:

```tsx
import { Modal } from '@/components/ui/Modal';

function App() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title="Confirm Delete">
            <p>Are you sure you want to delete this document?</p>
            <Button onClick={handleDelete}>Delete</Button>
        </Modal>
    );
}
```

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

```typescript
// GOOD
interface ButtonProps {
    isLoading: boolean;
    hasError: boolean;
    shouldAutoFocus: boolean;
}

// BAD
interface ButtonProps {
    loading: boolean;
    error: boolean;
    focus: boolean;
}
```

### State Management

- Use local state (`useState`) for component-specific state
- Use Redux for global application state
- Use React Query for server state

```typescript
// Component-specific state
const [isOpen, setIsOpen] = useState(false);

// Global state
const messages = useAppSelector((state) => state.chat.messages);
const dispatch = useAppDispatch();

// Server state
const { data: documents } = useQuery(['documents'], fetchDocuments);
```

### Event Handlers

- Prefix event handler props with `on`
- Name handler functions with `handle` prefix

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

```typescript
// Memoized component
export const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{/* Expensive rendering */}</div>;
});

// Lazy loaded component
const ChatBot = React.lazy(() => import('./components/chat/ChatBot'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <ChatBot />
    </Suspense>
  );
}
```

### Testing

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
});
```

## Styling

- Use TailwindCSS utility classes
- Create custom classes in `index.css` for reusable styles
- Follow mobile-first responsive design

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
├── chat/
│   ├── ChatBot.tsx          # Main component
│   ├── ChatMessages.tsx
│   ├── ChatInput.tsx
│   ├── ChatSidebar.tsx
│   └── index.ts             # Barrel export
├── ui/
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Modal.tsx
│   └── index.ts
└── upload/
    ├── DocumentUpload.tsx
    ├── DocumentList.tsx
    └── index.ts
```

Use barrel exports for cleaner imports:

```typescript
// components/chat/index.ts
export { ChatBot } from './ChatBot';
export { ChatMessages } from './ChatMessages';
export { ChatInput } from './ChatInput';
export { ChatSidebar } from './ChatSidebar';

// Usage
import { ChatBot, ChatMessages } from '@/components/chat';
```
