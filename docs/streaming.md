# Socket.IO Streaming Implementation

Comprehensive WebSocket streaming implementation for InsightHub dual RAG system, enabling real-time LLM response streaming and bidirectional communication between React frontend and Flask backend.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Backend Implementation](#backend-implementation)
  - [Dependencies](#dependencies)
  - [LLM Provider Interface](#llm-provider-interface)
  - [Provider Implementations](#provider-implementations)
  - [Flask Application](#flask-application)
- [Frontend Implementation](#frontend-implementation)
  - [Dependencies](#dependencies-1)
  - [Socket Service](#socket-service)
  - [Chat Component Integration](#chat-component-integration)
- [Socket.IO Events](#socketio-events)
- [Real-time Features](#real-time-features)
- [Testing](#testing)
- [Performance Optimization](#performance-optimization)
- [Error Handling](#error-handling)
- [Future Enhancements](#future-enhancements)

---

## Overview

InsightHub uses Socket.IO for bidirectional WebSocket communication between React frontend and Flask backend. This enables real-time features including token-by-token LLM response streaming, document processing status updates, and workspace provisioning feedback.

### Key Features

- **Chat Streaming**: LLM responses streamed token-by-token for immediate feedback
- **Status Updates**: Real-time progress updates for document processing and workspace operations
- **Connection Management**: Automatic reconnection with state preservation
- **Event-Driven**: RabbitMQ integration for async processing with WebSocket forwarding
- **Error Handling**: Graceful error propagation with user-friendly messages

---

## Architecture

### Connection Flow

```
React Client (Socket.IO Client)
      -> WebSocket Events
Flask Server (Socket.IO Server)
      -> Chat Service
      -> RabbitMQ (async processing)
      -> Chat Worker
      -> RAG System + LLM
      -> Response Events back to Client
     -> (Streaming Response)
Flask Server (Socket.IO)
     -> (Chunk Events)
React Client (Real-time UI Updates)
```

### Component Architecture

**Backend Components**:
- **Socket.IO Server**: WebSocket connection management
- **LLM Provider Interface**: Abstract streaming interface
- **Provider Implementations**: Ollama, OpenAI, Claude, HuggingFace
- **Event Handlers**: Chat, status, and error event processing
- **Session Management**: Chat session persistence and retrieval

**Frontend Components**:
- **Socket Service**: Connection and event management
- **Chat Components**: Real-time message display and interaction
- **State Management**: Redux integration for streaming state
- **UI Components**: Typing indicators, progress bars, error displays

---

## Backend Implementation

### Dependencies

**Flask-SocketIO**: WebSocket server for Flask applications
**python-socketio**: Socket.IO server implementation
**Shared Messaging**: RabbitMQ integration for async processing

### Flask Application Setup

```python
# packages/server/src/api.py
from flask_socketio import SocketIO
from src.domains.workspaces.chat.events import register_socket_handlers

socketio = SocketIO(cors_allowed_origins="*")

# Initialize SocketIO with Flask app
socketio.init_app(app)

# Register chat event handlers
register_socket_handlers(socketio)

# Register status update handlers
register_status_socket_handlers(socketio)

# Chat event consumer forwards worker events to WebSocket
chat_event_consumer = create_chat_event_consumer(socketio)
```

### LLM Provider Interface

**Location**: `src/infrastructure/llm/llm.py`

```python
from abc import ABC, abstractmethod
from typing import Generator, Optional, Dict, Any

class LlmProvider(ABC):
    """Abstract interface for LLM providers with streaming support."""
    
    @abstractmethod
    def chat_stream(
        self, 
        message: str, 
        conversation_history: Optional[list[Dict[str, str]]] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Generate streaming response for chat message.
        
        Args:
            message: User's chat message
            conversation_history: Previous messages for context
            **kwargs: Additional provider-specific parameters
            
        Yields:
            str: Response tokens/chunks
            
        Raises:
            LlmProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the configured model."""
        pass
```

### Provider Implementations

#### Ollama Provider

```python
# src/infrastructure/llm/ollama_provider.py
import requests
from typing import Generator, Dict, Any
from .llm import LlmProvider

class OllamaProvider(LlmProvider):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    def chat_stream(
        self, 
        message: str, 
        conversation_history: Optional[list[Dict[str, str]]] = None
    ) -> Generator[str, None, None]:
        """Stream response from Ollama API."""
        
        # Build conversation context
        messages = []
        if conversation_history:
            for msg in conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})
        
        # Make streaming request
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "messages": messages,
                "stream": True
            },
            stream=True
        )
        
        # Stream response chunks
        for line in response.iter_lines():
            if line.strip():
                try:
                    data = json.loads(line)
                    if "message" in data.get("response", {}):
                        yield data["response"]["message"]["content"]
                except json.JSONDecodeError:
                    continue
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "ollama",
            "model": self.model,
            "base_url": self.base_url
        }
```

#### OpenAI Provider

```python
# src/infrastructure/llm/openai_provider.py
import openai
from typing import Generator, Dict, Any
from .llm import LlmProvider

class OpenAIProvider(LlmProvider):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def chat_stream(
        self, 
        message: str, 
        conversation_history: Optional[list[Dict[str, str]]] = None
    ) -> Generator[str, None, None]:
        """Stream response from OpenAI API."""
        
        # Build messages
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        # Create streaming completion
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        
        # Stream response chunks
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "openai",
            "model": self.model
        }
```

### Flask Application

**Location**: `src/api.py`

```python
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import jwt_required, get_jwt_identity
from .domains.chat.service import ChatService
from .infrastructure.socket.socket_handler import SocketHandler

def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize services
    chat_service = ChatService()
    socket_handler = SocketHandler(socketio, chat_service)
    
    # Register Socket.IO event handlers
    socket_handler.register_handlers()
    
    return app, socketio
```

### Socket Handler

**Location**: `src/infrastructure/socket/socket_handler.py`

```python
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from typing import Dict, Any
import uuid

class SocketHandler:
    def __init__(self, socketio: SocketIO, chat_service):
        self.socketio = socketio
        self.chat_service = chat_service
        self.active_sessions: Dict[str, str] = {}
    
    def register_handlers(self):
        """Register all Socket.IO event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            emit('connected', {
                'message': 'Connected to InsightHub chat server',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            session_id = self.active_sessions.get(request.sid)
            if session_id:
                leave_room(session_id)
                del self.active_sessions[request.sid]
        
        @self.socketio.on('chat_message')
        @jwt_required()
        def handle_chat_message(data):
            """Handle incoming chat message."""
            try:
                user_id = get_jwt_identity()
                session_id = data.get('session_id') or str(uuid.uuid4())
                workspace_id = data.get('workspace_id')
                message = data.get('message')
                
                # Join session room
                join_room(session_id)
                self.active_sessions[request.sid] = session_id
                
                # Store user message
                self.chat_service.store_message(
                    session_id=session_id,
                    user_id=user_id,
                    workspace_id=workspace_id,
                    content=message,
                    role='user'
                )
                
                # Stream LLM response
                self._stream_llm_response(
                    session_id=session_id,
                    workspace_id=workspace_id,
                    message=message,
                    user_id=user_id
                )
                
            except Exception as e:
                emit('error', {
                    'message': f'Error processing message: {str(e)}',
                    'timestamp': datetime.utcnow().isoformat()
                })
    
    def _stream_llm_response(self, session_id: str, workspace_id: str, 
                           message: str, user_id: str):
        """Stream LLM response to client."""
        
        try:
            # Get conversation history
            history = self.chat_service.get_conversation_history(session_id)
            
            # Get LLM provider for workspace
            llm_provider = self.chat_service.get_llm_provider(workspace_id)
            
            # Stream response
            full_response = ""
            for chunk in llm_provider.chat_stream(message, history):
                full_response += chunk
                emit('chat_chunk', {
                    'session_id': session_id,
                    'chunk': chunk,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=session_id)
            
            # Store complete response
            self.chat_service.store_message(
                session_id=session_id,
                user_id=user_id,
                workspace_id=workspace_id,
                content=full_response,
                role='assistant'
            )
            
            # Send completion event
            emit('chat_complete', {
                'session_id': session_id,
                'full_response': full_response,
                'timestamp': datetime.utcnow().isoformat()
            }, room=session_id)
            
        except Exception as e:
            emit('error', {
                'message': f'Error generating response: {str(e)}',
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat()
            }, room=session_id)
```

---

## Frontend Implementation

### Dependencies

**socket.io-client**: Socket.IO client for React applications
**TypeScript**: Full type safety for events and data structures

### Socket Service Implementation

```typescript
// packages/client/src/services/socket.ts
import { io, Socket } from 'socket.io-client';

class SocketService {
    private socket: Socket | null = null;

    connect() {
        this.socket = io(import.meta.env.VITE_API_URL || 'http://localhost:5000');
        // Connection event handlers...
    }

    // Chat events
    sendChatMessage(data: ChatMessageData) {
        this.socket?.emit('chat_message', data);
    }

    onChatChunk(callback: (data: ChatChunkData) => void) {
        this.socket?.on('chat_chunk', callback);
    }

    onChatComplete(callback: (data: ChatCompleteData) => void) {
        this.socket?.on('chat_complete', callback);
    }

    // Status events
    onDocumentStatus(callback: (data: DocumentStatusData) => void) {
        this.socket?.on('document_status', callback);
    }

    onWorkspaceStatus(callback: (data: WorkspaceStatusData) => void) {
        this.socket?.on('workspace_status', callback);
    }
}

export default new SocketService();
```

### Socket Service

**Location**: `src/services/socket.ts`

```typescript
import { io, Socket } from 'socket.io-client';
import { ChatMessage, ChatState } from '../types/chat';

export interface SocketService {
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: string, sessionId: string, workspaceId: string) => void;
  onChatChunk: (callback: (chunk: string, sessionId: string) => void) => void;
  onChatComplete: (callback: (response: string, sessionId: string) => void) => void;
  onError: (callback: (error: string) => void) => void;
  onConnected: (callback: () => void) => void;
  onDisconnected: (callback: () => void) => void;
}

class SocketIOService implements SocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  
  constructor(private apiUrl: string) {}
  
  connect(): void {
    if (this.socket?.connected) {
      return;
    }
    
    this.socket = io(this.apiUrl, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
    });
    
    this.setupEventListeners();
  }
  
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.reconnectAttempts = 0;
  }
  
  sendMessage(message: string, sessionId: string, workspaceId: string): void {
    if (this.socket?.connected) {
      this.socket.emit('chat_message', {
        message,
        session_id: sessionId,
        workspace_id: workspaceId
      });
    } else {
      console.error('Socket not connected');
    }
  }
  
  private setupEventListeners(): void {
    if (!this.socket) return;
    
    this.socket.on('connect', () => {
      console.log('Connected to chat server');
      this.reconnectAttempts = 0;
      this.onConnectedCallback?.();
    });
    
    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected from chat server:', reason);
      this.onDisconnectedCallback?.();
    });
    
    this.socket.on('chat_chunk', (data) => {
      this.onChatChunkCallback?.(data.chunk, data.session_id);
    });
    
    this.socket.on('chat_complete', (data) => {
      this.onChatCompleteCallback?.(data.full_response, data.session_id);
    });
    
    this.socket.on('error', (data) => {
      console.error('Socket error:', data);
      this.onErrorCallback?.(data.message);
    });
  }
  
  // Callback properties
  private onConnectedCallback?: () => void;
  private onDisconnectedCallback?: () => void;
  private onChatChunkCallback?: (chunk: string, sessionId: string) => void;
  private onChatCompleteCallback?: (response: string, sessionId: string) => void;
  private onErrorCallback?: (error: string) => void;
  
  // Setters for callbacks
  onConnected(callback: () => void): void {
    this.onConnectedCallback = callback;
  }
  
  onChatChunk(callback: (chunk: string, sessionId: string) => void): void {
    this.onChatChunkCallback = callback;
  }
  
  onChatComplete(callback: (response: string, sessionId: string) => void): void {
    this.onChatCompleteCallback = callback;
  }
  
  onError(callback: (error: string) => void): void {
    this.onErrorCallback = callback;
  }
}

export const socketService = new SocketIOService(process.env.VITE_SOCKET_URL || 'http://localhost:5000');
```

### Chat Component Integration

**Location**: `src/components/chat/ChatBot.tsx`

```typescript
import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { socketService } from '../../services/socket';
import { addMessage, setStreamingStatus } from '../../store/slices/chatSlice';
import { ChatMessage } from '../../types/chat';

export const ChatBot: React.FC = () => {
  const dispatch = useDispatch();
  const { activeSessionId, activeWorkspaceId, messages, isStreaming } = useSelector(
    (state: any) => state.chat
  );
  const [inputValue, setInputValue] = useState('');
  const [currentResponse, setCurrentResponse] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    // Setup socket event listeners
    socketService.onConnected(() => {
      console.log('Connected to chat server');
    });
    
    socketService.onChatChunk((chunk: string, sessionId: string) => {
      if (sessionId === activeSessionId) {
        setCurrentResponse(prev => prev + chunk);
        dispatch(setStreamingStatus(true));
      }
    });
    
    socketService.onChatComplete((response: string, sessionId: string) => {
      if (sessionId === activeSessionId) {
        dispatch(addMessage({
          id: Date.now().toString(),
          content: response,
          role: 'assistant',
          timestamp: new Date(),
          sessionId
        }));
        setCurrentResponse('');
        dispatch(setStreamingStatus(false));
      }
    });
    
    socketService.onError((error: string) => {
      console.error('Chat error:', error);
      dispatch(setStreamingStatus(false));
    });
    
    // Connect to socket
    socketService.connect();
    
    return () => {
      socketService.disconnect();
    };
  }, [activeSessionId, dispatch]);
  
  useEffect(() => {
    // Auto-scroll to bottom on new messages
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentResponse]);
  
  const handleSendMessage = () => {
    if (!inputValue.trim() || !activeSessionId || !activeWorkspaceId) {
      return;
    }
    
    // Add user message to store
    dispatch(addMessage({
      id: Date.now().toString(),
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
      sessionId: activeSessionId
    }));
    
    // Send message via socket
    socketService.sendMessage(inputValue, activeSessionId, activeWorkspaceId);
    
    // Clear input
    setInputValue('');
  };
  
  return (
    <div className="chat-bot">
      <div className="messages-container">
        {messages.map((message: ChatMessage) => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="content">{message.content}</div>
            <div className="timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        
        {/* Streaming response */}
        {isStreaming && currentResponse && (
          <div className="message assistant streaming">
            <div className="content">{currentResponse}</div>
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-container">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              handleSendMessage();
            }
          }}
          placeholder="Type your message..."
          disabled={isStreaming}
          className="chat-input"
        />
        <button
          onClick={handleSendMessage}
          disabled={isStreaming || !inputValue.trim()}
          className="send-button"
        >
          Send
        </button>
      </div>
    </div>
  );
};
```

---

## Socket.IO Events

### Client to Server Events

#### `chat_message`

**Purpose**: Send chat message for async processing via workers

**Client Code**:
```typescript
// packages/client/src/services/socket.ts
socketService.sendChatMessage({
    message: "What is RAG?",
    session_id: 123,
    workspace_id: 456,
    rag_type: "vector"
});
```

**Server Handling**:
```python
# packages/server/src/domains/workspaces/chat/routes.py
@socketio.on('chat_message')
def handle_chat_message(data):
    # Store message and publish to RabbitMQ for worker processing
    chat_service.send_message(workspace_id, session_id, user_id, content)
```

#### `cancel_message`

**Purpose**: Cancel ongoing streaming response

**Client Code**:
```typescript
socketService.cancelMessage();
```

### Server to Client Events

#### `connected`

**Purpose**: Confirm successful connection

**Server Code**:
```python
emit('connected', {
    'message': 'Connected to InsightHub chat server',
    'timestamp': datetime.utcnow().isoformat()
})
```

#### `chat_chunk`

**Purpose**: Stream individual tokens from LLM response

**Server Code** (via chat event consumer):
```python
# packages/server/src/api.py - chat_event_consumer forwards worker events
def on_chat_response_chunk(event_data: dict) -> None:
    socketio.emit('chat_chunk', {
        'chunk': event_data['chunk']
    })
```

**Client Handling**:
```typescript
// packages/client/src/components/chat/ChatBot.tsx
socketService.onChatChunk((data: ChatChunkData) => {
    dispatch(updateMessageInSession({
        sessionId: activeSessionId,
        content: data.chunk,
        append: true
    }));
});
```

#### `chat_complete`

**Purpose**: Signal completion of streaming response

**Server Code**:
```python
# Chat worker publishes completion event
message_publisher.publish('chat.response_complete', {
    'session_id': session_id,
    'message_id': message_id,
    'full_response': full_response
})
```

**Client Handling**:
```typescript
socketService.onChatComplete((data: ChatCompleteData) => {
    dispatch(setTyping(false));
    // Response is complete
});
```

#### `chat_error`

**Purpose**: Report chat processing errors

**Server Code**:
```python
message_publisher.publish('chat.error', {
    'error': 'LLM service unavailable'
})
```

#### Status Events

**Document Status**:
```typescript
socketService.onDocumentStatus((data: DocumentStatusData) => {
    dispatch(updateDocumentStatus(data));
});
```

**Workspace Status**:
```typescript
socketService.onWorkspaceStatus((data: WorkspaceStatusData) => {
    dispatch(updateWorkspaceStatus(data));
});
```

---

## Real-time Features

### Typing Indicators

**Visual feedback during LLM generation**:

```css
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #666;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}
```

### Connection Status

**Real-time connection monitoring**:

```typescript
const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');

useEffect(() => {
  socketService.onConnected(() => {
    setConnectionStatus('connected');
  });
  
  socketService.onDisconnected(() => {
    setConnectionStatus('disconnected');
  });
}, []);
```

### Progress Indicators

**Optional progress tracking for long responses**:

```typescript
interface StreamingState {
  tokensReceived: number;
  estimatedTokensTotal?: number;
  startTime: number;
}

const [streamingState, setStreamingState] = useState<StreamingState>({
  tokensReceived: 0,
  startTime: Date.now()
});
```

---

## Testing

### Backend Testing

**Unit Tests**:
```python
# tests/unit/test_socket_handler.py
import pytest
from unittest.mock import Mock, patch
from src.infrastructure.socket.socket_handler import SocketHandler

def test_handle_chat_message_success():
    """Test successful chat message handling."""
    # Setup
    mock_socketio = Mock()
    mock_chat_service = Mock()
    handler = SocketHandler(mock_socketio, mock_chat_service)
    
    # Mock dependencies
    mock_chat_service.get_conversation_history.return_value = []
    mock_chat_service.get_llm_provider.return_value = MockLlmProvider()
    
    # Execute
    with patch('src.infrastructure.socket.socket_handler.get_jwt_identity', return_value='user123'):
        handler.handle_chat_message({
            'message': 'Hello',
            'session_id': 'session123',
            'workspace_id': 'workspace456'
        })
    
    # Assert
    mock_socketio.emit.assert_any_call('chat_chunk', room='session123')
    mock_chat_service.store_message.assert_called()
```

### Frontend Testing

**Component Tests**:
```typescript
// src/components/chat/ChatBot.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatBot } from './ChatBot';

describe('ChatBot', () => {
  test('sends message on form submission', async () => {
    render(<ChatBot />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    fireEvent.change(input, { target: { value: 'Hello world' } });
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText('Hello world')).toBeInTheDocument();
    });
  });
});
```

**Socket Service Tests**:
```typescript
// src/services/socket.test.ts
import { socketService } from './socket';

// Mock Socket.IO
const mockSocket = {
  on: vi.fn(),
  emit: vi.fn(),
  connect: vi.fn(),
  disconnect: vi.fn(),
  connected: false
};

vi.mock('socket.io-client', () => ({
  io: vi.fn(() => mockSocket)
}));

describe('SocketService', () => {
  test('connects to socket server', () => {
    socketService.connect();
    
    expect(mockSocket.connect).toHaveBeenCalledWith(
      'http://localhost:5000',
      expect.any(Object)
    );
  });
});
```

### Integration Tests

**End-to-End Streaming Test**:
```python
# tests/integration/test_streaming.py
import pytest
import socketio
from testcontainers.postgres import PostgresContainer

def test_full_streaming_workflow(postgres_container):
    """Test complete streaming workflow with real services."""
    # Setup test environment
    # ... container setup code ...
    
    # Create Socket.IO client
    client = socketio.Client()
    
    # Track received events
    received_chunks = []
    received_complete = False
    
    def on_chat_chunk(data):
        received_chunks.append(data['chunk'])
    
    def on_chat_complete(data):
        nonlocal received_complete
        received_complete = True
        assert data['full_response'] == ''.join(received_chunks)
    
    client.on('chat_chunk', on_chat_chunk)
    client.on('chat_complete', on_chat_complete)
    
    # Connect and send message
    client.connect('http://localhost:5000')
    client.emit('chat_message', {
        'message': 'Test streaming',
        'session_id': 'test-session',
        'workspace_id': 'test-workspace'
    })
    
    # Wait for completion
    pytest.wait_for(lambda: received_complete, timeout=30)
```

---

## Performance Optimization

### Backend Optimizations

**Efficient Streaming**:
```python
def _stream_llm_response(self, session_id: str, message: str):
    """Optimized streaming with minimal overhead."""
    
    # Use generator for memory efficiency
    for chunk in self.llm_provider.chat_stream(message):
        # Emit immediately without buffering
        self.socketio.emit('chat_chunk', {
            'session_id': session_id,
            'chunk': chunk,
            'timestamp': datetime.utcnow().isoformat()
        }, room=session_id)
        
        # Small delay to prevent overwhelming client
        time.sleep(0.001)  # 1ms delay
```

**Connection Pooling**:
```python
# Reuse LLM provider instances
class LlmProviderFactory:
    _instances = {}
    
    @classmethod
    def get_provider(cls, workspace_id: str) -> LlmProvider:
        if workspace_id not in cls._instances:
            cls._instances[workspace_id] = cls._create_provider(workspace_id)
        return cls._instances[workspace_id]
```

### Frontend Optimizations

**Efficient State Updates**:
```typescript
// Use React.memo for message components
const MessageComponent = React.memo(({ message }: { message: ChatMessage }) => {
  return (
    <div className={`message ${message.role}`}>
      <div className="content">{message.content}</div>
    </div>
  );
});

// Use useCallback for event handlers
const handleSendMessage = useCallback(() => {
  // Implementation
}, [inputValue, activeSessionId, activeWorkspaceId]);
```

**Debounced Input**:
```typescript
import { useDebouncedCallback } from 'use-debounce';

const debouncedSendMessage = useDebouncedCallback(
  (message: string) => {
    socketService.sendMessage(message, sessionId, workspaceId);
  },
  { delay: 300 }
);
```

---

## Error Handling

### Connection Errors

**Automatic Reconnection**:
```typescript
class SocketIOService {
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  
  private handleDisconnect = (reason: string) => {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  };
}
```

### Streaming Errors

**Graceful Error Handling**:
```python
def _stream_llm_response(self, session_id: str, message: str):
    try:
        for chunk in self.llm_provider.chat_stream(message):
            self.socketio.emit('chat_chunk', {
                'session_id': session_id,
                'chunk': chunk
            }, room=session_id)
            
    except LlmProviderError as e:
        self.socketio.emit('error', {
            'session_id': session_id,
            'message': f'LLM error: {str(e)}',
            'error_type': 'llm_error'
        }, room=session_id)
        
    except Exception as e:
        self.socketio.emit('error', {
            'session_id': session_id,
            'message': f'Server error: {str(e)}',
            'error_type': 'server_error'
        }, room=session_id)
```

### Client Error Handling

**User-Friendly Error Messages**:
```typescript
const [error, setError] = useState<string | null>(null);

socketService.onError((errorMessage: string) => {
  setError(errorMessage);
  
  // Auto-clear error after 5 seconds
  setTimeout(() => setError(null), 5000);
});
```

---

## Future Enhancements

### Advanced Features

1. **Request Cancellation**:
   - Allow users to cancel long-running responses
   - Implement server-side cancellation logic
   - Clean up resources properly

2. **Progress Indicators**:
   - Show tokens/second generation rate
   - Estimate time remaining for long responses
   - Visual progress bars for streaming

3. **Message Queuing**:
   - Queue messages when disconnected
   - Send queued messages on reconnection
   - Maintain message order

4. **Multi-User Support**:
   - Real-time collaboration features
   - User presence indicators
   - Shared typing indicators

5. **Enhanced Error Recovery**:
   - Automatic retry for failed messages
   - Exponential backoff for reconnection
   - Fallback to HTTP polling if WebSocket fails

### Performance Improvements

1. **Binary Streaming**:
   - Use binary protocols for efficiency
   - Compress large messages
   - Implement protocol buffers

2. **Connection Pooling**:
   - Multiple WebSocket connections
   - Load balancing across connections
   - Intelligent connection selection

3. **Caching Strategies**:
   - Cache common responses
   - Implement response deduplication
   - Smart pre-fetching

This comprehensive Socket.IO implementation provides a robust foundation for real-time communication in the InsightHub dual RAG system, ensuring responsive and engaging user experiences.