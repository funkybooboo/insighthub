# InsightHub Client-Server API Specification

This document specifies all APIs that the InsightHub client requires from the server, based on current client implementation. It serves as both a reference for frontend developers and a checklist for backend implementation.

## Overview

The client communicates with the server through two main channels:

1. **REST APIs** - For synchronous operations like authentication, CRUD operations, and configuration
2. **WebSocket APIs** - For real-time features like streaming chat responses and status updates

**Document Status**: This specification is derived from the actual client service layer code (`api.ts` and `socket.ts`), ensuring all listed endpoints are actively used by the current implementation.

## Implementation Priority

### High Priority (Core Features - Implement First)

1. **Authentication endpoints** - User registration, login, logout, profile access
2. **Workspace CRUD** - Create, read, update, delete workspaces
3. **Document management** - Upload, list, and delete documents
4. **Chat functionality** - Send messages and receive responses
5. **Basic WebSocket chat streaming** - Real-time message streaming

### Medium Priority (Enhanced Features)

1. **RAG configuration endpoints** - Workspace-specific RAG settings
2. **Status update WebSockets** - Document processing and workspace status
3. **Wikipedia integration** - External data source fetching
4. **User preferences/profile updates** - Theme settings, profile editing

### Low Priority (Nice-to-have)

1. **Password change** - User password updates
2. **Default RAG config** - User-level default configurations
3. **Advanced workspace features** - Bulk operations, advanced filtering

## REST API Endpoints

### Health & System

#### GET /health

- **Status**: ✅ Currently Used
- **Purpose**: Check server health status
- **Used by**: Health checks, connection validation
- **Authentication**: None required
- **Response**: `{ status: string }`

### Authentication

#### POST /api/auth/signup

- **Status**: ✅ Currently Used
- **Purpose**: Register new user account
- **Used by**: SignupForm component
- **Authentication**: None required
- **Request**:
    ```typescript
    {
      username: string;
      email: string;
      password: string;
      full_name?: string;
    }
    ```
- **Response**: AuthResponse with user data and JWT token
- **Error Codes**: 400 (validation), 409 (email exists)

#### POST /api/auth/login

- **Status**: ✅ Currently Used
- **Purpose**: Authenticate user and get JWT token
- **Used by**: LoginForm component
- **Authentication**: None required
- **Request**:
    ```typescript
    {
        username: string;
        password: string;
    }
    ```
- **Response**: AuthResponse with user data and JWT token
- **Error Codes**: 401 (invalid credentials)

#### POST /api/auth/logout

- **Status**: ✅ Currently Used
- **Purpose**: Invalidate JWT token
- **Used by**: Logout functionality
- **Authentication**: Bearer token required
- **Request**: Empty body
- **Response**: `{ message: string }`

#### GET /api/auth/me

- **Status**: ✅ Currently Used
- **Purpose**: Get current user profile information
- **Used by**: Protected routes, user profile display
- **Authentication**: Bearer token required
- **Response**: UserResponse with user data

#### PATCH /api/auth/preferences

- **Status**: ✅ Currently Used
- **Purpose**: Update user preferences (theme, etc.)
- **Used by**: ThemePreferences component
- **Authentication**: Bearer token required
- **Request**:
    ```typescript
    {
      theme_preference?: 'light' | 'dark';
    }
    ```
- **Response**: UserResponse with updated user data

#### PATCH /api/auth/profile

- **Status**: ✅ Currently Used
- **Purpose**: Update user profile information
- **Used by**: ProfileSettings component
- **Authentication**: Bearer token required
- **Request**:
    ```typescript
    {
      full_name?: string;
      email?: string;
    }
    ```
- **Response**: UserResponse with updated user data

#### POST /api/auth/change-password

- **Status**: ✅ Currently Used
- **Purpose**: Change user password
- **Used by**: PasswordChangeForm component
- **Authentication**: Bearer token required
- **Request**:
    ```typescript
    {
        current_password: string;
        new_password: string;
    }
    ```
- **Response**: void (success status)

### Workspaces

#### GET /api/workspaces

- **Status**: ✅ Currently Used
- **Purpose**: List all workspaces for the authenticated user
- **Used by**: WorkspacesPage, workspace selection
- **Authentication**: Bearer token required
- **Response**: `Workspace[]`

