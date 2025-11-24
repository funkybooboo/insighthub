# Client Implementation Gaps Analysis

Based on the `client-user-flows.md` document, here are the missing features and implementation gaps in the current client:

## 🚨 Critical Missing Features

### 1. RAG Enhancement Prompt UI Component

**Status**: ❌ Missing
**Impact**: High - Core chat enhancement feature

**What's Expected**:

- When `chat.no_context_found` WebSocket event is received, show a prompt with 3 options:
    - "Upload a Document"
    - "Fetch from Wikipedia"
    - "Continue without additional context"

**What's Implemented**:

- ChatBot has some RAG enhancement logic but no dedicated UI prompt component
- Manual document upload and Wikipedia fetch work, but no integrated prompt system

**Required Implementation**:

```typescript
// New component: RAGEnhancementPrompt.tsx
interface RAGEnhancementPromptProps {
    onUploadDocument: () => void;
    onFetchWikipedia: (query: string) => void;
    onContinueWithoutContext: () => void;
    isVisible: boolean;
}
```

### 2. Persistent Chat Sessions with Backend Storage

**Status**: ⚠️ Partially Missing
**Impact**: High - Chat history and session management

**What's Expected**:

- Chat sessions stored on backend with full CRUD operations
- API endpoints: `/api/workspaces/{workspaceId}/chat/sessions/{sessionId}/messages`
- Sessions persist across browser sessions

**What's Implemented**:

- Client-side chat session management (local Redux state)
- Sessions are lost on page refresh
- No backend persistence

**Required API Endpoints**:

```typescript
// Missing from api.ts
async createChatSession(workspaceId: number, title: string): Promise<ChatSession>
async getChatSessions(workspaceId: number): Promise<ChatSession[]>
async deleteChatSession(workspaceId: number, sessionId: number): Promise<void>
async sendChatMessage(workspaceId: number, sessionId: number, content: string): Promise<void>
async cancelChatMessage(workspaceId: number, sessionId: number): Promise<void>
```

### 3. API Endpoint Path Mismatches

**Status**: ❌ Incorrect Paths
**Impact**: Medium - API integration issues

**Mismatches Found**:

| User Flows Expect                                                  | Client Currently Uses                         | Status            |
| ------------------------------------------------------------------ | --------------------------------------------- | ----------------- |
| `/api/workspaces/{workspaceId}/chat/sessions/{sessionId}/messages` | `/api/chat`                                   | ❌ Wrong          |
| `/api/workspaces/{workspaceId}/chat/sessions/{sessionId}/cancel`   | `socketService.cancelMessage()`               | ⚠️ WebSocket only |
| `/api/workspaces/{workspaceId}/documents/fetch-wikipedia`          | `/api/workspaces/{workspaceId}/rag/wikipedia` | ❌ Wrong          |

### 4. Missing WebSocket Events

**Status**: ❌ Missing Events
**Impact**: Medium - Real-time status updates

**Missing WebSocket Events**:

- `chat.no_context_found` - Triggers RAG enhancement prompt
- `wikipedia_fetch_status` - Status updates for Wikipedia fetching
- `chat.response_chunk` - Streaming response chunks (currently using `chat_chunk`)

**Current WebSocket Events** (from socket.ts):

```typescript
✅ chat_chunk, chat_complete, chat_cancelled
✅ document_status, workspace_status
✅ subscribed, connected, disconnected, error
❌ chat.no_context_found
❌ wikipedia_fetch_status
❌ chat.response_chunk (using chat_chunk instead)
```

## 🔧 Implementation Priority & Plan

### Phase 1: Critical Chat Features (Week 1)

1. **Create RAGEnhancementPrompt component**
2. **Add missing WebSocket event handlers**
3. **Fix API endpoint paths to match user flows**

### Phase 2: Backend Chat Sessions (Week 2)

1. **Implement chat session CRUD API endpoints**
2. **Update ChatBot to use backend sessions**
3. **Add session persistence**

### Phase 3: Polish & Testing (Week 3)

1. **Add comprehensive error handling**
2. **Implement chat message cancellation via API**
3. **Add session title auto-generation**

## 📋 Detailed Implementation Requirements

### New Components Needed:

1. `RAGEnhancementPrompt.tsx` - Modal/prompt for context enhancement options
2. `ChatSessionManager.tsx` - Backend session management wrapper

### New API Methods Needed:

```typescript
// In api.ts
async createChatSession(workspaceId: number, title?: string): Promise<ChatSession>
async getChatSessions(workspaceId: number): Promise<ChatSession[]>
async deleteChatSession(workspaceId: number, sessionId: number): Promise<void>
async sendChatMessage(workspaceId: number, sessionId: number, content: string, messageType?: string): Promise<{message_id: string}>
async cancelChatMessage(workspaceId: number, sessionId: number, messageId?: string): Promise<void>
async fetchWikipedia(workspaceId: number, query: string): Promise<void> // Fix endpoint path
```

### New WebSocket Events Needed:

```typescript
// In socket.ts
onChatNoContextFound(callback: (data: {session_id: number, query: string}) => void): void
onWikipediaFetchStatus(callback: (data: WikipediaFetchStatusData) => void): void
onChatResponseChunk(callback: (data: {chunk: string, message_id: string}) => void): void // More specific than current chat_chunk
```

### Redux State Updates Needed:

```typescript
// In chatSlice.ts
interface ChatSession {
    id: string;
    backendId?: number; // Add backend session ID
    title: string;
    messages: Message[];
    createdAt: number;
    updatedAt: number;
    workspaceId: number; // Add workspace association
}
```

## 🎯 Next Steps

1. **Immediate**: Create RAGEnhancementPrompt component and integrate with ChatBot
2. **Short-term**: Fix API endpoint paths and add missing WebSocket events
3. **Medium-term**: Implement backend chat session persistence
4. **Testing**: Verify all user flows work end-to-end

The client currently has ~70% of the required functionality. The missing 30% consists mainly of the RAG enhancement prompt system and proper backend chat session management.</content>
<parameter name="filePath">packages/client/docs/implementation-gaps.md
