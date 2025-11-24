# Low-Level Design Document

## 1. Database Schema

### 1.1 PostgreSQL Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workspaces table
CREATE TABLE workspaces (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RAG Configurations table
CREATE TABLE rag_configs (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER UNIQUE REFERENCES workspaces(id) ON DELETE CASCADE,
    rag_type VARCHAR(50) DEFAULT 'vector', -- 'vector', 'graph', 'hybrid'
    chunking_strategy VARCHAR(50) DEFAULT 'sentence',
    embedding_model VARCHAR(255) DEFAULT 'nomic-embed-text',
    embedding_dim INTEGER DEFAULT 768,
    top_k INTEGER DEFAULT 8,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    content_type VARCHAR(100),
    file_size BIGINT,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'indexed', 'failed'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat Sessions table
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER REFERENCES workspaces(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat Messages table
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}', -- sources, citations, timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_workspaces_user_id ON workspaces(user_id);
CREATE INDEX idx_documents_workspace_id ON documents(workspace_id);
CREATE INDEX idx_chat_sessions_workspace_id ON chat_sessions(workspace_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_documents_status ON documents(status);
```

### 1.2 Vector Database Schema (Qdrant)

```yaml
Collection: documents_{workspace_id}
  Vectors:
    size: 768  # Matches embedding dimension
    distance: Cosine
  Payload Schema:
    document_id: integer
    chunk_id: string
    text: string
    metadata:
      filename: string
      page: integer (optional)
      position: integer
      token_count: integer
      workspace_id: integer
```

### 1.3 Graph Database Schema (Neo4j)

```cypher
// Node Types
(:Entity {
  id: string,
  name: string,
  type: string,  // 'PERSON', 'ORGANIZATION', 'CONCEPT', etc.
  workspace_id: integer,
  document_id: integer,
  properties: map
})

(:Chunk {
  id: string,
  document_id: integer,
  workspace_id: integer,
  text: string,
  position: integer
})

// Relationship Types
(:Entity)-[:RELATED_TO {
  type: string,
  confidence: float,
  source_chunk_id: string,
  workspace_id: integer
}]->(:Entity)

(:Chunk)-[:MENTIONS]->(:Entity)
(:Chunk)-[:NEXT]->(:Chunk)
(:Entity)-[:CO_OCCURS_WITH {
  workspace_id: integer
}]->(:Entity)
```

## 2. API Specifications

### 2.1 REST Endpoints

#### Authentication

```
POST /api/auth/register
  Request: { email, password }
  Response: { user: { id, email }, token }

POST /api/auth/login
  Request: { email, password }
  Response: { user: { id, email }, token }

POST /api/auth/logout
  Response: { success: true }

GET /api/auth/me
  Headers: Authorization: Bearer <token>
  Response: { user: { id, email } }
```

#### Workspaces

```
GET /api/workspaces
  Response: { workspaces: [...] }

POST /api/workspaces
  Request: { name, description? }
  Response: { workspace: {...} }

GET /api/workspaces/:id
  Response: { workspace: {...}, rag_config: {...} }

PUT /api/workspaces/:id
  Request: { name?, description? }
  Response: { workspace: {...} }

DELETE /api/workspaces/:id
  Response: { success: true }
```

#### Documents

```
GET /api/workspaces/:workspace_id/documents
  Response: { documents: [...] }

POST /api/workspaces/:workspace_id/documents
  Content-Type: multipart/form-data
  Request: { file, metadata? }
  Response: { document: {...}, status: 'pending' }

DELETE /api/workspaces/:workspace_id/documents/:id
  Response: { success: true }

GET /api/workspaces/:workspace_id/documents/:id/status
  Response: { status, progress?, error? }
```

#### RAG Configuration

```
GET /api/workspaces/:workspace_id/rag-config
  Response: { config: {...} }

PUT /api/workspaces/:workspace_id/rag-config
  Request: { rag_type?, chunking_strategy?, embedding_model?, top_k? }
  Response: { config: {...} }
```

#### Chat Sessions

```
GET /api/workspaces/:workspace_id/sessions
  Response: { sessions: [...] }

POST /api/workspaces/:workspace_id/sessions
  Request: { title? }
  Response: { session: {...} }

GET /api/sessions/:id/messages
  Response: { messages: [...] }

DELETE /api/sessions/:id
  Response: { success: true }
```

### 2.2 WebSocket Events

#### Client to Server

```typescript
// Join a chat session
socket.emit('join_session', { session_id: number })

// Send a chat message
socket.emit('chat_message', {
  session_id: number,
  content: string,
  rag_mode?: 'vector' | 'graph' | 'hybrid'
})

// Leave a session
socket.emit('leave_session', { session_id: number })
```

#### Server to Client

```typescript
// Streaming response chunk
socket.on('chat_chunk', {
  session_id: number,
  chunk: string,
  index: number
})

// Response complete
socket.on('chat_complete', {
  session_id: number,
  message_id: number,
  sources: Array<{
    document_id: number,
    chunk_id: string,
    text: string,
    score: number
  }>
})

// Error occurred
socket.on('chat_error', {
  session_id: number,
  error: string
})

// Document processing status update
socket.on('document_status', {
  document_id: number,
  status: string,
  progress?: number
})
```

## 3. Class Diagrams

### 3.1 Server Domain Classes

```
+------------------+
|     Service      |
+------------------+
        ^
        |
+-------+--------+-------+-------+
|       |        |       |       |
v       v        v       v       v
+------+ +------+ +-----+ +-----+ +------+
|Auth  | |Chat  | |Doc  | |User | |Health|
|Svc   | |Svc   | |Svc  | |Svc  | |Svc   |
+------+ +------+ +-----+ +-----+ +------+
    |        |       |       |
    v        v       v       v
+------+ +------+ +-----+ +-----+
|Auth  | |Chat  | |Doc  | |User |
|Repo  | |Repo  | |Repo | |Repo |
+------+ +------+ +-----+ +-----+
```

### 3.2 RAG Component Classes

```
+------------------+       +------------------+
|  DocumentParser  |       |     Chunker      |
+------------------+       +------------------+
| +parse(bytes)    |       | +chunk(doc)      |
+------------------+       +------------------+
        |                          |
        v                          v
+------------------+       +------------------+
|EmbeddingEncoder  |       |   VectorIndex    |
+------------------+       +------------------+
| +encode(texts)   |       | +upsert(id,vec)  |
| +encode_one(text)|       | +search(vec,k)   |
+------------------+       +------------------+
                                   |
                                   v
                           +------------------+
                           |  VectorRetriever |
                           +------------------+
                           | +retrieve(vec,k) |
                           +------------------+
                                   |
                                   v
+------------------+       +------------------+
|     Ranker       |       | ContextBuilder   |
+------------------+       +------------------+
| +rerank(results) |       | +build(results)  |
+------------------+       +------------------+
                                   |
                                   v
                           +------------------+
                           |       LLM        |
                           +------------------+
                           | +generate(prompt)|
                           | +stream(prompt)  |
                           +------------------+
```

### 3.3 Graph RAG Components

```
+------------------+       +------------------+
| EntityExtractor  |       |RelationExtractor |
+------------------+       +------------------+
| +extract(text)   |       | +extract(text)   |
+------------------+       +------------------+
        |                          |
        v                          v
                +------------------+
                |  GraphBuilder    |
                +------------------+
                | +build_nodes()   |
                | +build_edges()   |
                +------------------+
                          |
                          v
                +------------------+
                |   GraphStore     |
                +------------------+
                | +add_nodes()     |
                | +add_edges()     |
                | +query_neighbors()|
                | +query_subgraph()|
                +------------------+
                          |
                          v
                +------------------+
                | GraphRetriever   |
                +------------------+
                | +retrieve_by_seed|
                | +retrieve_by_query|
                +------------------+
```

## 4. Sequence Diagrams

### 4.1 Document Upload Sequence

```
Client          Server          Filesystem      PostgreSQL      RabbitMQ
  |               |               |                 |               |
  |--POST /doc--->|               |                 |               |
  |               |--store file-->|                 |               |
  |               |<--file_path---|                 |               |
  |               |               |--INSERT doc---->|               |
  |               |               |                 |<--doc_id------|
  |               |--publish event------------------>|               |
  |               |               |                 |               |
  |<--202 Accepted|               |                 |               |
  |               |               |                 |               |

Parser          Chunker         Embedder        Indexer         Connector
  |<--document.uploaded------------------------------------------|
  |--parse----->|               |               |               |
  |             |<--document.parsed-----------------------------|
  |             |--chunk------->|               |               |
  |             |               |<--document.chunked------------|
  |             |               |--embed------->|               |
  |             |               |               |<--embedding.created-|
  |             |               |               |--index to Qdrant-->|
  |             |               |               |               |--build graph->|
```

### 4.2 Chat Query Sequence

```
Client          Socket.IO       ChatService     RAGEngine       LLM
  |               |               |               |               |
  |--chat_message->|               |               |               |
  |               |--process------>|               |               |
  |               |               |--encode query->|               |
  |               |               |--retrieve----->|               |
  |               |               |<--chunks-------|               |
  |               |               |--build context->|               |
  |               |               |               |--generate---->|
  |               |               |               |<--token stream-|
  |               |<--chat_chunk---|               |               |
  |<--chat_chunk--|               |               |               |
  |               |               |               |<--complete----|
  |               |<--chat_complete|               |               |
  |<--chat_complete|               |               |               |
```

## 5. Worker Implementation Details

### 5.1 Worker Base Pattern

```python
from abc import ABC, abstractmethod
import pika
import json
import logging
from typing import Dict, Any

class BaseWorker(ABC):
    def __init__(self, queue_name: str, exchange: str = 'documents'):
        self.queue_name = queue_name
        self.exchange = exchange
        self.connection = None
        self.channel = None
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establish connection to RabbitMQ"""
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST', 'localhost'),
                port=int(os.getenv('RABBITMQ_PORT', 5672)),
                credentials=pika.PlainCredentials(
                    os.getenv('RABBITMQ_USER', 'guest'),
                    os.getenv('RABBITMQ_PASS', 'guest')
                )
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.channel.queue_bind(
            exchange=self.exchange,
            queue=self.queue_name,
            routing_key=self.queue_name
        )

    def consume(self):
        """Start consuming messages from queue"""
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self.process_message,
            auto_ack=False
        )
        self.logger.info(f"Worker {self.__class__.__name__} started consuming")
        self.channel.start_consuming()

    def process_message(self, channel, method, properties, body):
        """Process incoming message"""
        try:
            event = json.loads(body)
            self.logger.info(f"Processing event: {event.get('event_type')}")
            result = self.handle(event)
            self.publish_result(result)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            self.handle_error(e, event)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    @abstractmethod
    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the specific event type"""
        pass

    def publish_result(self, result: Dict[str, Any]):
        """Publish result to next queue"""
        # Implementation depends on specific worker
        pass

    def handle_error(self, error: Exception, event: Dict[str, Any]):
        """Handle processing errors"""
        # Log error and potentially update document status
        pass
```

### 5.2 Parser Worker

```python
class ParserWorker(BaseWorker):
    def __init__(self):
        super().__init__(queue_name='parser_queue')
        self.parsers = {
            'application/pdf': PDFParser(),
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DocxParser(),
            'text/html': HTMLParser(),
            'text/plain': TextParser(),
        }

    def handle(self, event: dict) -> dict:
        document_id = event['document_id']
        file_path = event['file_path']
        content_type = event['content_type']

        # Read file from filesystem
        with open(file_path, 'rb') as f:
            file_bytes = f.read()

        # Parse based on content type
        parser = self.parsers.get(content_type, TextParser())
        text = parser.parse(file_bytes)

        return {
            'event_type': 'document.parsed',
            'document_id': document_id,
            'text': text,
            'metadata': {
                'char_count': len(text),
                'content_type': content_type
            }
        }
```

### 5.3 Embedder Worker

```python
class EmbedderWorker(BaseWorker):
    def __init__(self):
        super().__init__(queue_name='embedder_queue')
        self.encoder = OllamaEmbeddingEncoder(
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            model=os.getenv('OLLAMA_EMBEDDING_MODEL', 'nomic-embed-text')
        )

    def handle(self, event: dict) -> dict:
        document_id = event['document_id']
        chunks = event['chunks']

        # Batch encode chunks
        texts = [chunk['text'] for chunk in chunks]
        vectors = self.encoder.encode(texts)

        # Attach vectors to chunks
        embedded_chunks = []
        for chunk, vector in zip(chunks, vectors):
            embedded_chunks.append({
                **chunk,
                'vector': vector
            })

        return {
            'event_type': 'embedding.created',
            'document_id': document_id,
            'chunks': embedded_chunks
        }
```

## 6. Error Handling

### 6.1 Error Types

```python
class InsightHubError(Exception):
    """Base exception for all InsightHub errors"""
    pass

class ValidationError(InsightHubError):
    """Invalid input data"""
    pass

class NotFoundError(InsightHubError):
    """Resource not found"""
    pass

class AuthenticationError(InsightHubError):
    """Authentication failed"""
    pass

class AuthorizationError(InsightHubError):
    """User not authorized for this action"""
    pass

class RateLimitError(InsightHubError):
    """Rate limit exceeded"""
    pass

class ExternalServiceError(InsightHubError):
    """External service (LLM, DB) failed"""
    pass

class ProcessingError(InsightHubError):
    """Document/query processing failed"""
    pass
```

### 6.2 Error Response Format

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Invalid email format",
    "details": {
      "field": "email",
      "value": "invalid-email"
    },
    "request_id": "abc123"
  }
}
```

## 7. Configuration Schema

### 7.1 Environment Variables

```bash
# Server
FLASK_ENV=development|production
SECRET_KEY=<random-string>
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# Storage
STORAGE_TYPE=filesystem
STORAGE_PATH=/app/uploads

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Graph Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:1b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Optional: Cloud LLMs
OPENAI_API_KEY=<key>
ANTHROPIC_API_KEY=<key>
```

### 7.2 RAG Configuration Options

```yaml
chunking_strategies:
  - sentence    # Split on sentence boundaries
  - paragraph   # Split on paragraph boundaries
  - recursive   # Recursive text splitting
  - fixed       # Fixed character count

embedding_models:
  - nomic-embed-text    # Ollama default
  - all-minilm          # SentenceTransformers
  - text-embedding-3-small  # OpenAI

rag_types:
  - vector   # Pure vector similarity search
  - graph    # Graph traversal + entity matching
  - hybrid   # Combined vector + graph retrieval
```

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# Test chunker
def test_sentence_chunker():
    from server.infrastructure.rag.chunking.sentence import SentenceChunker
    
    chunker = SentenceChunker(max_chunk_size=100)
    doc = Document(id="1", content="First sentence. Second sentence.")
    chunks = chunker.chunk(doc)
    assert len(chunks) == 2
    assert chunks[0].text == "First sentence."

# Test embedding encoder (with dummy)
def test_embedding_encoder():
    from server.infrastructure.rag.embeddings.dummy import DummyEmbeddingModel
    
    encoder = DummyEmbeddingModel(dimension=768)
    vectors = encoder.encode(["hello", "world"])
    assert len(vectors) == 2
    assert len(vectors[0]) == 768
```

### 8.2 Integration Tests

```python
# Test full RAG pipeline with testcontainers
import pytest
from testcontainers.qdrant import QdrantContainer

@pytest.fixture
def qdrant_container():
    with QdrantContainer("qdrant/qdrant:latest") as qdrant:
        yield qdrant

def test_rag_pipeline(qdrant_container):
    from server.infrastructure.rag.vector_rag import VectorRag
    from server.infrastructure.rag.embeddings.ollama import OllamaEmbeddingModel
    from server.infrastructure.rag.vector_stores.qdrant_store import QdrantVectorStore
    from server.infrastructure.rag.chunking.sentence import SentenceChunker
    
    # Setup
    rag = VectorRag(
        embedder=OllamaEmbeddingModel(),
        vector_store=QdrantVectorStore(
            host=qdrant_container.get_container_host_ip(),
            port=qdrant_container.get_exposed_port(6333)
        ),
        chunker=SentenceChunker()
    )

    # Index document
    rag.add_documents([{"content": "The sky is blue."}])

    # Query
    result = rag.query("What color is the sky?")
    assert "blue" in result['answer'].lower()
```

## 9. Performance Optimizations

### 9.1 Caching Strategy

| Data | Cache Type | TTL | Invalidation |
|------|-----------|-----|--------------|
| User sessions | Redis | 24h | On logout |
| Embeddings | Redis | 1h | On document delete |
| RAG configs | In-memory | 5m | On config update |
| Rate limits | Redis | 1m | Rolling window |

### 9.2 Batch Processing

```python
# Batch embedding generation
def embed_documents(documents: list[Document], batch_size: int = 32):
    all_chunks = []
    for doc in documents:
        chunks = chunker.chunk(doc)
        all_chunks.extend(chunks)

    # Process in batches
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        texts = [c.text for c in batch]
        vectors = encoder.encode(texts)

        # Batch upsert to Qdrant
        vector_store.upsert_many([
            (c.id, v, c.metadata)
            for c, v in zip(batch, vectors)
        ])
```

### 9.3 Connection Pooling

```python
# SQLAlchemy connection pool
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

# Redis connection pool
import redis

redis_pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    max_connections=50
)
redis_client = redis.Redis(connection_pool=redis_pool)
```

## 10. Security Implementation

### 10.1 JWT Authentication

```python
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def generate_token(self, user_id: int, email: str) -> str:
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
```

### 10.2 Input Validation

```python
from marshmallow import Schema, fields, validate, ValidationError

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

class DocumentUploadSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(max=255))
    content = fields.Str(required=True)
    metadata = fields.Dict(missing={})

def validate_input(schema_class, data):
    try:
        schema = schema_class()
        return schema.load(data)
    except ValidationError as e:
        raise ValidationError(f"Validation error: {e.messages}")
```

This low-level design provides the detailed implementation specifications for building the InsightHub dual RAG system with Flask, React, and modern AI technologies.