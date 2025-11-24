# InsightHub

A dual RAG system comparing Vector RAG and Graph RAG for academic research paper analysis.

## Features

* Vector RAG with document chunking, embedding, and retrieval
* Real-time streaming via Socket.IO WebSocket
* Fully local (Ollama + Qdrant + PostgreSQL)
* React frontend with chat interface
* Modular architecture with pluggable components
* Multiple LLM providers (Ollama, OpenAI, Claude, HuggingFace)
* CLI and REST API interfaces
* **Full application and infrastructure monitoring via ELK (Elasticsearch, Logstash, Kibana)**

## Client-Side Features (React Frontend)

The InsightHub client application provides a rich and interactive user experience with the following key features:

*   **User Management**: Secure login, signup, user profile updates, and theme preference settings.
*   **Default RAG Configuration**: Users can define and manage their preferred default RAG settings (Vector or Graph RAG, embedding models, chunking parameters, reranking) which can be inherited by new workspaces.
*   **Workspace Management**:
    *   **Creation**: Create new workspaces with customizable RAG configurations (or use defaults). Real-time feedback on provisioning status. Concurrent creation of multiple workspaces is supported.
    *   **Selection**: Easily switch between active workspaces.
    *   **Details**: View workspace metadata, associated documents, and chat sessions.
    *   **Editing**: Update workspace name and description. RAG configuration is locked once a workspace is active.
    *   **Deletion**: Initiate asynchronous workspace deletion with real-time status updates and UI locking for the deleting workspace.
    *   **Status Indicators**: Visual cues for workspace status (provisioning, ready, failed, deleting).
*   **Chat Session Management**: Create, select, and delete individual chat sessions within an active workspace.
*   **Document Management**:
    *   **Upload**: Upload PDF and text documents to the active workspace. Supports concurrent uploads across different workspaces.
    *   **Listing**: View a list of uploaded documents with their processing status.
    *   **Deletion**: Remove documents from a workspace.
    *   **Real-time Processing Status**: Live updates on document parsing, chunking, embedding, and indexing progress, displayed in the dedicated "Documents" column.
*   **Interactive Chat Interface**:
    *   **Streaming Responses**: Receive token-by-token LLM responses.
    *   **RAG Context Display**: View the source documents/chunks used by the RAG system for bot responses.
    *   **Chat Locking**: Chat input is automatically disabled if the active workspace is provisioning, deleting, or has documents undergoing processing.
*   **Intelligent RAG Enhancement Prompt**:
    *   When the RAG system finds insufficient context for a query, the client presents options to improve knowledge:
        *   **Upload a Document**: Directs the user to add more relevant files.
        *   **Fetch from Wikipedia**: Triggers a backend process to search and inject relevant Wikipedia content. Status of this fetch is visible in the "Documents" column.
        *   **Continue without additional context**: Allows the user to proceed with the LLM without RAG augmentation.
    *   If RAG enhancement is chosen, the chat pauses, the relevant job proceeds, and the original query is automatically retried once the new context is processed.
*   **Responsive Layout**: Optimized for various screen sizes with a clear 3-column structure (Workspaces, Chat Sessions, Main Chat, Documents).
*   **Visual & Audio Feedback**: Theme switching (light/dark), pop/notification sounds for interactions, and error messages.

## Client API Dependencies

The InsightHub client application interacts with the backend primarily through a REST API and real-time WebSocket communication. Below is a summary of the key endpoints and events the client relies on and expects from the server.

### REST API Endpoints

The client uses the following HTTP REST API endpoints:

*   **Authentication & User Management**:
    *   `POST /api/auth/signup`: User registration.
    *   `POST /api/auth/login`: User login, returns JWT.
    *   `POST /api/auth/logout`: User logout.
    *   `GET /api/auth/me`: Get current user's profile.
    *   `PATCH /api/auth/preferences`: Update user preferences (e.g., theme).
    *   `PATCH /api/auth/profile`: Update user profile details.
    *   `POST /api/auth/change-password`: Change user's password.
    *   `GET /api/auth/default-rag-config`: Get user's default RAG configuration.
    *   `PUT /api/auth/default-rag-config`: Save user's default RAG configuration.

*   **Workspace Management**:
    *   `GET /api/workspaces`: List all workspaces for the authenticated user.
    *   `GET /api/workspaces/{workspaceId}`: Get details for a specific workspace.
    *   `POST /api/workspaces`: Create a new workspace, optionally with initial RAG configuration.
    *   `PATCH /api/workspaces/{workspaceId}`: Update basic workspace details (name, description).
    *   `DELETE /api/workspaces/{workspaceId}`: Delete a workspace and its associated resources.
    *   `GET /api/workspaces/{workspaceId}/rag-config`: Get the RAG configuration for a specific workspace.
    *   `POST /api/workspaces/{workspaceId}/rag-config`: Create RAG configuration for a workspace.
    *   `PATCH /api/workspaces/{workspaceId}/rag-config`: Update RAG configuration for a workspace.