#### GET /api/workspaces/{workspaceId}

- **Status**: ✅ Currently Used
- **Purpose**: Get details for a specific workspace
- **Used by**: WorkspaceDetailPage, workspace settings
- **Authentication**: Bearer token required
- **Response**: `Workspace`

#### POST /api/workspaces

- **Status**: ✅ Currently Used
- **Purpose**: Create a new workspace
- **Used by**: Workspace creation forms
- **Authentication**: Bearer token required
- **Request**: `CreateWorkspaceRequest`
- **Response**: `Workspace` (201 Created)

#### PATCH /api/workspaces/{workspaceId}

- **Status**: ✅ Currently Used
- **Purpose**: Update workspace details
- **Used by**: WorkspaceSettings component
- **Authentication**: Bearer token required
- **Request**: `UpdateWorkspaceRequest`
- **Response**: `Workspace`

#### DELETE /api/workspaces/{workspaceId}

- **Status**: ✅ Currently Used
- **Purpose**: Delete a workspace
- **Used by**: Workspace deletion functionality
- **Authentication**: Bearer token required
- **Request**: Empty body
- **Response**: `{ message: string }`

### Documents

#### GET /api/workspaces/{workspaceId}/documents

- **Status**: ✅ Currently Used
- **Purpose**: List all documents in a workspace
- **Used by**: DocumentList component
- **Authentication**: Bearer token required
- **Response**:
    ```typescript
    {
      documents: Document[];
      count: number;
    }
    ```

#### POST /api/workspaces/{workspaceId}/documents/upload

- **Status**: ✅ Currently Used
- **Purpose**: Upload a document to the workspace
- **Used by**: DocumentUpload, FileUpload components
- **Authentication**: Bearer token required
- **Request**: `multipart/form-data` with file
- **Response**:
    ```typescript
    {
        message: string;
        document: Document;
    }
    ```
- **Error Codes**: 400 (invalid file), 413 (file too large)

#### DELETE /api/workspaces/{workspaceId}/documents/{docId}

- **Status**: ✅ Currently Used
- **Purpose**: Delete a document from workspace
- **Used by**: DocumentManager component
- **Authentication**: Bearer token required
- **Request**: Empty body
- **Response**: `{ message: string }`

### RAG Configuration

#### GET /api/workspaces/{workspaceId}/rag-config

- **Status**: ✅ Currently Used
- **Purpose**: Get RAG configuration for a workspace
- **Used by**: RagConfigSettings, RagConfigForm components
- **Authentication**: Bearer token required
- **Response**: `RagConfig`

#### POST /api/workspaces/{workspaceId}/rag-config

- **Status**: ✅ Currently Used
- **Purpose**: Create RAG configuration for a workspace
- **Used by**: RagConfigForm component
- **Authentication**: Bearer token required
- **Request**: `CreateRagConfigRequest`
- **Response**: `RagConfig`

#### PATCH /api/workspaces/{workspaceId}/rag-config

- **Status**: ✅ Currently Used
- **Purpose**: Update RAG configuration for a workspace
- **Used by**: RagConfigSettings component
- **Authentication**: Bearer token required
- **Request**: `UpdateRagConfigRequest`
- **Response**: `RagConfig`

#### GET /api/auth/default-rag-config

- **Status**: ✅ Currently Used
- **Purpose**: Get user's default RAG configuration
- **Used by**: RagConfigForm for default values
- **Authentication**: Bearer token required
- **Response**: `DefaultRagConfig | null`

#### PUT /api/auth/default-rag-config

- **Status**: ✅ Currently Used
- **Purpose**: Save user's default RAG configuration
- **Used by**: RagConfigForm component
- **Authentication**: Bearer token required
- **Request**: `DefaultRagConfig`
- **Response**: `DefaultRagConfig`

### Chat

#### POST /api/chat

- **Status**: ✅ Currently Used
- **Purpose**: Send a chat message and get a response from the RAG system
- **Used by**: ChatBot component
- **Authentication**: Bearer token required
- **Request**:
    ```typescript
    {
      message: string;
      session_id?: number;
      workspace_id?: number;
      rag_type?: string;
    }
    ```
