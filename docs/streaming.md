# Socket.IO Streaming Implementation

WebSocket streaming for real-time LLM response streaming.

## Overview

Socket.IO enables bidirectional WebSocket connections for token-by-token LLM response streaming from Flask backend to React frontend.

## Backend (Python/Flask)

### Dependencies
- `python-socketio` (v5.14.3)
- `flask-socketio` (v5.5.1)

### LLM Provider Interface

Added streaming to `LlmProvider` (`src/infrastructure/llm/llm.py`):

```python
@abstractmethod
def chat_stream(
    self, message: str, conversation_history: list[dict[str, str]] | None = None
) -> Generator[str, None, None]:
    """Yields chunks of generated response text."""
    pass
```

### Provider Implementations

- **Ollama**: Streams via `stream=True` parameter
- **OpenAI**: Uses streaming API with delta content
- **Claude**: Uses Anthropic streaming API with context manager
- **HuggingFace**: Falls back to full response (no native streaming)

### Flask Application

**File**: `src/api.py`

Socket.IO events:
- `connect`: Client connection confirmation
- `disconnect`: Client disconnection
- `chat_message`: Main streaming handler

**Flow**:
1. Client connects, receives `connected` event
2. Client sends `chat_message` with query
3. Server creates/retrieves session, stores message
4. Streams response via `chat_chunk` events
5. Stores complete response
6. Sends `chat_complete` event with session ID
7. Errors handled via `error` event

## Frontend (React/TypeScript)

### Dependencies
- `socket.io-client` (v4.8.1)

### Socket Service

**File**: `src/services/socket.ts`

`SocketService` class manages:
- Connection/disconnection
- Event emission and listening
- Connection state

**Key Methods**:
- `connect()`: Establish connection
- `sendMessage(data)`: Send chat message
- `onChatChunk(callback)`: Listen for chunks
- `onChatComplete(callback)`: Listen for completion
- `onError(callback)`: Listen for errors

### ChatBot Component

**File**: `src/components/chat/ChatBot.tsx`

Replaced HTTP calls with Socket.IO streaming:
- `useEffect` manages socket lifecycle
- Accumulates chunks in ref
- Real-time UI updates
- Typing indicator during streaming

**Flow**:
1. User submits message
2. Add message to UI, show typing indicator
3. Send via Socket.IO
4. Receive chunks, update in real-time
5. On completion, hide indicator, play sound

## Socket.IO Events

**Client to Server**:
- `chat_message`: Send chat message with context

**Server to Client**:
- `connected`: Connection confirmation
- `chat_chunk`: LLM response token
- `chat_complete`: Response done with full text and session ID
- `error`: Error message

## Testing

### Test Script

**File**: `test_streaming.py`

Standalone script that:
- Connects to Socket.IO server
- Sends test message
- Receives and displays chunks
- Prints statistics

### Running

```bash
# Backend
cd packages/server && poetry run python -m src.api

# Frontend
cd packages/client && bun run dev

# Access: http://localhost:5173
```

## Key Features

1. **Real-time Streaming**: Tokens appear as generated
2. **Conversation History**: Session management preserves context
3. **Error Handling**: Graceful errors with user-friendly messages
4. **Connection Management**: Auto-reconnection and state tracking
5. **Multiple LLM Support**: Ollama, OpenAI, Claude, HuggingFace

## Database Integration

- User messages stored before streaming
- Assistant responses stored after completion
- Session management for continuity
- Metadata includes RAG type and chunk count

## Performance

- Immediate streaming from LLM
- No server-side buffering
- Efficient client-side accumulation with refs
- Minimal re-renders

## Future Enhancements

1. Progress indicators (tokens/sec, time remaining)
2. Request cancellation
3. Retry logic for failed connections
4. Message queuing for offline scenarios
5. Multi-user typing indicators
6. RAG context streaming

## Compatibility

- **Python**: 3.11+
- **Node**: Bun runtime compatible
- **Browsers**: Modern browsers with WebSocket support
- **Transport**: WebSocket primary, polling fallback