*   **Document Management**:
    *   `POST /api/workspaces/{workspaceId}/documents/upload`: Upload a document to a specified workspace.
    *   `GET /api/workspaces/{workspaceId}/documents`: List documents within a specified workspace.
    *   `DELETE /api/workspaces/{workspaceId}/documents/{docId}`: Delete a specific document from a workspace.

*   **RAG Enhancement**:
    *   `POST /api/workspaces/{workspaceId}/rag/wikipedia`: Trigger a Wikipedia article fetch and injection into the RAG system for a specific workspace.

*   **Health Check**:
    *   `GET /health`: Basic API health check endpoint.

### WebSocket Events (Socket.IO)

The client communicates with the backend via Socket.IO for real-time updates and streaming chat responses.

*   **Client to Server (Outgoing Events)**:
    *   `chat_message`: Sends a user's chat message along with `session_id` and `workspace_id`.
    *   `cancel_message`: Requests the server to stop streaming the current LLM response.

*   **Server to Client (Incoming Events)**:
    *   `connected`: Sent by the server upon successful WebSocket connection.
    *   `chat_chunk`: Delivers partial LLM response tokens for streaming display.
    *   `chat_complete`: Indicates the completion of an LLM response, typically includes the full response and RAG context.
    *   `chat_cancelled`: Notifies the client that the server cancelled the LLM response.
    *   `error`: General error notifications from the server.
    *   `document_status`: Provides real-time updates on the processing status of documents within a workspace.
    *   `workspace_status`: Delivers real-time updates on the provisioning or deletion status of workspaces.
    *   `wikipedia_fetch_status`: Reports the real-time status of Wikipedia fetch and RAG injection jobs.

## Tech Stack

**Frontend**: React 19 + TypeScript + Vite + TailwindCSS + Redux
**Backend**: Python 3.11 + Flask + Socket.IO
**Infrastructure**: PostgreSQL, Qdrant, Ollama, MinIO, ELK Stack
**Tools**: Docker, Docker Compose, Poetry, Bun, Task

## Application Workflow

The InsightHub application facilitates interactive RAG-based querying through a client-server-worker architecture, driven by a series of events and status updates:

1.  **User Authentication & Settings**:
    *   Users create an account or sign in.
    *   They can modify basic account settings and manage their default RAG configuration (e.g., selecting Vector RAG or Graph RAG, and configuring sub-options like chunking strategy, embedding models, etc.). These settings are saved to their profile.

2.  **Workspace Creation & RAG Configuration**:
    *   Users create new workspaces. During creation, they are prompted to configure the RAG system specifically for that workspace, inheriting from their default settings or customizing further.
    *   Once configured, the server saves the workspace's RAG configuration and emits an event (e.g., `workspace.create_requested`) for a worker.
    *   A dedicated worker receives this event and begins provisioning the necessary resources for the requested RAG system (e.g., creating Qdrant collections, Neo4j instances).
    *   Throughout this provisioning, the worker sends granular status updates (events) back to the server.
    *   The server receives these status events and updates the client in real-time via WebSockets (Socket.IO), providing the user with live feedback on the workspace's creation progress.
    *   **Concurrency**: Users can create new workspaces even while others are still provisioning.

3.  **Document Upload & Processing**:
    *   Once a workspace is created and its RAG system is ready, users can upload documents (single or batch uploads). Documents are always tied to a specific workspace.
    *   The client sends the uploaded document to the server.
    *   The server saves the document (e.g., to MinIO) and creates a database record. It then emits an event (e.g., `document.upload_requested`) for a worker.
    *   A worker processes this event, retrieves the document, and integrates it into the workspace's RAG system (e.g., parsing, chunking, embedding, indexing in Qdrant/Neo4j).
    *   During processing, the worker emits status events, which the server relays to the client via WebSockets, keeping the user informed of the document's processing status. This status is displayed in the "Documents" column.
    *   **Concurrency**: Users can upload new documents even while other documents (in the same or different workspaces) are being processed.
    *   **Chat Locking**: While documents are being processed within a workspace, chat functionality for *that specific workspace* is temporarily locked. Users can only initiate chats in a workspace once all its uploaded documents are fully processed.

4.  **Querying the RAG System & Enhancement Prompts**:
    *   Once documents are processed and the RAG system is fully operational for a workspace, users can begin asking questions.
    *   For queries within a workspace that has processed documents, the LLM's context will be augmented (injected) with relevant information retrieved by the RAG system based on the user's query.
    *   If no documents have been uploaded or processed in a workspace, chats will function as normal LLM conversations without RAG augmentation.
    *   **RAG Enhancement Prompt**: If the RAG system finds no relevant context in the available documents for a query, the user is presented with options to enhance the RAG system:
        *   **Upload a Document**: Guides the user to the "Documents" panel to upload a new document.
        *   **Intelligently Fetch from Wikipedia**: Triggers a backend process to search Wikipedia for information related to the query and inject it into the RAG system.
        *   **Continue without additional context**: Proceeds with the query using only the LLM's base knowledge, without RAG augmentation.
    *   If "Upload a Document" or "Fetch from Wikipedia" is selected, the chat is paused. Once the new context is processed and integrated into the RAG system, the original query is automatically retried. Status updates for Wikipedia fetches are shown in the "Documents" column.
    *   Subsequent document uploads to the same workspace will follow the same processing pipeline, incrementally enhancing the existing RAG system.