- **Response**:
    ```typescript
    {
      answer: string;
      context: ChatContext[];
      session_id: number;
      documents_count: number;
    }
    ```

### External Data Sources

#### POST /api/workspaces/{workspaceId}/rag/wikipedia

- **Status**: ✅ Currently Used
- **Purpose**: Fetch a Wikipedia article and inject it into the RAG system
- **Used by**: RagConfigForm or dedicated Wikipedia import feature
- **Authentication**: Bearer token required
- **Request**:
    ```typescript
    {
        query: string;
    }
    ```
- **Response**: `{ message: string }`

## WebSocket Events

### Connection Management

#### connect()

- **Status**: ✅ Currently Used
- **Purpose**: Establish WebSocket connection
- **Used by**: SocketService initialization
- **Events**: Connection status updates

#### disconnect()

- **Status**: ✅ Currently Used
- **Purpose**: Close WebSocket connection
- **Used by**: Cleanup on logout/app close

### Chat Streaming

#### emit 'chat_message'

- **Status**: ✅ Currently Used
- **Purpose**: Send chat message for streaming response
- **Used by**: ChatBot component
- **Data**:
    ```typescript
    {
      message: string;
      session_id?: number;
      workspace_id?: number;
      rag_type?: string;
      client_id?: string;
    }
    ```

#### on 'chat_chunk'

- **Status**: ✅ Currently Used
- **Purpose**: Receive streaming response chunks
- **Used by**: ChatMessages component for real-time display
- **Data**: `{ chunk: string }`

#### on 'chat_complete'

- **Status**: ✅ Currently Used
- **Purpose**: Receive complete response with metadata
- **Used by**: Chat completion handling
- **Data**:
    ```typescript
    {
      session_id: number;
      full_response: string;
      context?: Context[];
    }
    ```

#### emit 'cancel_message'

- **Status**: ✅ Currently Used
- **Purpose**: Cancel ongoing chat message
- **Used by**: Chat input cancel functionality
- **Data**: `{ client_id: string }`

#### on 'chat_cancelled'

- **Status**: ✅ Currently Used
- **Purpose**: Confirm message cancellation
- **Used by**: UI state updates
- **Data**: `{ status: string }`

### Status Updates

#### emit 'subscribe_status'

- **Status**: ✅ Currently Used
- **Purpose**: Subscribe to status updates for user
- **Used by**: Status updates initialization
- **Data**: `{ user_id: number }`

#### on 'subscribed'

- **Status**: ✅ Currently Used
- **Purpose**: Confirm subscription
- **Used by**: Status update setup
- **Data**: `{ user_id: number, room: string }`

#### on 'document_status'

- **Status**: ✅ Currently Used
- **Purpose**: Receive document processing status updates
- **Used by**: Document upload progress, status indicators
- **Data**:
    ```typescript
    {
      document_id: number;
      workspace_id: number;
      status: 'pending' | 'processing' | 'ready' | 'failed';
      message?: string;
      error?: string;
      progress?: number;
      timestamp: string;
    }
    ```

#### on 'workspace_status'

- **Status**: ✅ Currently Used
- **Purpose**: Receive workspace status updates
- **Used by**: Workspace provisioning status
- **Data**:
    ```typescript
    {
      workspace_id: number;
      user_id: number;
      status: 'provisioning' | 'ready' | 'error';
      message?: string;
      error?: string;
      timestamp: string;
    }
    ```

### Error Handling

#### on 'error'

- **Status**: ✅ Currently Used
- **Purpose**: Handle WebSocket errors
- **Used by**: Global error handling
- **Data**: `{ error: string }`

#### on 'connected'

- **Status**: ✅ Currently Used
- **Purpose**: Connection established confirmation
- **Used by**: Connection status management

#### on 'disconnect'

- **Status**: ✅ Currently Used
- **Purpose**: Connection lost notification
- **Used by**: Reconnection logic

## Data Types

### Core Types

