# InsightHub Client User Flows and API Interactions

This document provides a detailed breakdown of every significant user action within the InsightHub React Frontend, mapping the client-side flow, API interactions, and expected backend/worker behaviors. This level of detail aims to clarify the full application flow for developers working on the server and worker components.

**Note**: This documentation is based on the actual implementation in the codebase as of the current version. Some advanced features (like Graph RAG, dedicated chat orchestrator workers, and Wikipedia fetching) are planned but not yet fully implemented. The current implementation focuses on Vector RAG with asynchronous document processing.

---

## Table of Contents

1.  [User Authentication](#1-user-authentication)
     *   [User Login](#user-login)
     *   [User Signup](#user-signup)
     *   [User Logout](#user-logout)
     *   [Get Current User Profile](#get-current-user-profile)
     *   [Update User Profile](#update-user-profile)
     *   [Update User Preferences (e.g., Theme)](#update-user-preferences-eg-theme)
     *   [Change User Password](#change-user-password)
2.  [Default RAG Configuration Management](#2-default-rag-configuration-management)
     *   [Fetch Default RAG Config](#fetch-default-rag-config)
     *   [Save Default RAG Config](#save-default-rag-config)
3.  [Workspace Management](#3-workspace-management)
     *   [List Workspaces](#list-workspaces)
     *   [Select Active Workspace](#select-active-workspace)
     *   [Create New Workspace](#create-new-workspace)
     *   [View Workspace Details](#view-workspace-details)
     *   [Edit Workspace Details](#edit-workspace-details)
     *   [Delete Workspace](#delete-workspace)
4.  [Chat Session Management](#4-chat-session-management)
     *   [Create New Chat Session](#create-new-chat-session)
     *   [Select Active Chat Session](#select-active-chat-session)
     *   [Delete Chat Session](#delete-chat-session)
5.  [Document Management](#5-document-management)
     *   [Upload Document](#upload-document)
     *   [List Documents in Workspace](#list-documents-in-workspace)
     *   [Delete Document](#delete-document)
6.  [Chat Interaction](#6-chat-interaction)
     *   [Send Chat Message](#send-chat-message)
     *   [Cancel Chat Message Streaming](#cancel-chat-message-streaming)
     *   [RAG Enhancement Prompt (No Context Found)](#rag-enhancement-prompt-no-context-found)
         *   [Action: Upload a Document (from Prompt)](#action-upload-a-document-from-prompt)
         *   [Action: Fetch from Wikipedia (from Prompt)](#action-fetch-from-wikipedia-from-prompt)
         *   [Action: Continue without additional context (from Prompt)](#action-continue-without-additional-context-from-prompt)
7.  [Real-time Status Updates (WebSocket)](#7-real-time-status-updates-websocket)
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
*   **Server** (`packages/server/src/domains/auth/routes.py`):
    *   Receives `POST /api/auth/login`.
    *   Validates credentials against PostgreSQL user records using `UserService`.
    *   If valid, generates a JWT using `jwt_utils.py`.
    *   Responds with JWT and user details.
*   **Workers**: No direct worker interaction for login.

**Real-time Feedback (Client-Side)**:
*   Upon successful login, the client connects to the WebSocket server via `socketService`.
*   `socketService.onConnected` event confirms connection.

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
*   **Server** (`packages/server/src/domains/workspaces/routes.py`):
    *   Receives `POST /api/workspaces`.
    *   Authenticates JWT using middleware.
    *   Validates input using `WorkspaceService`.
    *   Creates new workspace record in PostgreSQL with status 'provisioning'.
    *   Creates workspace RAG config record in PostgreSQL.
    *   Responds with the new workspace object.
    *   **Publishes `workspace.provision_requested` event to RabbitMQ** via `message_publisher`.
*   **Worker (Provisioner)** (`packages/workers/provisioner/`):
    *   Consumes `workspace.provision_requested` event.
    *   Creates Qdrant collection for the workspace.
    *   Sends status updates via WebSocket events (`workspace_status`) to the server.

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
*   **Worker (Deletion Worker)** (`packages/workers/deletion/`):
    *   Consumes `workspace.deletion_requested` event.
    *   Cleans up RAG system resources (Qdrant collection) and associated data.
    *   Sends status updates via `workspace_status` WebSocket events.

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
*   **API Call**: No direct API call. Chat sessions are managed locally until a message is sent.
*   **Success Handling**: A new empty chat interface is displayed.

**Backend/Worker Interactions**:
*   **Server**: No direct interaction until a message is sent.
*   **Workers**: No direct interaction.

**Real-time Feedback (Client-Side)**:
*   The "Chat Sessions" list updates with the new session. The chat panel displays a blank conversation.

---

### Select Active Chat Session

**User Action**: User clicks on a chat session in the left sidebar (Chat Sessions column).

**Client-Side Flow**:
*   **UI State**: The selected chat session is highlighted as active.
*   **Redux Actions**: `chatSlice.setActiveSession(sessionId)` dispatched.
*   **API Call**: No API call. Chat history retrieved from local Redux state.
*   **Success Handling**: The chat panel displays the messages of the selected session.

**Backend/Worker Interactions**:
*   **Server**: No direct interaction.
*   **Workers**: No direct interaction.

**Real-time Feedback (Client-Side)**:
*   The chat panel updates to show the conversation history of the newly active session.

---

### Delete Chat Session

**User Action**: User clicks the delete icon next to a chat session in the left sidebar, and confirms deletion.

**Client-Side Flow**:
*   **UI State**: Delete confirmation dialog opens.
*   **Redux Actions**: `chatSlice.deleteSession(sessionId)` dispatched.
*   **API Call**: No API call. Chat sessions are currently managed client-side only.
*   **Success Handling**: The chat session is removed from Redux state and UI.

**Backend/Worker Interactions**:
*   **Server**: No direct interaction (chat sessions are local).
*   **Workers**: No direct interaction.

**Real-time Feedback (Client-Side)**:
*   The deleted chat session disappears from the "Chat Sessions" list. The chat panel updates accordingly.

---

## 5. Document Management

### Upload Document

**User Action**: User clicks the "Upload Document" button, selects a file(s) from their system and confirms upload.

**Client-Side Flow**:
*   **UI State**: Upload button disabled, file input disabled. Loading spinner shown next to the file name in the document list.
*   **Redux Actions**: `statusSlice.updateDocumentStatus` dispatched multiple times during processing.
*   **API Call**:
    *   **Method**: `POST`
    *   **Endpoint**: `/api/workspaces/{workspaceId}/documents/upload` (JWT in Authorization header)
    *   **Payload**: `multipart/form-data` containing the file.
    *   **Expected Response (Success)**: `200 OK`, `{"message": "Document upload initiated", "document": {"id": 101, "filename": "report.pdf", ...}}`.
    *   **Expected Response (Failure)**: `400 Bad Request` (e.g., invalid file type, too large), `{"detail": "Error message"}`.
*   **Error Handling**: Error message displayed in the UI. Document status updated to 'failed'.
*   **Success Handling**: Document added to Redux state with 'pending' status. UI shows document in list.

**Backend/Worker Interactions (Expected)**:
*   **Server** (`packages/server/src/domains/workspaces/documents/routes.py`):
    *   Receives `POST /api/workspaces/{workspaceId}/documents/upload`.
    *   Authenticates JWT.
    *   Validates workspace access and file.
    *   Saves file to MinIO/S3 via `BlobStorage`.
    *   Creates Document record in PostgreSQL with status 'pending'.
    *   Responds with confirmation and initial document details.
    *   **Publishes `document.uploaded` event to RabbitMQ** via `message_publisher`.
*   **Worker (Parser)** (`packages/workers/parser/`):
    *   Consumes `document.uploaded` event.
    *   Extracts text from PDF/DOCX using document parsers from shared library.
    *   Updates document record with extracted text.
    *   **Publishes `document.parsed` event** to RabbitMQ.
*   **Worker (Chunker)** (`packages/workers/chucker/`):
    *   Consumes `document.parsed` event.
    *   Splits text into chunks using chunking strategies from shared library.
    *   **Publishes `document.chunked` event** to RabbitMQ.
*   **Worker (Embedder)** (`packages/workers/embedder/`):
    *   Consumes `document.chunked` event.
    *   Generates vector embeddings using Ollama/Sentence Transformers.
    *   **Publishes `document.embedded` event** to RabbitMQ.
*   **Worker (Indexer)** (`packages/workers/indexer/`):
    *   Consumes `document.embedded` event.
    *   Stores vectors in Qdrant collection for the workspace.
    *   **Publishes `document.indexed` event** to RabbitMQ.
*   **Server (Status Consumer)** (`api.py`):
    *   Receives status updates from workers via `status_consumer`.
    *   Updates Document `processing_status` in PostgreSQL.
    *   **Emits real-time `document_status` WebSocket events to the client.**

**Real-time Feedback (Client-Side)**:
*   Document entry in the right column updates with status (`pending`, `parsing`, `chunking`, `embedding`, `indexing`, `ready`, `failed`).
*   If triggered by RAG enhancement prompt, `ChatBot` waits until document status becomes 'ready', then auto-retries the last query.

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

## 6. Chat Interaction

### Send Chat Message

**User Action**: User types a message in the chat input field and clicks "Send" or presses "Enter".

**Client-Side Flow**:
*   **UI State**: Chat input field disabled, send button disabled. User message immediately appended to chat history.
*   **Redux Actions**: `chatSlice.addMessageToSession` dispatched to add the user's message. `chatSlice.setTyping(true)` dispatched.
*   **WebSocket Call**:
    *   **Event**: `chat_message`
    *   **Payload**: `{"message": "user's message content", "session_id": 123, "workspace_id": 456, "rag_type": "vector"}`
*   **Error Handling**: If WebSocket fails, error message displayed.
*   **Success Handling**: Client listens for WebSocket events for the streamed bot response.

**Backend/Worker Interactions (Expected)**:
*   **Server** (`packages/server/src/domains/workspaces/chat/routes.py`):
    *   Receives WebSocket `chat_message` event.
    *   Authenticates JWT and authorizes workspace/session access.
    *   Stores user message in PostgreSQL via `ChatService`.
    *   **Publishes `chat.message_received` event to RabbitMQ** via `message_publisher`.
    *   Chat worker processes the message asynchronously.
*   **Worker (Chat Worker)** (`packages/workers/chat/`):
    *   Consumes `chat.message_received` event.
    *   Performs RAG retrieval using `VectorRAG` from shared library.
    *   Calls LLM (Ollama/OpenAI) with retrieved context.
    *   **Publishes response chunks** via `chat.response_chunk` events to RabbitMQ.
    *   **Publishes completion** via `chat.response_complete` event.
*   **Server (Event Consumer)** (`api.py`):
    *   Receives chat events from RabbitMQ via `chat_event_consumer`.
    *   Forwards `chat.response_chunk` events as WebSocket events to client.
    *   Forwards `chat.response_complete` event to client.

**Real-time Feedback (Client-Side)**:
*   The bot's response is streamed into the chat interface token-by-token.
*   Typing indicator shown while bot is generating response.
*   Upon completion, bot's full message appears, input field re-enabled.
*   If no context found, `chat.no_context_found` event triggers RAG Enhancement Prompt.

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
*   **Worker (Chat Worker)**:
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

**Backend/Worker Interactions**:
*   **Server**: Emits `chat.no_context_found` WebSocket event to the client based on worker feedback.
*   **Workers**: Chat worker determines no context was found and publishes `chat.no_context_found` event.

**Real-time Feedback (Client-Side)**:
*   The chat interface pauses, displaying the prompt options.

#### Action: Upload a Document (from Prompt)

**User Action**: User clicks "Upload a Document" from the RAG Enhancement Prompt, selects a file(s), and confirms.

**Client-Side Flow**:
*   **UI State**: Prompt options replaced by file upload interface. Upload progress displayed.
*   **Redux Actions**: `chatSlice.setEnhancementPromptVisible(false)` dispatched.
*   **API Call**: Same as `Upload Document` flow.
*   **Success Handling**: Upon successful upload and document processing (`document_status: 'ready'`), the client automatically re-sends the original query.

**Backend/Worker Interactions**:
*   **Server**: Same as `Upload Document` flow.
*   **Workers**: Same as `Upload Document` flow.
*   **Auto-retry**: When document becomes 'ready', `ChatService.retry_pending_rag_queries()` is called to re-run the original query with new context.

**Real-time Feedback (Client-Side)**:
*   Document processing status updates shown. Once ready, chat automatically retries the query without user intervention.

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
*   **Redux Actions**: `chatSlice.setEnhancementPromptVisible(false)` dispatched.
*   **WebSocket Call**: Re-sends the original query with `ignore_rag: true` flag.
*   **Success Handling**: Chat proceeds with LLM response without RAG context.

**Backend/Worker Interactions**:
*   **Server**: Receives message with `ignore_rag: true` flag.
*   **Chat Worker**: Processes query but skips RAG retrieval, calls LLM directly.

**Real-time Feedback (Client-Side)**:
*   Bot provides response without retrieved context (may be less informed).

---

## 7. Real-time Status Updates (WebSocket)

### Document Status Updates

**WebSocket Event**: `document_status`

**Client-Side Flow**:
*   **Event Listener**: `socketService` listens for `document_status` events.
*   **Data Structure**: `{"document_id": 123, "workspace_id": 456, "status": "pending" | "parsing" | "chunking" | "embedding" | "indexing" | "ready" | "failed", "message": "Optional status message"}`
*   **Redux Actions**: `statusSlice.updateDocumentStatus` dispatched.
*   **Error Handling**: If `status` is "failed", error message displayed.
*   **Success Handling**: `DocumentList` updates status badge for the specific document.

**Backend/Worker Interactions**:
*   **Server** (`api.py` status consumer): Receives status updates from workers and emits `document_status` WebSocket events.
*   **Workers**: Parser, Chunker, Embedder, Indexer workers send status updates after each processing stage.

**Real-time Feedback (Client-Side)**:
*   Document status dynamically updated in `DocumentList` as it progresses through ingestion pipeline.

### Workspace Status Updates

**WebSocket Event**: `workspace_status`

**Client-Side Flow**:
*   **Event Listener**: `socketService` listens for `workspace_status` events.
*   **Data Structure**: `{"workspace_id": 123, "status": "provisioning" | "ready" | "deleting" | "failed", "message": "Optional status message"}`
*   **Redux Actions**: `statusSlice.updateWorkspaceStatus` dispatched.
*   **Error Handling**: If `status` is "failed", error message displayed.
*   **Success Handling**: Workspace status updated in sidebar and detail pages.

**Backend/Worker Interactions**:
*   **Server** (`api.py` status consumer): Receives status updates from provisioner/deletion workers and emits `workspace_status` WebSocket events.
*   **Provisioner Worker**: Sends status updates during workspace creation (Qdrant collection setup).

**Real-time Feedback (Client-Side)**:
*   Workspace status dynamically updated with spinners/badges. Interactive elements enable/disable based on status.

### Chat Streaming Events

**WebSocket Events**: `chat_chunk`, `chat_complete`, `chat_error`, `chat_no_context_found`

**Client-Side Flow**:
*   **Event Listener**: `socketService` forwards events to `ChatBot` component.
*   **Data Structures**:
    *   `chat_chunk`: `{"chunk": "token_text"}`
    *   `chat_complete`: `{"session_id": 123, "full_response": "complete response"}`
    *   `chat_error`: `{"error": "error message"}`
    *   `chat_no_context_found`: Triggers RAG enhancement prompt
*   **Redux Actions**: `chatSlice.updateMessageInSession` for chunks, `chatSlice.setTyping(false)` on complete.
*   **Success Handling**: Chat interface streams response token-by-token, then shows complete message.

**Backend/Worker Interactions**:
*   **Chat Worker**: Publishes `chat.response_chunk`/`chat.response_complete` events to RabbitMQ.
*   **Server** (`api.py` chat event consumer): Forwards events as WebSocket events to client.

**Real-time Feedback (Client-Side)**:
*   Response streams character-by-character in chat interface with typing indicator.

### Wikipedia Fetch Status Updates

**WebSocket Event**: `wikipedia_fetch_status`

**Client-Side Flow**:
*   **Event Listener**: `socketService` listens for `wikipedia_fetch_status` events.
*   **Data Structure**: `{"workspace_id": 123, "query": "search query", "status": "fetching" | "processing" | "completed" | "failed", "document_ids": [456], "message": "status message"}`
*   **Redux Actions**: `statusSlice.updateWikipediaFetchStatus` dispatched.
*   **Error Handling**: Error message displayed in chat.
*   **Success Handling**: On completion, chat auto-retries the original query with new context.

**Backend/Worker Interactions**:
*   **Wikipedia Worker** (`packages/workers/wikipedia/`): Fetches content, creates documents, goes through ingestion pipeline.
*   **Server**: Emits `wikipedia_fetch_status` events based on worker progress.

**Real-time Feedback (Client-Side)**:
*   Loading indicator shown in chat while Wikipedia content is fetched and processed.

---

## Implementation Status

### Currently Implemented
- **Vector RAG**: Full implementation with Qdrant, Ollama, and configurable chunking
- **Document Processing Pipeline**: Parser -> Chucker -> Embedder -> Indexer workers
- **Real-time Chat**: WebSocket streaming with async processing via chat worker
- **Workspace Management**: Creation, configuration, and basic provisioning
- **Authentication**: JWT-based auth with user profiles and preferences
- **Status Updates**: Real-time WebSocket events for document/workspace processing

### Planned/Not Yet Implemented
- **Graph RAG**: Neo4j-based graph retrieval (shared library has interfaces but no implementation)
- **Wikipedia Fetching**: Worker exists but integration not complete
- **Advanced RAG Features**: Re-ranking, query expansion, multi-modal support
- **Chat Session Persistence**: Currently client-side only
- **Workspace Deletion**: Basic framework exists but full cleanup not implemented

### Key Architecture Patterns
- **Clean Architecture**: Presentation -> Domain -> Infrastructure layers
- **Factory Pattern**: Pluggable RAG components and service instantiation
- **Repository Pattern**: Abstracted data access with SQL implementations
- **Observer Pattern**: Real-time status updates via WebSocket events
- **Dependency Injection**: Services receive dependencies via constructors

This documentation reflects the actual implementation as of the current codebase. Some features may be partially implemented or use simplified approaches compared to the full planned architecture.
