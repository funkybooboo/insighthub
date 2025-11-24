# InsightHub Flask REST API Documentation

Complete REST API for the InsightHub dual RAG system with Flask 3.0+, featuring document management, chat functionality, and real-time WebSocket communication.

## Quick Start

### Start the Server

```bash
# Using Task commands
task server

# Or directly with Poetry
poetry run python src/api.py

# Check server health
curl http://localhost:5000/health
```

The server will start on `http://localhost:5000` by default (configurable via `.env`).

## Base URL Structure

All API endpoints are prefixed with `/api/`:

```
http://localhost:5000/api/{endpoint}
```

## Authentication

All protected endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### POST /api/auth/register
Register a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe" // Optional
}
```

**Response** (201 Created):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-11-24T10:30:00Z"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid email format, weak password
- `409 Conflict`: Email already exists

### POST /api/auth/login
Authenticate user and receive JWT token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `400 Bad Request`: Missing required fields

### POST /api/auth/logout
Invalidate JWT token and logout user.

**Request**:
```json
{}
```

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

### GET /api/auth/me
Get current user profile information.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "theme_preference": "dark",
    "created_at": "2025-11-24T10:30:00Z"
  }
}
```

## Workspaces

### GET /api/workspaces
List all workspaces for the authenticated user.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "workspaces": [
    {
      "id": 1,
      "name": "Research Papers",
      "description": "Academic research papers",
      "rag_config": {
        "rag_type": "vector",
        "embedding_model": "nomic-embed-text",
        "top_k": 8
      },
      "created_at": "2025-11-24T10:30:00Z",
      "updated_at": "2025-11-24T10:30:00Z"
    }
  ]
}
```

### POST /api/workspaces
Create a new workspace.

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "name": "New Project",
  "description": "My new research project",
  "rag_config": {
    "rag_type": "vector",
    "embedding_model": "nomic-embed-text",
    "chunking_strategy": "sentence",
    "top_k": 8
  }
}
```

**Response** (201 Created):
```json
{
  "workspace": {
    "id": 2,
    "name": "New Project",
    "description": "My new research project",
    "rag_config": {
      "rag_type": "vector",
      "embedding_model": "nomic-embed-text",
      "chunking_strategy": "sentence",
      "top_k": 8
    },
    "created_at": "2025-11-24T10:30:00Z"
  }
}
```

### GET /api/workspaces/{workspace_id}
Get details for a specific workspace.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "workspace": {
    "id": 1,
    "name": "Research Papers",
    "description": "Academic research papers",
    "rag_config": {
      "rag_type": "vector",
      "embedding_model": "nomic-embed-text",
      "top_k": 8
    },
    "document_count": 5,
    "session_count": 12,
    "created_at": "2025-11-24T10:30:00Z",
    "updated_at": "2025-11-24T10:30:00Z"
  }
}
```

### PUT /api/workspaces/{workspace_id}
Update workspace details.

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Response** (200 OK):
```json
{
  "workspace": {
    "id": 1,
    "name": "Updated Project Name",
    "description": "Updated description",
    "rag_config": {
      "rag_type": "vector",
      "embedding_model": "nomic-embed-text",
      "top_k": 8
    },
    "updated_at": "2025-11-24T11:00:00Z"
  }
}
```

### DELETE /api/workspaces/{workspace_id}
Delete a workspace.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "Workspace deleted successfully"
}
```

## Documents

### GET /api/workspaces/{workspace_id}/documents
List all documents in a workspace.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "documents": [
    {
      "id": "doc_123",
      "filename": "research_paper.pdf",
      "content_type": "application/pdf",
      "file_size": 2048576,
      "status": "ready",
      "metadata": {
        "page_count": 15,
        "chunk_count": 42
      },
      "created_at": "2025-11-24T10:30:00Z",
      "updated_at": "2025-11-24T10:30:00Z"
    }
  ],
  "count": 1
}
```

### POST /api/workspaces/{workspace_id}/documents
Upload a document to the workspace.

**Headers**: `Authorization: Bearer <token>`

**Request**: `multipart/form-data`
```
file: [binary file data]
```

**Response** (202 Accepted):
```json
{
  "message": "Document upload initiated",
  "document": {
    "id": "doc_124",
    "filename": "research_paper.pdf",
    "content_type": "application/pdf",
    "file_size": 2048576,
    "status": "pending"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid file type, file too large
- `413 Payload Too Large`: File exceeds size limit

### GET /api/workspaces/{workspace_id}/documents/{document_id}/status
Get processing status of a document.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "document": {
    "id": "doc_124",
    "filename": "research_paper.pdf",
    "status": "processing",
    "progress": 65,
    "current_step": "chunking",
    "metadata": {
      "pages_processed": 10,
      "chunks_created": 25
    }
  }
}
```

**Status Values**:
- `pending`: Upload received, waiting to process
- `parsing`: Extracting text from document
- `chunking`: Splitting text into chunks
- `embedding`: Generating vector embeddings
- `indexing`: Storing in vector database
- `ready`: Processing complete, ready for queries
- `failed`: Processing failed with error

### DELETE /api/workspaces/{workspace_id}/documents/{document_id}
Delete a document from workspace.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "Document deleted successfully"
}
```

## Chat Sessions

### GET /api/workspaces/{workspace_id}/sessions
List all chat sessions in a workspace.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "sessions": [
    {
      "id": "session_123",
      "title": "RAG System Questions",
      "created_at": "2025-11-24T10:30:00Z",
      "updated_at": "2025-11-24T10:30:00Z",
      "message_count": 8
    }
  ],
  "count": 1
}
```

### POST /api/workspaces/{workspace_id}/sessions
Create a new chat session.

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "title": "New Chat Session"
}
```

