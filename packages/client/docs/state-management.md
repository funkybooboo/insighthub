# State Management Documentation

This document explains the state management architecture in the InsightHub client application.

## Table of Contents

- [Overview](#overview)
- [Redux Store Structure](#redux-store-structure)
- [Slices](#slices)
- [Typed Hooks](#typed-hooks)
- [Best Practices](#best-practices)
- [Examples](#examples)

## Overview

The application uses **Redux Toolkit** for global state management, providing a predictable state container with minimal boilerplate.

### Technology Stack

- **Redux Toolkit**: Modern Redux with less boilerplate
- **React-Redux**: React bindings for Redux
- **Redux Thunk**: Async logic middleware (included in Redux Toolkit)

### State Categories

1. **Global State (Redux)**: App-wide state that multiple components need
2. **Server State (React Query)**: Data from API calls with caching
3. **Local State (useState)**: Component-specific state

## Redux Store Structure

**Location**: `src/store/index.ts`

```typescript
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import chatReducer from './slices/chatSlice';

export const store = configureStore({
    reducer: {
        auth: authReducer,
        chat: chatReducer,
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Store Organization

```
src/store/
--- index.ts              # Store configuration
--- hooks.ts              # Typed useAppSelector and useAppDispatch
--- slices/               # Feature-based slices
    --- authSlice.ts      # Authentication state
    --- chatSlice.ts      # Chat state
```

## Slices

### Auth Slice

**Location**: `src/store/slices/authSlice.ts`

Manages authentication and user session state.

#### State Shape

```typescript
interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
}

interface User {
    id: string;
    username: string;
    email: string;
    fullName?: string;
}
```

#### Actions

```typescript
// Synchronous actions
authSlice.actions.setUser(user: User)
authSlice.actions.setToken(token: string)
authSlice.actions.logout()
authSlice.actions.setLoading(isLoading: boolean)
authSlice.actions.setError(error: string | null)

// Async thunks
loginUser(credentials: LoginCredentials)
registerUser(userData: RegisterData)
logoutUser()
```

#### Selectors

```typescript
// Select current users
const user = useAppSelector((state) => state.auth.user);

// Select auth status
const isAuthenticated = useAppSelector((state) => state.auth.isAuthenticated);

// Select loading state
const isLoading = useAppSelector((state) => state.auth.isLoading);

// Select error
const error = useAppSelector((state) => state.auth.error);
```

#### Example Usage

```typescript
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { loginUser, logout } from '@/store/slices/authSlice';

function LoginForm() {
  const dispatch = useAppDispatch();
  const { isLoading, error } = useAppSelector(state => state.auth);

  const handleLogin = async (credentials: LoginCredentials) => {
    await dispatch(loginUser(credentials));
  };

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <form onSubmit={handleLogin}>
      {/* Form fields */}
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### Chat Slice

**Location**: `src/store/slices/chatSlice.ts`

Manages chat messages, sessions, and UI state.

#### State Shape

```typescript
interface ChatState {
    messages: ChatMessage[];
    sessions: ChatSession[];
    currentSessionId: string | null;
    isTyping: boolean;
    isConnected: boolean;
    error: string | null;
}

interface ChatMessage {
    id: string;
    sessionId: string;
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    metadata?: Record<string, any>;
}

interface ChatSession {
    id: string;
    title: string;
    createdAt: Date;
    updatedAt: Date;
    messageCount: number;
    ragType: 'vector' | 'graph';
}
```

#### Actions

```typescript
// Message actions
chatSlice.actions.addMessage(message: ChatMessage)
chatSlice.actions.updateMessage(messageId: string, content: string)
chatSlice.actions.clearMessages()

// Session actions
chatSlice.actions.setCurrentSession(sessionId: string)
chatSlice.actions.addSession(session: ChatSession)
chatSlice.actions.removeSession(sessionId: string)

// UI state actions
chatSlice.actions.setTyping(isTyping: boolean)
chatSlice.actions.setConnected(isConnected: boolean)
chatSlice.actions.setError(error: string | null)
```

#### Selectors

```typescript
// Select messages for current session
const messages = useAppSelector((state) => {
    const sessionId = state.chat.currentSessionId;
    return state.chat.messages.filter((m) => m.sessionId === sessionId);
});

// Select all sessions
const sessions = useAppSelector((state) => state.chat.sessions);

// Select current session
const currentSession = useAppSelector((state) => {
    const sessionId = state.chat.currentSessionId;
    return state.chat.sessions.find((s) => s.id === sessionId);
});

// Select typing state
const isTyping = useAppSelector((state) => state.chat.isTyping);

// Select connection state
const isConnected = useAppSelector((state) => state.chat.isConnected);
```

#### Example Usage

```typescript
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  addMessage,
  setTyping,
  setCurrentSession,
} from '@/store/slices/chatSlice';

function ChatComponent() {
  const dispatch = useAppDispatch();
  const messages = useAppSelector(state => {
    const sessionId = state.chat.currentSessionId;
    return state.chat.messages.filter(m => m.sessionId === sessionId);
  });
  const isTyping = useAppSelector(state => state.chat.isTyping);

  const handleSendMessage = (content: string) => {
    // Add users message
    dispatch(addMessage({
      id: generateId(),
      sessionId: currentSessionId,
      role: 'user',
      content,
      timestamp: new Date(),
    }));

    // Set typing state
    dispatch(setTyping(true));

    // Send via WebSocket (handled by Socket.IO service)
    socketService.sendMessage({ message: content, sessionId: currentSessionId });
  };

  return (
    <div>
      <ChatMessages messages={messages} isTyping={isTyping} />
      <ChatInput onSend={handleSendMessage} />
    </div>
  );
}
```

## Typed Hooks

**Location**: `src/store/hooks.ts`

Pre-typed versions of `useDispatch` and `useSelector` for better TypeScript support.

```typescript
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';
import type { RootState, AppDispatch } from './index';

// Use throughout the app instead of plain useDispatch and useSelector
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

### Benefits

- Full TypeScript autocomplete for state
- Type-safe dispatch of actions
- Catch errors at compile time

### Usage

```typescript
// GOOD: Typed hooks
import { useAppDispatch, useAppSelector } from '@/store/hooks';

const user = useAppSelector((state) => state.auth.user); // Fully typed!
const dispatch = useAppDispatch();

// BAD: Untyped hooks
import { useDispatch, useSelector } from 'react-redux';

const user = useSelector((state: any) => state.auth.user); // Manual typing needed
const dispatch = useDispatch();
```

## Best Practices

### 1. Keep State Normalized

```typescript
// GOOD: Normalized state
interface ChatState {
    messagesById: Record<string, ChatMessage>;
    messageIds: string[];
    sessionsById: Record<string, ChatSession>;
    sessionIds: string[];
}

// BAD: Nested/duplicated state
interface ChatState {
    sessions: {
        id: string;
        messages: ChatMessage[]; // Duplicated data
    }[];
}
```

### 2. Use Immer for Immutable Updates

Redux Toolkit uses Immer internally, allowing "mutating" syntax:

```typescript
const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        addMessage(state, action) {
            // Looks like mutation, but Immer handles immutability
            state.messages.push(action.payload);
        },
        updateMessage(state, action) {
            const message = state.messages.find((m) => m.id === action.payload.id);
            if (message) {
                message.content = action.payload.content;
            }
        },
    },
});
```

### 3. Co-locate Selectors with Slices

```typescript
// In authSlice.ts
export const selectUser = (state: RootState) => state.auth.user;
export const selectIsAuthenticated = (state: RootState) => state.auth.isAuthenticated;

// In component
import { selectUser } from '@/store/slices/authSlice';

const user = useAppSelector(selectUser);
```

### 4. Use Async Thunks for Side Effects

```typescript
import { createAsyncThunk } from '@reduxjs/toolkit';

export const fetchMessages = createAsyncThunk('chats/fetchMessages', async (sessionId: string) => {
    const response = await api.getMessages(sessionId);
    return response.data;
});

const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        /* ... */
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchMessages.pending, (state) => {
                state.isLoading = true;
            })
            .addCase(fetchMessages.fulfilled, (state, action) => {
                state.messages = action.payload;
                state.isLoading = false;
            })
            .addCase(fetchMessages.rejected, (state, action) => {
                state.error = action.error.message || 'Failed to fetch messages';
                state.isLoading = false;
            });
    },
});
```

### 5. Don't Store Derived Data

```typescript
// BAD: Storing derived data
interface ChatState {
    messages: ChatMessage[];
    messageCount: number; // Derived from messages.length
}

