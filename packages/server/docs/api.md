# InsightHub Flask REST API

A loosely coupled REST API for document upload and chat interactions with the RAG system.

## Quick Start

### Start the Server

```bash
# Using Make
make server

# Or directly with Poetry
poetry run python src/api.py
```

The server will start on `http://localhost:5000` (configurable via `.env`).

### Check Server Health

```bash
# Using Make
make health

# Or using curl
curl http://localhost:5000/health
curl http://localhost:5000/heartbeat
```

## API Endpoints

### Health Endpoints

#### GET /heartbeat
Simple heartbeat endpoint that returns 200 OK.

**Response**: Empty (200 OK)

#### GET /health
Health check with status information.

**Response**:
```json
{
  "status": "healthy"
}
```

### Document Management

#### POST /api/upload
Upload a document (PDF or TXT) to the system.

**Request**: `multipart/form-data` with `file` field

**Response**:
```json
{
  "message": "Document uploaded successfully",
  "document": {
    "id": 1,
    "filename": "example.txt",
    "text_length": 830,
    "type": "txt"
  }
}
```

#### GET /api/documents
List all uploaded documents.

**Response**:
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "example.txt",
      "text_length": 830,
      "type": "txt"
    }
  ],
  "count": 1
}
```

#### DELETE /api/documents/:id
Delete a document by ID.

**Response**:
```json
{
  "message": "Document deleted successfully"
}
```

### Chat

#### POST /api/chat
Send a chat message and get a response from the RAG system.

**Request**:
```json
{
  "message": "What is InsightHub?",
  "conversation_id": "optional-id"
}
```

**Response**:
```json
{
  "answer": "InsightHub is a dual RAG system...",
  "context": [
    {
      "text": "Sample context chunk",
      "score": 0.85,
      "metadata": {"source": "document_1"}
    }
  ],
  "conversation_id": "optional-id",
  "documents_count": 1
}
```

## Configuration

Configuration is managed through environment variables in `.env`:

```bash
# Flask API Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

See `.env.example` for all available options.

## CLI Tool

A direct CLI interface is available for testing without HTTP:

```bash
# Upload a document
make cli ARGS="upload test_document.txt"

# Send a chat message
make cli ARGS="chat 'What is InsightHub?' --show-context"

# List documents
make cli ARGS="list"

# Delete a document
make cli ARGS="delete 1"

# Interactive session
make cli ARGS="interactive"
```

The CLI bypasses the REST API and interacts directly with the RAG system.

## Client Integration

The React client uses the API service at `packages/client/src/services/api.ts`:

```typescript
import apiService from '@/services/api';

// Upload document
await apiService.uploadDocument(file);

// Send chat message
const response = await apiService.sendChatMessage({
  message: "Hello",
  conversation_id: "session-123"
});
```

Configure the API URL in `packages/client/.env`:
```
VITE_API_URL=http://localhost:5000
```

## Architecture

The API is designed to be loosely coupled with the RAG system:

- **api.py**: Flask REST endpoints
- **cli.py**: Direct CLI interface (no HTTP)
- **TODO**: RAG system integration (currently using mock responses)

The API currently stores documents in memory. Future integration with the RAG system will add:
- Vector/Graph RAG implementations
- Embedding generation
- Similarity search
- LLM-based answer generation