**Response** (201 Created):
```json
{
  "session": {
    "id": "session_124",
    "title": "New Chat Session",
    "created_at": "2025-11-24T10:30:00Z"
  }
}
```

### GET /api/sessions/{session_id}/messages
Get message history for a chat session.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "messages": [
    {
      "id": "msg_456",
      "session_id": "session_123",
      "role": "user",
      "content": "What is RAG?",
      "created_at": "2025-11-24T10:30:00Z"
    },
    {
      "id": "msg_457",
      "session_id": "session_123",
      "role": "assistant",
      "content": "RAG stands for Retrieval-Augmented Generation...",
      "metadata": {
        "sources": [
          {
            "document_id": "doc_123",
            "chunk_id": "chunk_45",
            "score": 0.89
          }
        ]
      },
      "created_at": "2025-11-24T10:30:00Z"
    }
  ],
  "count": 2
}
```

### POST /api/sessions/{session_id}/messages
Send a message to a chat session.

**Headers**: `Authorization: Bearer <token>`

**Request**:
```json
{
  "content": "How does vector RAG work?",
  "rag_mode": "vector" // "vector", "graph", or "hybrid"
}
```

**Response** (202 Accepted):
```json
{
  "message": "Message received, processing started",
  "message_id": "msg_458"
}
```

The actual response will be streamed via WebSocket events.

### DELETE /api/sessions/{session_id}
Delete a chat session.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "Session deleted successfully"
}
```

## WebSocket Events

Real-time communication is handled via Socket.IO at `ws://localhost:5000`.

### Connection

**Client to Server**:
```typescript
socket.emit('join_session', { session_id: 'session_123' });
```

**Server to Client**:
```typescript
socket.on('session_joined', (data) => {
  console.log('Joined session:', data.session_id);
});
```

### Chat Events

**Client to Server**:
```typescript
socket.emit('chat_message', {
  session_id: 'session_123',
  content: 'What is RAG?',
  rag_mode: 'vector'
});
```

**Server to Client**:
```typescript
// Streaming response chunks
socket.on('chat_chunk', (data) => {
  console.log('Chunk:', data.chunk);
  // Append to message
});

// Response complete
socket.on('chat_complete', (data) => {
  console.log('Complete:', data.message);
  console.log('Sources:', data.sources);
});

// Error handling
socket.on('chat_error', (data) => {
  console.error('Chat error:', data.error);
});
```

### Document Status Events

**Server to Client**:
```typescript
socket.on('document_status', (data) => {
  console.log('Document status:', data.document_id, data.status);
  
  // Update UI based on status
  switch (data.status) {
    case 'pending':
      // Show upload spinner
      break;
    case 'processing':
      // Show progress bar
      break;
    case 'ready':
      // Enable chat functionality
      break;
    case 'failed':
      // Show error message
      break;
  }
});
```

## Configuration

### Environment Variables

Configuration is managed through environment variables in `.env`:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/insighthub

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Vector Database Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_PREFIX=insighthub

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
```

### CORS Configuration

CORS is configured for frontend development:

```python
# In Flask app
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    }
  },
  "request_id": "req_123"
}
```

### Error Types

- `ValidationError`: Invalid input data
- `AuthenticationError`: Invalid or missing credentials
- `AuthorizationError`: User not authorized for resource
- `NotFoundError`: Resource not found
- `ProcessingError`: Document or chat processing failed
- `RateLimitError`: Too many requests
- `ExternalServiceError`: LLM or database service unavailable

## Rate Limiting

API endpoints implement rate limiting:

```python
# Rate limit: 100 requests per minute per user
@app.before_request
def rate_limit():
    # Check user request rate
    if rate_exceeded:
        return jsonify({
            "error": {
                "type": "RateLimitError",
                "message": "Rate limit exceeded"
            }
        }), 429
```

## Health Endpoints

### GET /health

Basic health check.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T10:30:00Z",
  "version": "1.0.0"
}
```

### GET /heartbeat

Lightweight heartbeat for monitoring.

**Response** (200 OK):
```json
{
  "status": "ok",
  "timestamp": "2025-11-24T10:30:00Z"
}
```

## Client Integration

The React 19 client integrates with this API via the service layer:

```typescript
// packages/client/src/services/api.ts
class ApiService {
  private baseUrl = 'http://localhost:5000/api';

  async uploadDocument(file: File, workspaceId: string) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.baseUrl}/workspaces/${workspaceId}/documents`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.getToken()}`,
      },
      body: formData,
    });

    return response.json();
  }

  async sendMessage(sessionId: string, content: string, ragMode: string) {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionId}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.getToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content, rag_mode }),
    });

    return response.json();
  }
}
```

## Architecture Notes

The Flask API follows clean architecture principles:

- **Domains**: Business logic separated by feature (`auth`, `chat`, `documents`, `health`)
- **Infrastructure**: External integrations (`database`, `rag`, `storage`, `llm`)
- **Middleware**: Cross-cutting concerns (CORS, authentication, rate limiting)
- **WebSocket**: Real-time communication via Flask-SocketIO
- **Testing**: Comprehensive unit and integration tests

This API provides the foundation for the InsightHub dual RAG system with proper error handling, authentication, and real-time capabilities.