5.  **Workspace Deletion**:
    *   When a user initiates the deletion of a workspace, that workspace, along with all its associated chats and documents, is immediately marked with a 'deleting' status in the UI. During this period, all interactions with that specific workspace (chat, document uploads, settings edits) are locked.
    *   A request is sent to the backend to remove the workspace and all its RAG system resources asynchronously.
    *   The backend sends real-time status updates via WebSockets.
    *   Once all resources are successfully removed and the backend confirms the complete deletion, the workspace is removed from the user's UI.

This event-driven flow ensures scalability, responsiveness, and clear communication of background processes to the user.




## Quick Start

### Prerequisites

* Docker & Docker Compose
* [Task](https://taskfile.dev): `sh -c "$(curl --location https://taskfile.dev/install.sh)"`
* 4GB disk space, 8GB RAM recommended

### Production

```bash
task build && task up
# Access: http://localhost:3000
# ELK Monitoring: http://localhost:5601
```

### Development

**Containerized (hot-reload)**:

```bash
task build-dev && task up-dev
# Server: http://localhost:5000
# Client: http://localhost:3000
# ELK Monitoring: http://localhost:5601
```

**Local + Infrastructure**:

```bash
task up-infra

# Terminal 1
cd packages/server && poetry install && task server

# Terminal 2
cd packages/client && bun install && task dev

# ELK Monitoring available at http://localhost:5601
```

---

## ELK Monitoring

The InsightHub application now ships logs from all project containers to the ELK stack:

* **Filebeat** reads container stdout/stderr logs.
* **Logstash** processes logs and forwards them to **Elasticsearch**.
* **Kibana** provides a web interface for searching, filtering, and visualizing logs.

**Default access**:

| Service       | URL                                            |
|---------------|------------------------------------------------|
| Kibana        | [http://localhost:5601](http://localhost:5601) |
| Elasticsearch | [http://localhost:9200](http://localhost:9200) |

**Tips**:

* You can filter logs in Kibana by `docker.container.name` or `docker.container.image`.
* Only containers labeled with `project=insighthub` are shipped to ELK.
* Use Kibana dashboards to separate app logs, database logs, and infrastructure logs.

---

## Key Commands

```bash
task --list          # Show all commands
task up              # Start production
task up-dev          # Start development
task up-infra        # Infrastructure only
task down            # Stop all
task check           # Run quality checks
task logs-server-dev # View server logs
task clean           # Remove containers/volumes
```

---

## Project Structure

```
insighthub/
+-- packages/
|   +-- server/              # Python RAG backend
|   |   +-- src/
|   |   |   +-- infrastructure/rag/  # RAG implementations
|   |   |   +-- domains/             # Business logic
|   |   |   +-- api.py               # Flask app
|   |   +-- tests/           # Unit & integration tests
|   +-- client/              # React frontend
|       +-- src/
|           +-- components/  # UI components
|           +-- store/       # Redux state
+-- elk/                     # ELK stack configuration
|   +-- filebeat/filebeat.yml
|   +-- logstash/logstash.conf
+-- docker-compose.yml       # Service orchestration
+-- Taskfile.yml             # Task commands
```

---

## Testing

See [testing guide](docs/testing.md) for the complete testing guide.

### Quick Test Commands

```bash
# Client Tests
cd packages/client
task test              # Unit tests (319 passing)
task test:e2e          # E2E tests (Playwright)
task storybook         # Component documentation

# Server Tests
cd packages/server
task test              # Unit tests with coverage
task test:api          # Bruno API tests
```

---

## Code Quality

```bash
# Server
cd packages/server
task format      # Auto-format code
task test        # Run tests
task check       # All checks

# Client
cd packages/client
task format      # Prettier
task lint        # ESLint
task check       # All checks
```

---

## Configuration

Environment variables in `.env`:

```bash
# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:1b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Database
DATABASE_URL=postgresql://insighthub:password@localhost:5432/insighthub

# Storage
BLOB_STORAGE_TYPE=s3
S3_ENDPOINT_URL=http://localhost:9000
```

---

## Troubleshooting

```bash
# Services not starting
task ps && task logs

# Database issues
task down && docker volume rm insighthub_postgres_data && task up-dev

# Port conflicts
lsof -i :5000 && lsof -i :3000

# Hot-reload not working
task restart-dev

# Pull models manually
docker compose exec ollama ollama pull llama3.2:1b

# Check ELK logs
docker compose logs filebeat
docker compose logs logstash
docker compose logs kibana
```

See [docs/docker.md](docs/docker.md) for details.

---

## Documentation

* [Testing Guide](docs/testing.md) - Comprehensive testing documentation
* [Docker Setup](docs/docker.md)
* [Task Commands](docs/taskfile-setup.md)
* [Architecture](docs/architecture.md)
* [Contributing](docs/contributing.md)

## License

GPL-3.0