// GOOD: Compute derived data in selectors
const selectMessageCount = (state: RootState) => state.chat.messages.length;

// Or use createSelector from Redux Toolkit (memoized)
import { createSelector } from '@reduxjs/toolkit';

const selectSessionMessages = createSelector(
    (state: RootState) => state.chat.messages,
    (state: RootState) => state.chat.currentSessionId,
    (messages, sessionId) => messages.filter((m) => m.sessionId === sessionId)
);
```

### 6. Handle WebSocket State Carefully

```typescript
// Update Redux state from Socket.IO events
socketService.onChatChunk((chunk) => {
    dispatch(appendToCurrentMessage(chunk));
});

socketService.onChatComplete((data) => {
    dispatch(setTyping(false));
    dispatch(addMessage(data.message));
});

socketService.onError((error) => {
    dispatch(setError(error.message));
    dispatch(setTyping(false));
});
```

## Examples

### Complete Chat Flow

```typescript
import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  addMessage,
  setTyping,
  setConnected,
  setError,
} from '@/store/slices/chatSlice';
import socketService from '@/services/socket';

function ChatContainer() {
  const dispatch = useAppDispatch();
  const messages = useAppSelector(state => {
    const sessionId = state.chat.currentSessionId;
    return state.chat.messages.filter(m => m.sessionId === sessionId);
  });
  const isTyping = useAppSelector(state => state.chat.isTyping);
  const isConnected = useAppSelector(state => state.chat.isConnected);

  useEffect(() => {
    // Connect to WebSocket
    socketService.connect();

    // Set up event listeners
    socketService.onConnect(() => {
      dispatch(setConnected(true));
    });

    socketService.onDisconnect(() => {
      dispatch(setConnected(false));
    });

    socketService.onChatChunk((chunk) => {
      // Append chunk to current message
      // (implementation details omitted)
    });

    socketService.onChatComplete((data) => {
      dispatch(setTyping(false));
      dispatch(addMessage(data.message));
    });

    socketService.onError((error) => {
      dispatch(setError(error.message));
      dispatch(setTyping(false));
    });

    // Cleanup
    return () => {
      socketService.disconnect();
    };
  }, [dispatch]);

  const handleSendMessage = (content: string) => {
    const userMessage: ChatMessage = {
      id: generateId(),
      sessionId: currentSessionId,
      role: 'user',
      content,
      timestamp: new Date(),
    };

    dispatch(addMessage(userMessage));
    dispatch(setTyping(true));

    socketService.sendMessage({
      message: content,
      sessionId: currentSessionId,
    });
  };

  return (
    <div>
      {!isConnected && <div>Connecting...</div>}
      <ChatMessages messages={messages} isTyping={isTyping} />
      <ChatInput onSend={handleSendMessage} disabled={!isConnected} />
    </div>
  );
}
```

### Session Management

```typescript
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import {
  setCurrentSession,
  addSession,
  removeSession,
} from '@/store/slices/chatSlice';
import api from '@/services/api';

