# InsightHub Client User Flows and API Interactions

This document provides a detailed breakdown of every significant user action within the InsightHub React Frontend, mapping the client-side flow, API interactions, and expected backend/worker behaviors. This level of detail aims to clarify the full application flow for developers working on the server and worker components.

---

## Table of Contents

1.  [User Authentication](#user-authentication)
    *   [User Login](#user-login)
    *   [User Signup](#user-signup)
    *   [User Logout](#user-logout)
    *   [Get Current User Profile](#get-current-user-profile)
    *   [Update User Profile](#update-user-profile)
    *   [Update User Preferences (e.g., Theme)](#update-user-preferences-eg-theme)
    *   [Change User Password](#change-user-password)
2.  [Default RAG Configuration Management](#default-rag-configuration-management)
    *   [Fetch Default RAG Config](#fetch-default-rag-config)
    *   [Save Default RAG Config](#save-default-rag-config)
3.  [Workspace Management](#workspace-management)
    *   [List Workspaces](#list-workspaces)
    *   [Select Active Workspace](#select-active-workspace)
    *   [Create New Workspace](#create-new-workspace)
    *   [View Workspace Details](#view-workspace-details)
    *   [Edit Workspace Details](#edit-workspace-details)
    *   [Delete Workspace](#delete-workspace)
4.  [Chat Session Management](#chat-session-management)
    *   [Create New Chat Session](#create-new-chat-session)
    *   [Select Active Chat Session](#select-active-chat-session)
    *   [Delete Chat Session](#delete-chat-session)
5.  [Document Management](#document-management)
    *   [Upload Document](#upload-document)
    *   [List Documents in Workspace](#list-documents-in-workspace)
    *   [Delete Document](#delete-document)
6.  [Chat Interaction](#chat-interaction)
    *   [Send Chat Message](#send-chat-message)
    *   [Cancel Chat Message Streaming](#cancel-chat-message-streaming)
    *   [RAG Enhancement Prompt (No Context Found)](#rag-enhancement-prompt-no-context-found)
        *   [Action: Upload a Document (from Prompt)](#action-upload-a-document-from-prompt)
        *   [Action: Fetch from Wikipedia (from Prompt)](#action-fetch-from-wikipedia-from-prompt)
        *   [Action: Continue without additional context (from Prompt)](#action-continue-without-additional-context-from-prompt)
7.  [Real-time Status Updates (WebSocket)](#real-time-status-updates-websocket)
    *   [Document Status Updates](#document-status-updates)
    *   [Workspace Status Updates](#workspace-status-updates)
    *   [Wikipedia Fetch Status Updates](#wikipedia-fetch-status-updates)

---

## 1. User Authentication

### User Login

**User Action**: User enters username/password on the login form and clicks "Login".

**Client-Side Flow**:
*   **UI State**: Login button disabled, loading indicator shown.
*   **Redux Actions**: `authSlice.login.pending` dispatched.
*   **API Call**:
    *   **Method**: `POST`
    *   **Endpoint**: `/api/auth/login`
    *   **Payload**: `{"username": "user", "password": "password"}`
    *   **Expected Response (Success)**: `200 OK`, `{"access_token": "jwt_token", "token_type": "bearer", "user": {id: 1, username: "user", email: "...", full_name: "..."}}`
    *   **Expected Response (Failure)**: `401 Unauthorized` or `400 Bad Request`, `{"detail": "Invalid credentials"}`
*   **Error Handling**: If API fails, `authSlice.login.rejected` is dispatched, error message displayed on UI.
*   **Success Handling**: If API succeeds, JWT token saved to `localStorage`, `authSlice.login.fulfilled` dispatched, user navigated to `/` (main application).

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `POST /api/auth/login`.
    *   Validates credentials against PostgreSQL user records.
    *   If valid, generates a JWT.
    *   Responds with JWT and user details.
*   **Workers**: No direct worker interaction for login.

**Real-time Feedback (Client-Side)**:
*   Upon successful login, the client connects to the WebSocket server.
*   `socketService.onConnected` event confirms connection, potentially logging "Connected to chat server".

---

### User Signup

**User Action**: User enters username, email, and password on the signup form, then clicks "Sign Up".

**Client-Side Flow**:
*   **UI State**: Signup button disabled, loading indicator shown.
*   **Redux Actions**: `authSlice.signup.pending` dispatched.
*   **API Call**:
    *   **Method**: `POST`
    *   **Endpoint**: `/api/auth/signup`
    *   **Payload**: `{"username": "newuser", "email": "newuser@example.com", "password": "securepassword", "full_name": "New User"}` (full_name optional)
    *   **Expected Response (Success)**: `200 OK`, `{"access_token": "jwt_token", "token_type": "bearer", "user": {id: 2, username: "newuser", email: "...", full_name: "..."}}`
    *   **Expected Response (Failure)**: `409 Conflict` (username/email exists) or `400 Bad Request`, `{"detail": "Error message"}`
*   **Error Handling**: If API fails, `authSlice.signup.rejected` is dispatched, error message displayed on UI.
*   **Success Handling**: If API succeeds, JWT token saved to `localStorage`, `authSlice.signup.fulfilled` dispatched, user navigated to `/` (main application).

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `POST /api/auth/signup`.
    *   Validates input (e.g., strong password, unique username/email).
    *   Hashes password.
    *   Creates new user record in PostgreSQL.
    *   Generates a JWT.
    *   Responds with JWT and new user details.
*   **Workers**: No direct worker interaction for signup.

**Real-time Feedback (Client-Side)**:
*   Upon successful signup, the client connects to the WebSocket server.
*   `socketService.onConnected` event confirms connection, potentially logging "Connected to chat server".

---

### User Logout

**User Action**: User clicks "Logout" button (e.g., from User Menu in the header).

**Client-Side Flow**:
*   **UI State**: Logout button might temporarily show loading state.
*   **Redux Actions**: `authSlice.logout.pending` dispatched.
*   **API Call**:
    *   **Method**: `POST`
    *   **Endpoint**: `/api/auth/logout` (JWT in Authorization header)
    *   **Payload**: None
    *   **Expected Response (Success)**: `200 OK`, `{"message": "Successfully logged out"}`
    *   **Expected Response (Failure)**: `401 Unauthorized` (if token invalid/expired), `{"detail": "Error message"}`
*   **Error Handling**: If API fails, `authSlice.logout.rejected` dispatched, error message displayed. Client still clears local session.
*   **Success Handling**: Regardless of API success/failure (as server invalidation might fail), client removes JWT token from `localStorage`, dispatches `authSlice.logout.fulfilled`, clears `authSlice` state, and navigates user to `/login`.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `POST /api/auth/logout`.
    *   (Optional, depending on JWT implementation) Invalidates the provided JWT on the server-side (e.g., adds to a blocklist/denylist).
    *   Responds with confirmation.
*   **Workers**: No direct worker interaction.

**Real-time Feedback (Client-Side)**:
*   Client disconnects from the WebSocket server.
*   `socketService.onDisconnected` event confirms disconnection.

---

### Get Current User Profile

**User Action**: Implicitly on application load (if authenticated) or when navigating to a profile/settings page.

**Client-Side Flow**:
*   **UI State**: Loading indicator for user data might be shown.
*   **Redux Actions**: `authSlice.getCurrentUser.pending` dispatched.
*   **API Call**:
    *   **Method**: `GET`
    *   **Endpoint**: `/api/auth/me` (JWT in Authorization header)
    *   **Payload**: None
    *   **Expected Response (Success)**: `200 OK`, `{"id": 1, "username": "user", "email": "...", "full_name": "...", "created_at": "...", "theme_preference": "dark"}`
    *   **Expected Response (Failure)**: `401 Unauthorized` (if token invalid/expired), `{"detail": "Error message"}`
*   **Error Handling**: If API fails with 401, client logs out. Other errors dispatch `authSlice.getCurrentUser.rejected`, error displayed.
*   **Success Handling**: If API succeeds, `authSlice.getCurrentUser.fulfilled` dispatched, `user` state updated in Redux. `theme_preference` is used to set the global UI theme.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `GET /api/auth/me`.
    *   Authenticates JWT.
    *   Retrieves user details from PostgreSQL.
    *   Responds with user object.
*   **Workers**: No direct worker interaction.

**Real-time Feedback (Client-Side)**:
*   UI elements depending on user data (e.g., username in header, theme) update.

---

### Update User Profile

**User Action**: User updates name or email in a profile settings form and clicks "Save".

**Client-Side Flow**:
*   **UI State**: Save button disabled, loading indicator shown.
*   **Redux Actions**: (Not directly a Redux action for pending, handled locally)
*   **API Call**:
    *   **Method**: `PATCH`
    *   **Endpoint**: `/api/auth/profile` (JWT in Authorization header)
    *   **Payload**: `{"full_name": "New Full Name", "email": "newemail@example.com"}` (partial updates)
    *   **Expected Response (Success)**: `200 OK`, `{"id": 1, "username": "user", "email": "newemail@example.com", "full_name": "New Full Name", "created_at": "...", "theme_preference": "dark"}`
    *   **Expected Response (Failure)**: `400 Bad Request` (e.g., invalid email), `{"detail": "Error message"}` or `401 Unauthorized`.
*   **Error Handling**: Error message displayed on UI.
*   **Success Handling**: `authSlice.userUpdated` dispatched with new user data. UI reflects changes.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `PATCH /api/auth/profile`.
    *   Authenticates JWT.
    *   Validates input.
    *   Updates user record in PostgreSQL.
    *   Responds with updated user object.
*   **Workers**: No direct worker interaction.

**Real-time Feedback (Client-Side)**:
*   Header/profile display updates with new name/email.

---

### Update User Preferences (e.g., Theme)

**User Action**: User selects a new theme (e.g., "dark") from a preference setting.

**Client-Side Flow**:
*   **UI State**: UI might instantly switch theme for responsiveness, with a loading indicator for persistence.
*   **Redux Actions**: `authSlice.updatePreferences.pending` dispatched (or handled directly by `userSettingsSlice`).
*   **API Call**:
    *   **Method**: `PATCH`
    *   **Endpoint**: `/api/auth/preferences` (JWT in Authorization header)
    *   **Payload**: `{"theme_preference": "dark"}`
    *   **Expected Response (Success)**: `200 OK`, `{"id": 1, "username": "user", "email": "...", "full_name": "...", "theme_preference": "dark"}`
    *   **Expected Response (Failure)**: `400 Bad Request` or `401 Unauthorized`.
*   **Error Handling**: If API fails, `authSlice.updatePreferences.rejected` dispatched, theme might revert or error message displayed.
*   **Success Handling**: If API succeeds, `authSlice.updatePreferences.fulfilled` dispatched, global theme applied to `document.documentElement.classList`, and `user` state updated.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `PATCH /api/auth/preferences`.
    *   Authenticates JWT.
    *   Validates input.
    *   Updates user preferences in PostgreSQL.
    *   Responds with updated user object.
*   **Workers**: No direct worker interaction.

**Real-time Feedback (Client-Side)**:
*   The entire UI immediately switches to the selected theme.

---

### Change User Password

**User Action**: User provides current and new passwords in a form and clicks "Change Password".

**Client-Side Flow**:
*   **UI State**: Button disabled, loading indicator shown.
*   **Redux Actions**: (Not directly a Redux action for pending, handled locally)
*   **API Call**:
    *   **Method**: `POST`
    *   **Endpoint**: `/api/auth/change-password` (JWT in Authorization header)
    *   **Payload**: `{"current_password": "oldpassword", "new_password": "newsecurepassword"}`
    *   **Expected Response (Success)**: `200 OK`, `{"message": "Password updated successfully"}`
    *   **Expected Response (Failure)**: `400 Bad Request` (e.g., current password incorrect, new password too weak), `{"detail": "Error message"}` or `401 Unauthorized`.
*   **Error Handling**: Error message displayed on UI.
*   **Success Handling**: Success message displayed, form fields cleared.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `POST /api/auth/change-password`.
    *   Authenticates JWT.
    *   Verifies `current_password` against hashed password in PostgreSQL.
    *   Validates `new_password` (e.g., strength requirements).
    *   Hashes `new_password` and updates user record in PostgreSQL.
    *   Responds with success message.
*   **Workers**: No direct worker interaction.

**Real-time Feedback (Client-Side)**:
*   No real-time feedback beyond the success/error message on the current page.

---

## 2. Default RAG Configuration Management

### Fetch Default RAG Config

**User Action**: Implicitly on application load (if authenticated) or when navigating to the settings page.

**Client-Side Flow**:
*   **UI State**: Loading indicator for RAG config might be shown on settings page.
*   **Redux Actions**: `userSettingsSlice.fetchDefaultRagConfig.pending` dispatched.
*   **API Call**:
    *   **Method**: `GET`
    *   **Endpoint**: `/api/auth/default-rag-config` (JWT in Authorization header)
    *   **Payload**: None
    *   **Expected Response (Success)**: `200 OK`, `{"retriever_type": "vector", "embedding_model": "nomic-embed-text", "chunk_size": 1000, "chunk_overlap": 200, "top_k": 8, "rerank_enabled": false}` (example for VectorRAG) or `{"retriever_type": "graph", "max_hops": 2, "entity_extraction_model": "ollama"}` (example for GraphRAG).
    *   **Expected Response (Not Found)**: `404 Not Found`, `{"detail": "Default RAG config not found"}` (client initializes with internal defaults).
    *   **Expected Response (Failure)**: `401 Unauthorized` or `500 Internal Server Error`, `{"detail": "Error message"}`
*   **Error Handling**: If 404, client uses internal defaults. Other errors dispatch `userSettingsSlice.fetchDefaultRagConfig.rejected`, error message displayed on UI.
*   **Success Handling**: If API succeeds, `userSettingsSlice.fetchDefaultRagConfig.fulfilled` dispatched, `defaultRagConfig` state updated in Redux. UI forms (e.g., in SettingsPage, Create Workspace Modal) populate with these values.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `GET /api/auth/default-rag-config`.
    *   Authenticates JWT.
    *   Retrieves user's default RAG config from PostgreSQL.
    *   Responds with RAG config object or 404.
*   **Workers**: No direct worker interaction.

**Real-time Feedback (Client-Side)**:
*   Settings forms and create workspace forms initialize with the fetched (or default) RAG configuration.

---

### Save Default RAG Config

**User Action**: User modifies RAG configuration settings on the settings page and clicks "Save Changes".

**Client-Side Flow**:
*   **UI State**: Save button disabled, loading indicator shown. RAG config form becomes read-only during save.
*   **Redux Actions**: `userSettingsSlice.updateDefaultRagConfig.pending` dispatched.
*   **API Call**:
    *   **Method**: `PUT`
    *   **Endpoint**: `/api/auth/default-rag-config` (JWT in Authorization header)
    *   **Payload**: `{"retriever_type": "vector", "embedding_model": "new-model", "chunk_size": 1500, ...}` (full RAG config object, either Vector or Graph specific)
    *   **Expected Response (Success)**: `200 OK`, `{"retriever_type": "vector", "embedding_model": "new-model", ...}` (updated config).
    *   **Expected Response (Failure)**: `400 Bad Request` (e.g., invalid values), `{"detail": "Error message"}` or `401 Unauthorized`.
*   **Error Handling**: If API fails, `userSettingsSlice.updateDefaultRagConfig.rejected` dispatched, error message displayed on UI. Form remains editable.
*   **Success Handling**: If API succeeds, `userSettingsSlice.updateDefaultRagConfig.fulfilled` dispatched, `defaultRagConfig` state updated in Redux. Success message displayed briefly. Form becomes read-only again.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `PUT /api/auth/default-rag-config`.
    *   Authenticates JWT.
    *   Validates input against RAG config schema.
    *   Updates user's default RAG config in PostgreSQL.
    *   Responds with the saved RAG config.
*   **Workers**: No direct worker interaction.

**Real-time Feedback (Client-Side)**:
*   Success/error message displayed on the settings page. Configuration changes are persisted for future workspace creations.

---

## 3. Workspace Management

### List Workspaces

**User Action**: Implicitly on application load (if authenticated) or when navigating to the workspaces list (e.g., in the left sidebar).

**Client-Side Flow**:
*   **UI State**: Workspace list shows a loading spinner.
*   **Redux Actions**: `workspaceSlice.setLoading(true)` dispatched.
*   **API Call**:
    *   **Method**: `GET`
    *   **Endpoint**: `/api/workspaces` (JWT in Authorization header)
    *   **Payload**: None
    *   **Expected Response (Success)**: `200 OK`, `[{"id": 1, "name": "Research Papers", "description": "...", "status": "ready", ...}, {...}]` (array of Workspace objects).
    *   **Expected Response (Failure)**: `401 Unauthorized` or `500 Internal Server Error`, `{"detail": "Error message"}`
*   **Error Handling**: If API fails, `workspaceSlice.setError` dispatched, error message displayed in workspace list.
*   **Success Handling**: If API succeeds, `workspaceSlice.setWorkspaces` dispatched, `workspaces` state updated in Redux. If no active workspace is set, the first workspace in the list becomes active.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `GET /api/workspaces`.
    *   Authenticates JWT.
    *   Retrieves all workspaces associated with the user from PostgreSQL.
    *   Responds with a list of workspace objects.
*   **Workers**: No direct worker interaction.

**Real-time Feedback (Client-Side)**:
*   The list of workspaces is rendered in the left sidebar. The active workspace is highlighted.

---

### Select Active Workspace

**User Action**: User clicks on a workspace in the workspace dropdown/list in the left sidebar.

**Client-Side Flow**:
*   **UI State**: The selected workspace is highlighted as active. The workspace dropdown closes.
*   **Redux Actions**: `workspaceSlice.setActiveWorkspace(workspaceId)` dispatched.
*   **API Call**: No direct API call for selection. The client updates its local state.
*   **Error Handling**: N/A.
*   **Success Handling**: `activeWorkspaceId` in Redux state is updated. This triggers re-renders in components dependent on the active workspace (e.g., `ChatBot`, `DocumentManager`, `ChatSessionList`).

**Backend/Worker Interactions (Expected)**:
*   **Server**: No direct interaction for client-side active workspace selection.
*   **Workers**: No direct interaction.

**Real-time Feedback (Client-Side)**:
*   Chat messages, document lists, and potentially RAG config displayed change to reflect the newly active workspace. Chat input and document upload buttons may enable/disable based on the *new* active workspace's processing status.

---

### Create New Workspace

**User Action**: User clicks "Create New Workspace" button, fills out the form (name, description, RAG config), and clicks "Create Workspace" in the modal.

**Client-Side Flow**:
*   **UI State**: Create Workspace modal opens. "Create Workspace" button disabled while form is invalid or during creation. Loading spinner shown during API call.
*   **Redux Actions**: `userSettingsSlice.fetchDefaultRagConfig` dispatched (to pre-populate RAG config form), `workspaceSlice.addWorkspace` dispatched on success, `workspaceSlice.setActiveWorkspace` dispatched on success.
*   **API Call**:
    *   **Method**: `POST`
    *   **Endpoint**: `/api/workspaces` (JWT in Authorization header)
    *   **Payload**: `{"name": "New Project", "description": "My new project", "rag_config": {"retriever_type": "vector", "embedding_model": "nomic-embed-text", ...}}` (includes full RAG config object).
    *   **Expected Response (Success)**: `201 Created`, `{"id": 3, "name": "New Project", "description": "...", "status": "provisioning", ...}` (new Workspace object).
    *   **Expected Response (Failure)**: `400 Bad Request` (e.g., invalid name/description/RAG config), `{"detail": "Error message"}`
*   **Error Handling**: Validation errors shown in modal. API errors set `validationError` state in modal.
*   **Success Handling**: `workspaceSlice.addWorkspace` adds new workspace to Redux state. `workspaceSlice.setActiveWorkspace` sets it as active. Modal closes.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `POST /api/workspaces`.
    *   Authenticates JWT.
    *   Validates input.
    *   Creates new workspace record in PostgreSQL with status 'provisioning'.
    *   Creates workspace RAG config record in PostgreSQL.
    *   Responds with the new workspace object.
    *   **Publishes `workspace.provision_requested` event to RabbitMQ** (payload includes workspace_id, rag_config).
*   **Worker (Orchestrator)**:
    *   Consumes `workspace.provision_requested` event.
    *   Initiates provisioning of RAG system resources (e.g., Qdrant collection, Neo4j graph structure).
    *   Sends granular status updates via WebSocket events (e.g., `workspace_status`) to the server as provisioning progresses.

**Real-time Feedback (Client-Side)**:
*   The new workspace appears in the sidebar list with a 'provisioning' status badge and a loading spinner.
*   The `workspace_status` WebSocket events from the server update the status badge in real-time until it becomes 'ready' or 'failed'.
*   Chat is locked for this workspace until status becomes 'ready'.

---

### View Workspace Details

**User Action**: User clicks on "Workspace Settings" link for the active workspace (e.g., from the workspace dropdown in the left sidebar or directly navigates to `/workspaces/{workspaceId}`).

**Client-Side Flow**:
*   **UI State**: Workspace details page loads. Loading spinner shown initially.
*   **Redux Actions**: `workspaceSlice.setActiveWorkspace` (if navigating from dropdown) to ensure correct workspace is active.
*   **API Call**:
    *   **Method**: `GET`
    *   **Endpoint**: `/api/workspaces/{workspaceId}` (JWT in Authorization header)
    *   **Payload**: None
    *   **Expected Response (Success)**: `200 OK`, `{"id": 1, "name": "Project X", "description": "...", "status": "ready", "rag_config": {...}, "document_count": 5, "session_count": 10, ...}`
    *   **Expected Response (Failure)**: `401 Unauthorized` or `404 Not Found`, `{"detail": "Error message"}`
*   **Error Handling**: Error message displayed, user redirected to `/workspaces` if workspace not found.
*   **Success Handling**: Workspace details, including RAG configuration (read-only), document count, and chat session count, are displayed. Document list and File Upload components are rendered with the `workspaceId`.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `GET /api/workspaces/{workspaceId}`.
    *   Authenticates JWT.
    *   Retrieves workspace details from PostgreSQL.
    *   Responds with the workspace object.
*   **Workers**: No direct worker interaction for viewing details.

**Real-time Feedback (Client-Side)**:
*   The `StatusBadge` for the workspace reflects its current real-time status (provisioning, ready, error, deleting).
*   `FileUpload` and `DocumentList` enable/disable based on the workspace's processing or deleting status.

---

### Edit Workspace Details

**User Action**: User clicks "Edit" button on the Workspace Details page, modifies the name or description in the modal, and clicks "Save".

**Client-Side Flow**:
*   **UI State**: Edit Workspace modal opens. "Save" button disabled while form is invalid or during saving. Loading spinner shown during API call.
*   **Redux Actions**: `workspaceSlice.updateWorkspace` dispatched on success.
*   **API Call**:
    *   **Method**: `PATCH`
    *   **Endpoint**: `/api/workspaces/{workspaceId}` (JWT in Authorization header)
    *   **Payload**: `{"name": "Updated Name", "description": "New description"}` (partial updates)
    *   **Expected Response (Success)**: `200 OK`, `{"id": 1, "name": "Updated Name", ...}` (updated Workspace object).
    *   **Expected Response (Failure)**: `400 Bad Request` (e.g., invalid name/description), `{"detail": "Error message"}`
*   **Error Handling**: Validation errors shown in modal. API errors set `editError` state in modal.
*   **Success Handling**: `workspaceSlice.updateWorkspace` updates the workspace in Redux state. Modal closes.
*   **Important Note**: RAG configuration cannot be changed via this modal. The `RagConfigForm` is `readOnly` if the workspace status is not `provisioning`. If a workspace is still `provisioning`, RAG config *could* be updated here, but current client implementation doesn't expose it for editing post-creation through this modal. It's intended to be set only during creation or via a dedicated advanced settings.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `PATCH /api/workspaces/{workspaceId}`.
    *   Authenticates JWT.
    *   Validates input.
    *   Updates workspace record in PostgreSQL.
    *   If `rag_config` is part of the payload and `isRagConfigEditable` is true, it also updates the RAG config record.
    *   Responds with the updated workspace object.
*   **Workers**: No direct worker interaction for editing workspace details.

**Real-time Feedback (Client-Side)**:
*   Workspace name/description updates in the UI.

---

### Delete Workspace

**User Action**: User clicks "Delete" button on the Workspace Details page, confirms deletion in the dialog.

**Client-Side Flow**:
*   **UI State**: Delete Confirmation dialog opens. "Delete" button disabled during deletion.
*   **Redux Actions**:
    *   `statusSlice.updateWorkspaceStatus` dispatched immediately with `status: 'deleting'` for the specific workspace.
    *   `workspaceSlice.removeWorkspace` is implicitly triggered by a `useEffect` in `WorkspaceDetailPage.tsx` when the workspace's status transitions from `deleting` to `ready` (signaling backend completion) and `isWorkspaceBeingDeleted` is true.
*   **API Call**:
    *   **Method**: `DELETE`
    *   **Endpoint**: `/api/workspaces/{workspaceId}` (JWT in Authorization header)
    *   **Payload**: None
    *   **Expected Response (Success)**: `200 OK`, `{"message": "Workspace deletion initiated"}`.
    *   **Expected Response (Failure)**: `401 Unauthorized` or `500 Internal Server Error`, `{"detail": "Error message"}`
*   **Error Handling**: If API fails, `statusSlice.updateWorkspaceStatus` sets status to 'failed', error message displayed. `removeWorkspace` is not dispatched.
*   **Success Handling**: Client receives confirmation that deletion has been initiated. UI updates (buttons disabled, status 'deleting' shown). The workspace is eventually removed from Redux and the UI, and the user is navigated to `/workspaces` after backend confirms full deletion.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `DELETE /api/workspaces/{workspaceId}`.
    *   Authenticates JWT.
    *   Updates workspace status in PostgreSQL to 'deleting'.
    *   **Publishes `workspace.deletion_requested` event to RabbitMQ** (payload includes workspace_id).
    *   Responds with initiation confirmation.
*   **Worker (Orchestrator)**:
    *   Consumes `workspace.deletion_requested` event.
    *   Initiates asynchronous cleanup of all RAG system resources (e.g., Qdrant collection, Neo4j graph) and associated documents/chat sessions in PostgreSQL.
    *   Sends granular status updates via WebSocket events (e.g., `workspace_status`) to the server as deletion progresses.
    *   Upon completion, it sends a final `workspace_status` event with `status: 'ready'` or `status: 'failed'` (if cleanup fails).

**Real-time Feedback (Client-Side)**:
*   Workspace in sidebar shows 'deleting' status badge.
*   Workspace detail page displays a "Deleting workspace..." message.
*   All interactive elements for that workspace are disabled (`Edit`, `Open in Chat`, `Delete`, `FileUpload`, `DocumentList`).
*   Upon successful backend deletion and final status update, the workspace disappears from the UI, and the user is navigated away.

---

## 4. Chat Session Management

### Create New Chat Session

**User Action**: User clicks "New Chat" button in the left sidebar (Chat Sessions column).

**Client-Side Flow**:
*   **UI State**: A new empty chat session appears in the Chat Sessions list.
*   **Redux Actions**: `chatSlice.createSession` dispatched, creating a new local chat session. `chatSlice.setActiveSession` dispatched, making the new session active.
*   **API Call**: No direct API call is made immediately. Chat sessions are managed locally until a message is sent.
*   **Error Handling**: N/A.
*   **Success Handling**: A new empty chat interface is displayed.

**Backend/Worker Interactions (Expected)**:
*   **Server**: No direct interaction until a message is sent in the new session.
*   **Workers**: No direct interaction.

**Real-time Feedback (Client-Side)**:
*   The "Chat Sessions" list updates with the new session. The chat panel displays a blank conversation.

---

### Select Active Chat Session

**User Action**: User clicks on a chat session in the left sidebar (Chat Sessions column).

**Client-Side Flow**:
*   **UI State**: The selected chat session is highlighted as active.
*   **Redux Actions**: `chatSlice.setActiveSession(sessionId)` dispatched.
*   **API Call**: No API call is made. Chat history is retrieved from local Redux state.
*   **Error Handling**: N/A.
*   **Success Handling**: The chat panel displays the messages of the selected session.

**Backend/Worker Interactions (Expected)**:
*   **Server**: No direct interaction.
*   **Workers**: No direct interaction.

**Real-time Feedback (Client-Side)**:
*   The chat panel updates to show the conversation history of the newly active session.

---

### Delete Chat Session

**User Action**: User clicks the delete icon next to a chat session in the left sidebar, and confirms deletion in the dialog.

**Client-Side Flow**:
*   **UI State**: Delete confirmation dialog opens. "Delete" button disabled during deletion.
*   **Redux Actions**: `chatSlice.deleteSession(sessionId)` dispatched.
*   **API Call**: No direct API call to delete from backend. Chat sessions are currently managed client-side only (locally).
*   **Error Handling**: N/A.
*   **Success Handling**: The chat session is removed from the Redux state and the UI. If the deleted session was active, the client typically switches to the next available session or displays an empty chat state.

**Backend/Worker Interactions (Expected)**):
*   **Server**: No direct interaction (as chat sessions are local). (Future enhancement: persist chat sessions on backend).
*   **Workers**: No direct interaction.

**Real-time Feedback (Client-Side)**:
*   The deleted chat session disappears from the "Chat Sessions" list. The chat panel updates accordingly.

---

## 5. Document Management

### Upload Document

**User Action**: User clicks the "Upload Document" button (either in the right column or triggered by the RAG Enhancement Prompt), selects a file(s) from their system
       and confirms upload.

**Client-Side Flow**:
*   **UI State**: Upload button disabled, file input disabled. Loading spinner shown next to the file name in the document list, with progress percentage if available
       Document list might be automatically refreshed.
*   **Redux Actions**: Implicitly, `statusSlice.updateDocumentStatus` is dispatched multiple times throughout the upload and processing.
*   **API Call**:
*   **Method**: `POST`
*   **Endpoint**: `/api/workspaces/{workspaceId}/documents/upload` (JWT in Authorization header)
*   **Payload**: `multipart/form-data` containing the file.
*   **Expected Response (Success)**: `200 OK`, `{"message": "Document upload initiated", "document": {"id": 101, "filename": "report.pdf", ...}}`.
*   **Expected Response (Failure)**: `400 Bad Request` (e.g., invalid file type, too large), `{"detail": "Error message"}`.
*   **Error Handling**: Error message displayed in the UI (e.g., next to the document in the list, or a toast notification). Document status updated to 'failed'.
*   **Success Handling**: Document is added to the local Redux state with 'pending' or 'parsing' status. UI updates to show the document in the list.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
*   Receives `POST /api/workspaces/{workspaceId}/documents/upload`.
*   Authenticates JWT.
*   Validates workspace access and file.
*   Saves file to BlobStorage (e.g., MinIO/S3).
*   Creates Document record in PostgreSQL with status 'pending'.
*   Responds with confirmation and initial document details.
*   **Publishes `document.uploaded` event to RabbitMQ** (payload includes document_id, workspace_id, file_path_in_blob_storage).
*   **Worker (Ingestion Worker Chain)**:
*   **Parser Worker**: Consumes `document.uploaded`. Parses document text. Publishes `document.parsed`.
*   **Chunker Worker**: Consumes `document.chunked`. Chunks text. Publishes `document.chunked`.
*   **Embedder Worker**: Consumes `document.chunked`. Generates embeddings. Publishes `document.embedded`.
*   **Indexer Worker**: Consumes `document.embedded`. Indexes vectors/graphs in Qdrant/Neo4j. Publishes `document.indexed`.
*   **All Workers**: Send granular status updates to server via `document_status` WebSocket events as they process.
*   **Server (receiving worker updates)**:
*   Updates Document `processing_status` in PostgreSQL.
*   **Emits real-time `document_status` WebSocket events to the client.**

**Real-time Feedback (Client-Side)**:
*   Document entry in the right column updates with status (`pending`, `parsing`, `chunking`, `embedding`, `indexing`, `ready`, `failed`).
*   If triggered by RAG enhancement prompt, `ChatBot` remains paused until document status becomes 'ready' for the active workspace, then retries the last query.

---

### List Documents in Workspace

**User Action**: Implicitly on switching active workspace, loading a workspace detail page, or when the DocumentManager component expands.

**Client-Side Flow**:
*   **UI State**: Document list shows a loading spinner.
*   **Redux Actions**: (Not directly a Redux action for fetching, handled locally by `DocumentList`).
*   **API Call**:
*   **Method**: `GET`
*   **Endpoint**: `/api/workspaces/{workspaceId}/documents` (JWT in Authorization header)
*   **Payload**: None
*   **Expected Response (Success)**: `200 OK`, `{"documents": [{"id": 101, "filename": "report.pdf", "status": "ready", ...}, {...}], "count": 2}`.
*   **Expected Response (Failure)**: `401 Unauthorized` or `500 Internal Server Error`, `{"detail": "Error message"}`
*   **Error Handling**: Error message displayed in document list area.
*   **Success Handling**: Document data is displayed in the list, including their current processing status. Total document count is updated.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
*   Receives `GET /api/workspaces/{workspaceId}/documents`.
*   Authenticates JWT.
*   Retrieves document records for the workspace from PostgreSQL.
*   Responds with the list of document objects.
*   **Workers**: No direct worker interaction.

**Real-time Feedback (Client-Side)**:
*   The document list updates to show the current documents and their statuses.

---

### Delete Document

**User Action**: User clicks the delete icon next to a document in the document list, and confirms deletion in the dialog.

**Client-Side Flow**:
*   **UI State**: Delete confirmation dialog opens. "Delete" button disabled during deletion.
*   **Redux Actions**: `documentSlice.removeDocument` (or similar, if persisted).
*   **API Call**:
*   **Method**: `DELETE`
*   **Endpoint**: `/api/workspaces/{workspaceId}/documents/{docId}` (JWT in Authorization header)
*   **Payload**: None
*   **Expected Response (Success)**: `200 OK`, `{"message": "Document deleted successfully"}`.
*   **Expected Response (Failure)**: `401 Unauthorized` or `404 Not Found`, `{"detail": "Error message"}`.
*   **Error Handling**: Error message displayed.
*   **Success Handling**: Document is removed from the local Redux state and the UI. Document count is updated.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
*   Receives `DELETE /api/workspaces/{workspaceId}/documents/{docId}`.
*   Authenticates JWT.
*   Deletes document record from PostgreSQL.
*   **Publishes `document.deleted` event to RabbitMQ** (payload includes document_id, workspace_id, file_path_in_blob_storage).
*   Responds with success message.
*   **Worker (Cleanup Worker)**:
*   Consumes `document.deleted` event.
*   Removes actual file from BlobStorage.
*   Removes document's vectors/graphs from Qdrant/Neo4j.
*   **Server (receiving worker updates)**:
*   Potentially sends a final `document_status` WebSocket event (e.g., `deleted`) to ensure all clients are aware.

**Real-time Feedback (Client-Side)**:
*   The deleted document disappears from the document list.

---

### Send Chat Message

**User Action**: User types a message in the chat input field and clicks "Send" or presses "Enter".

**Client-Side Flow**:
*   **UI State**: Chat input field disabled, send button disabled. User message immediately appended to chat history with a 'pending' status.
*   **Redux Actions**: `chatSlice.addMessage` dispatched to add the user's message. `chatSlice.startStreamingResponse` dispatched to indicate bot response is incoming.
*   **API Call**:
    *   **Method**: `POST`
    *   **Endpoint**: `/api/workspaces/{workspaceId}/chat/sessions/{sessionId}/messages` (JWT in Authorization header)
    *   **Payload**: `{"content": "user's message content", "message_type": "user"}`
    *   **Expected Response (Success)**: `200 OK`, `{"message": "Query received, streaming response..."}` (initial ACK). The actual bot response will be streamed via WebSocket.
    *   **Expected Response (Failure)**: `400 Bad Request` (e.g., invalid message), `{"detail": "Error message"}` or `401 Unauthorized`.
*   **Error Handling**: If API fails, `chatSlice.addMessage` might update the user message status to 'failed', or an error message toast is displayed.
*   **Success Handling**: The server acknowledges the message. The client then listens for WebSocket events for the streamed bot response.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `POST /api/workspaces/{workspaceId}/chat/sessions/{sessionId}/messages`.
    *   Authenticates JWT and authorizes workspace/session access.
    *   Stores user message in PostgreSQL.
    *   **Publishes `chat.message_received` event to RabbitMQ** (payload includes message_id, session_id, workspace_id, user_message_content).
    *   Responds with initial success message.
    *   **Emits real-time `chat.response_chunk` WebSocket events to the client** as the LLM generates the response.
    *   **Emits `chat.response_complete` or `chat.error` WebSocket events** upon completion or failure.
*   **Worker (Chat Orchestrator)**:
    *   Consumes `chat.message_received` event.
    *   Orchestrates the RAG pipeline:
        1.  Retrieves relevant context from the active workspace's RAG system (Vector Store / Graph Store) based on the user's query and chat history.
        2.  Sends the query + retrieved context to the configured LLM.
        3.  Streams LLM response chunks back to the server.
    *   If no context is found, it can trigger a `chat.no_context_found` event, leading to the RAG Enhancement Prompt on the client.

**Real-time Feedback (Client-Side)**:
*   The bot's response is streamed into the chat interface character-by-character or word-by-word.
*   A 'typing' indicator might be shown while the bot is generating a response.
*   Upon completion, the bot's full message appears, and the input field is re-enabled.
*   If `chat.no_context_found` is emitted, the RAG Enhancement Prompt appears.

### Cancel Chat Message Streaming

**User Action**: User clicks the "Cancel" button (cross icon) or presses "Ctrl+C" while the bot is streaming a response.

**Client-Side Flow**:
*   **UI State**: Bot's streaming response is immediately paused/stopped. The "Cancel" button changes back to "Send".
*   **Redux Actions**: `chatSlice.stopStreamingResponse` dispatched.
*   **API Call**:
    *   **Method**: `POST`
    *   **Endpoint**: `/api/workspaces/{workspaceId}/chat/sessions/{sessionId}/cancel` (JWT in Authorization header)
    *   **Payload**: `{"message_id": "the_message_id_being_streamed"}` (optional, if tracking specific message streams)
    *   **Expected Response (Success)**: `200 OK`, `{"message": "Streaming cancelled"}`
    *   **Expected Response (Failure)**: `400 Bad Request` or `401 Unauthorized`
*   **Error Handling**: If API fails, a console log or minor toast might appear, but UI still reflects immediate cancellation.
*   **Success Handling**: Server acknowledges cancellation. Client UI is reset.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `POST /api/workspaces/{workspaceId}/chat/sessions/{sessionId}/cancel`.
    *   Authenticates JWT.
    *   Sends a signal to the appropriate worker/LLM process to stop generating further response chunks for that specific session/message.
    *   Responds with confirmation.
*   **Worker (Chat Orchestrator)**:
    *   Receives cancellation signal.
    *   Aborts the ongoing LLM generation and any further RAG processing for that message.

**Real-time Feedback (Client-Side)**:
*   The bot's partial response stops rendering. The chat input becomes active again.

### RAG Enhancement Prompt (No Context Found)

**User Action**: After a query yields no relevant context, the RAG Enhancement Prompt appears with options.

**Client-Side Flow**:
*   **UI State**: Chat input disabled. Prompt options ("Upload a Document", "Fetch from Wikipedia", "Continue without additional context") are displayed.
*   **Redux Actions**: `chatSlice.setEnhancementPromptVisible(true)` dispatched.
*   **API Call**: No direct API call is made; this is a client-side prompt based on a WebSocket event (`chat.no_context_found`).
*   **Error Handling**: N/A.
*   **Success Handling**: N/A.

**Backend/Worker Interactions (Expected)**:
*   **Server**: Emits `chat.no_context_found` WebSocket event to the client based on worker feedback.
*   **Workers**: Chat Orchestrator worker determines no context was found for the user's query and signals the server.

**Real-time Feedback (Client-Side)**:
*   The chat interface pauses, displaying the prompt options.

#### Action: Upload a Document (from Prompt)

**User Action**: User clicks "Upload a Document" from the RAG Enhancement Prompt, selects a file(s), and confirms.

**Client-Side Flow**:
*   **UI State**: Prompt options are replaced by the file upload interface or a modal. Upload progress displayed.
*   **Redux Actions**: `chatSlice.setEnhancementPromptVisible(false)` dispatched. (Further actions mirror `Upload Document` flow).
*   **API Call**: (Mirrors `Upload Document` flow).
*   **Expected Response (Success)**: (Mirrors `Upload Document` flow).
*   **Expected Response (Failure)**: (Mirrors `Upload Document` flow).
*   **Error Handling**: (Mirrors `Upload Document` flow).
*   **Success Handling**: Upon successful upload and document processing (`document_status: 'ready'`), the client automatically re-sends the original query that triggered the prompt.

**Backend/Worker Interactions (Expected)**:
*   **Server**: (Mirrors `Upload Document` flow).
*   **Workers**: (Mirrors `Upload Document` flow).

**Real-time Feedback (Client-Side)**:
*   Document processing status updates are shown. Once ready, the chat re-submits the query.

#### Action: Fetch from Wikipedia (from Prompt)

**User Action**: User clicks "Fetch from Wikipedia" from the RAG Enhancement Prompt.

**Client-Side Flow**:
*   **UI State**: Prompt options are replaced by a loading indicator.
*   **Redux Actions**: `chatSlice.setEnhancementPromptVisible(false)` dispatched.
*   **API Call**:
    *   **Method**: `POST`
    *   **Endpoint**: `/api/workspaces/{workspaceId}/documents/fetch-wikipedia` (JWT in Authorization header)
    *   **Payload**: `{"query": "original user query"}`
    *   **Expected Response (Success)**: `200 OK`, `{"message": "Wikipedia fetch initiated"}`.
    *   **Expected Response (Failure)**: `400 Bad Request` or `401 Unauthorized`.
*   **Error Handling**: Error message displayed in chat.
*   **Success Handling**: Client awaits `wikipedia_fetch_status` WebSocket events.

**Backend/Worker Interactions (Expected)**:
*   **Server**:
    *   Receives `POST /api/workspaces/{workspaceId}/documents/fetch-wikipedia`.
    *   Authenticates JWT.
    *   **Publishes `wikipedia.fetch_requested` event to RabbitMQ** (payload includes query, workspace_id).
    *   Responds with initiation confirmation.
*   **Worker (Wikipedia Worker)**:
    *   Consumes `wikipedia.fetch_requested` event.
    *   Searches Wikipedia for the query.
    *   Fetches relevant content.
    *   Creates new document record(s) from Wikipedia content (mirroring `Upload Document`'s ingestion chain).
    *   Sends granular status updates via `wikipedia_fetch_status` WebSocket events.

**Real-time Feedback (Client-Side)**:
*   Loading indicator shown. `wikipedia_fetch_status` events update UI. Once content is processed (`document_status: 'ready'`), the chat re-submits the query.

#### Action: Continue without additional context (from Prompt)

**User Action**: User clicks "Continue without additional context" from the RAG Enhancement Prompt.

**Client-Side Flow**:
*   **UI State**: Prompt options disappear. Chat input re-enabled.
*   **Redux Actions**: `chatSlice.setEnhancementPromptVisible(false)` dispatched. The original user query is re-submitted, but this time with a flag indicating to the server to *not* attempt RAG retrieval (or proceed with minimal context).
*   **API Call**: (Mirrors `Send Chat Message` flow, but with an additional flag in payload, e.g., `"ignore_rag": true`).
*   **Expected Response (Success)**: (Mirrors `Send Chat Message` flow).
*   **Expected Response (Failure)**: (Mirrors `Send Chat Message` flow).
*   **Error Handling**: (Mirrors `Send Chat Message` flow).
*   **Success Handling**: (Mirrors `Send Chat Message` flow).

**Backend/Worker Interactions (Expected)**:
*   **Server**: Receives message, passes the `ignore_rag` flag to the worker.
*   **Worker (Chat Orchestrator)**: Processes the query, but bypasses or minimizes RAG retrieval based on the `ignore_rag` flag.

**Real-time Feedback (Client-Side)**:
*   The bot provides a response, potentially less informed if no context was found.

---

## 7. Real-time Status Updates (WebSocket)

### Document Status Updates

**WebSocket Event**: `document_status`

**Client-Side Flow**:
*   **Event Listener**: Client (e.g., `socketService`, `DocumentManager` component) listens for `document_status` events.
*   **Data Structure (Expected)**: `{"document_id": "uuid", "workspace_id": "uuid", "status": "pending" | "parsing" | "chunking" | "embedding" | "indexing" | "ready" | "failed" | "deleted", "message": "Optional status message"}`
*   **Redux Actions**: `statusSlice.updateDocumentStatus` dispatched with the received status update.
*   **Error Handling**: If `status` is "failed", an error message might be displayed to the user.
*   **Success Handling**: UI (e.g., `DocumentList`) updates the status badge/indicator for the specific document.

**Backend/Worker Interactions (Expected)**:
*   **Server**: Receives status updates from Ingestion Workers (Parser, Chunker, Embedder, Indexer) and immediately emits them as `document_status` WebSocket events to relevant clients (users subscribed to that workspace).
*   **Workers**: After completing each stage of document processing (parsing, chunking, embedding, indexing), workers send a status update to the server.

**Real-time Feedback (Client-Side)**:
*   Document status is dynamically updated in the `DocumentList` as it progresses through ingestion.

### Workspace Status Updates

**WebSocket Event**: `workspace_status`

**Client-Side Flow**:
*   **Event Listener**: Client (e.g., `socketService`, `WorkspaceColumn`, `WorkspaceDetailPage`) listens for `workspace_status` events.
*   **Data Structure (Expected)**: `{"workspace_id": "uuid", "status": "provisioning" | "ready" | "deleting" | "failed", "message": "Optional status message"}`
*   **Redux Actions**: `statusSlice.updateWorkspaceStatus` dispatched. If `status` becomes "ready" after a "provisioning" state, it might trigger `workspaceSlice.setWorkspaceReady`. If `status` becomes "ready" after a "deleting" state, it triggers `workspaceSlice.removeWorkspace`.
*   **Error Handling**: If `status` is "failed", an error message related to workspace provisioning/deletion is displayed.
*   **Success Handling**: UI (e.g., workspace name in sidebar, `WorkspaceDetailPage`) updates the status badge/indicator for the specific workspace.

**Backend/Worker Interactions (Expected)**:
*   **Server**: Receives status updates from the Orchestrator Worker regarding workspace provisioning or deletion and immediately emits them as `workspace_status` WebSocket events.
*   **Worker (Orchestrator)**: Sends status updates to the server as it provisions or deletes workspace resources.

**Real-time Feedback (Client-Side)**:
*   Workspace status is dynamically updated (e.g., 'provisioning' with a spinner, 'ready' with a checkmark, 'deleting' with a warning). Interactive elements for the workspace may enable/disable based on its status.

### Wikipedia Fetch Status Updates

**WebSocket Event**: `wikipedia_fetch_status`

**Client-Side Flow**:
*   **Event Listener**: Client (e.g., `socketService`, `ChatBot` component) listens for `wikipedia_fetch_status` events.
*   **Data Structure (Expected)**: `{"workspace_id": "uuid", "query": "string", "status": "fetching" | "processing" | "completed" | "failed", "document_ids": ["uuid", ...], "message": "Optional status message"}`
*   **Redux Actions**: `statusSlice.updateWikipediaFetchStatus` dispatched.
*   **Error Handling**: If `status` is "failed", an error message is displayed in the chat.
*   **Success Handling**: UI (e.g., `ChatBot`) updates its display to show fetching progress, then re-submits the original query if `status` is "completed".

**Backend/Worker Interactions (Expected)**:
*   **Server**: Receives status updates from the Wikipedia Worker and immediately emits them as `wikipedia_fetch_status` WebSocket events.
*   **Worker (Wikipedia Worker)**: Sends status updates to the server as it searches, fetches, and initiates ingestion of Wikipedia content.

**Real-time Feedback (Client-Side)**:
*   A loading indicator or status message is shown in the chat area while Wikipedia content is being fetched and processed. Once completed, the chat automatically re-queries.

---