```typescript
interface AuthResponse {
    access_token: string;
    token_type: string;
    user: {
        id: number;
        username: string;
        email: string;
        full_name: string | null;
        created_at: string;
        theme_preference?: string;
    };
}

interface UserResponse {
    id: number;
    username: string;
    email: string;
    full_name: string | null;
    created_at: string;
    theme_preference?: string;
}

interface Workspace {
    id: number;
    name: string;
    description?: string;
    status: 'provisioning' | 'ready' | 'failed' | 'deleting';
    created_at: string;
    updated_at: string;
    rag_config?: RagConfig;
    document_count?: number;
    session_count?: number;
}

interface Document {
    id: number;
    filename: string;
    file_size: number;
    mime_type: string;
    chunk_count?: number;
    created_at: string;
}

interface RagConfig {
    id: number;
    workspace_id: number;
    retriever_type: 'vector' | 'graph';
    // ... additional config fields based on type
    created_at: string;
    updated_at: string;
}

interface ChatResponse {
    answer: string;
    context: ChatContext[];
    session_id: number;
    documents_count: number;
}

interface ChatContext {
    text: string;
    score: number;
    metadata: Record<string, unknown>;
}

interface Context {
    text: string;
    score: number;
    metadata: Record<string, unknown>;
}
```

### Request Types

```typescript
interface CreateWorkspaceRequest {
    name: string;
    description?: string;
    rag_config?: CreateRagConfigRequest;
}

interface UpdateWorkspaceRequest {
    name?: string;
    description?: string;
    status?: 'provisioning' | 'ready' | 'failed';
}

type CreateRagConfigRequest = VectorRagConfig | GraphRagConfig;
type UpdateRagConfigRequest = Partial<VectorRagConfig> | Partial<GraphRagConfig>;
type DefaultRagConfig = VectorRagConfig | GraphRagConfig;
```

## Authentication Requirements

- **JWT Bearer Token**: All protected endpoints require `Authorization: Bearer <token>` header
- **Token Storage**: Client stores tokens in localStorage
- **Auto-refresh**: Client redirects to login on 401 responses
- **Token Invalidation**: Tokens invalidated on logout

## Content Types

- **JSON requests**: `Content-Type: application/json`
- **File uploads**: `Content-Type: multipart/form-data`

## Error Handling

### HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict (duplicate email, etc.)
- `413`: Payload Too Large (file uploads)
- `500`: Internal Server Error

### WebSocket Errors

- Connection failures
- Message parsing errors
- Authentication errors
- Server-side processing errors

### Client Error Handling

- Automatic retry logic for transient failures
- Exponential backoff for reconnection
- User-friendly error messages
- Loading states for async operations

## Real-time Features

### Streaming Chat

- **Messages sent via WebSocket** for real-time response streaming
- **Client-generated IDs** for request tracking and cancellation
- **Chunked responses** for progressive UI updates

### Status Updates

- **Document processing status** via WebSocket for upload progress
- **Workspace provisioning status** for long-running operations
- **Filtered broadcasts** by user/workspace to avoid unnecessary traffic

## Implementation Notes

### Client Architecture

- **Service Layer**: Centralized API calls in `packages/client/src/services/`
- **Type Safety**: Full TypeScript interfaces for all requests/responses
- **Error Boundaries**: Comprehensive error handling and user feedback
- **State Management**: Redux Toolkit for client-side state

### Server Requirements

- **CORS Configuration**: Allow frontend origin for development
- **Rate Limiting**: Implement appropriate rate limits per user
- **File Upload Limits**: Configure max file sizes and types
- **WebSocket Scaling**: Handle multiple concurrent connections
- **Database Transactions**: Ensure data consistency across operations

### Testing Strategy

- **Unit Tests**: Mock external dependencies
- **Integration Tests**: Test with real database containers
- **E2E Tests**: Full user workflows
- **Load Testing**: WebSocket connection scaling

## Migration Notes

This specification reflects the **current client implementation**. Future enhancements may require additional endpoints. Always check the client service layer code (`api.ts`, `socket.ts`) for the most up-to-date API usage.

---

**Last Updated**: Based on client code analysis  
**Total Endpoints**: 23 REST + 13 WebSocket events  
**High Priority Endpoints**: 18 (authentication, workspaces, documents, chat, basic WebSocket)</content>
<parameter name="filePath">packages/client/docs/api-specification.md