function SessionManager() {
  const dispatch = useAppDispatch();
  const sessions = useAppSelector(state => state.chat.sessions);
  const currentSessionId = useAppSelector(state => state.chat.currentSessionId);

  const handleNewSession = async () => {
    const newSession = await api.createSession();
    dispatch(addSession(newSession));
    dispatch(setCurrentSession(newSession.id));
  };

  const handleSelectSession = (sessionId: string) => {
    dispatch(setCurrentSession(sessionId));
  };

  const handleDeleteSession = async (sessionId: string) => {
    await api.deleteSession(sessionId);
    dispatch(removeSession(sessionId));

    // Switch to another session if current was deleted
    if (sessionId === currentSessionId && sessions.length > 1) {
      const nextSession = sessions.find(s => s.id !== sessionId);
      if (nextSession) {
        dispatch(setCurrentSession(nextSession.id));
      }
    }
  };

  return (
    <div>
      <button onClick={handleNewSession}>New Session</button>
      <ul>
        {sessions.map(session => (
          <li
            key={session.id}
            onClick={() => handleSelectSession(session.id)}
            className={session.id === currentSessionId ? 'active' : ''}
          >
            {session.title}
            <button onClick={() => handleDeleteSession(session.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## Testing Redux

### Testing Reducers

```typescript
import chatReducer, { addMessage, setTyping } from './chatSlice';

describe('chatSlice', () => {
    it('should add message to state', () => {
        const initialState = { messages: [] /* ... */ };
        const message = {
            id: '1',
            sessionId: 'session-1',
            role: 'user',
            content: 'Hello',
            timestamp: new Date(),
        };

        const state = chatReducer(initialState, addMessage(message));

        expect(state.messages).toHaveLength(1);
        expect(state.messages[0]).toEqual(message);
    });

    it('should set typing state', () => {
        const initialState = { isTyping: false /* ... */ };

        const state = chatReducer(initialState, setTyping(true));

        expect(state.isTyping).toBe(true);
    });
});
```

### Testing Components with Redux

```typescript
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import chatReducer from '@/store/slices/chatSlice';
import ChatComponent from './ChatComponent';

function renderWithRedux(component: React.ReactElement, initialState = {}) {
  const store = configureStore({
    reducer: { chat: chatReducer },
    preloadedState: initialState,
  });

  return render(<Provider store={store}>{component}</Provider>);
}

describe('ChatComponent', () => {
  it('displays messages from Redux state', () => {
    const initialState = {
      chat: {
        messages: [
          { id: '1', role: 'user', content: 'Hello', /* ... */ },
        ],
        /* ... */
      },
    };

    renderWithRedux(<ChatComponent />, initialState);

    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

## Performance Optimization

### Memoized Selectors

```typescript
import { createSelector } from '@reduxjs/toolkit';

// Expensive computation only runs when dependencies change
const selectSessionMessages = createSelector(
    [(state: RootState) => state.chat.messages, (state: RootState) => state.chat.currentSessionId],
    (messages, sessionId) => {
        // Expensive filtering/sorting
        return messages
            .filter((m) => m.sessionId === sessionId)
            .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    }
);
```

### Avoid Unnecessary Re-renders

```typescript
// BAD: Creates new array on every render
const messages = useAppSelector((state) =>
    state.chat.messages.filter((m) => m.sessionId === currentSessionId)
);

// GOOD: Use memoized selector
const messages = useAppSelector(selectSessionMessages);
```
