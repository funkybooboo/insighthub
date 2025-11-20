# Workspace Feature Documentation

## Overview

The Workspace feature enables users to organize their documents and chat sessions into isolated environments. Each workspace has its own:

- Document collection
- Chat sessions
- RAG configuration (embedding model, retriever type, chunking strategy)

## Architecture

### Data Model

```typescript
interface Workspace {
    id: number;
    name: string;
    description?: string;
    created_at: string;
    updated_at: string;
    rag_config?: RagConfig;
    document_count?: number;
    session_count?: number;
}

interface RagConfig {
    id: number;
    workspace_id: number;
    embedding_model: string;
    retriever_type: string;
    chunk_size: number;
    chunk_overlap?: number;
    top_k?: number;
    created_at: string;
    updated_at: string;
}
```

### Components

#### WorkspaceSelector

Located at: `src/components/workspace/WorkspaceSelector.tsx`

**Purpose**: Allows users to switch between workspaces and create new ones.

**Features**:
- Dropdown to select active workspace
- Create new workspace button
- Modal form for workspace creation
- Input validation (name, description)
- Persists active workspace to localStorage

**Props**: None (uses Redux state)

**Usage**:
```tsx
import WorkspaceSelector from './components/workspace/WorkspaceSelector';

<WorkspaceSelector />
```

#### WorkspaceSettings

Located at: `src/components/workspace/WorkspaceSettings.tsx`

**Purpose**: Configure workspace metadata and RAG settings.

**Features**:
- Edit workspace name and description
- Configure RAG parameters:
  - Embedding model (nomic-embed-text, openai, sentence-transformer)
  - Retriever type (vector, graph)
  - Chunk size (100-5000)
  - Chunk overlap (0-1000)
  - Top K results (1-20)
- Delete workspace (with confirmation)
- Input validation on all fields

**Props**: None (uses Redux state)

**Usage**:
```tsx
import WorkspaceSettings from './components/workspace/WorkspaceSettings';

<WorkspaceSettings />
```

### State Management

The workspace state is managed using Redux Toolkit in `src/store/slices/workspaceSlice.ts`.

#### State Shape

```typescript
interface WorkspaceState {
    workspaces: Workspace[];
    activeWorkspaceId: number | null;
    isLoading: boolean;
    error: string | null;
}
```

#### Actions

- `setWorkspaces(workspaces: Workspace[])` - Set the full workspace list
- `addWorkspace(workspace: Workspace)` - Add a new workspace
- `updateWorkspace(workspace: Workspace)` - Update an existing workspace
- `removeWorkspace(id: number)` - Remove a workspace
- `setActiveWorkspace(id: number)` - Set the active workspace
- `setLoading(isLoading: boolean)` - Set loading state
- `setError(error: string | null)` - Set error message
- `clearError()` - Clear error message

#### Selectors

```typescript
// Get all workspaces
const workspaces = useSelector((state: RootState) => state.workspace.workspaces);

// Get active workspace ID
const activeWorkspaceId = useSelector((state: RootState) => state.workspace.activeWorkspaceId);

// Get active workspace object
const activeWorkspace = useSelector((state: RootState) => 
    state.workspace.workspaces.find(w => w.id === state.workspace.activeWorkspaceId)
);
```

### API Integration

Workspace API methods are defined in `src/services/api.ts`:

```typescript
// List all workspaces
await apiService.listWorkspaces();

// Get specific workspace
await apiService.getWorkspace(workspaceId);

// Create workspace
await apiService.createWorkspace({
    name: 'Research Papers',
    description: 'Academic papers on RAG'
});

// Update workspace
await apiService.updateWorkspace(workspaceId, {
    name: 'Updated Name'
});

// Delete workspace
await apiService.deleteWorkspace(workspaceId);

// Get RAG config
await apiService.getRagConfig(workspaceId);

// Create RAG config
await apiService.createRagConfig(workspaceId, {
    embedding_model: 'nomic-embed-text',
    retriever_type: 'vector',
    chunk_size: 1000,
    chunk_overlap: 200,
    top_k: 5
});

// Update RAG config
await apiService.updateRagConfig(workspaceId, {
    chunk_size: 1500
});
```

## Input Validation

All user inputs are validated using the validation utilities in `src/lib/validation.ts`:

### Workspace Name Validation

- Required
- Minimum 3 characters
- Maximum 100 characters
- Allowed characters: letters, numbers, spaces, hyphens, underscores

### Description Validation

- Optional
- Maximum 500 characters

### RAG Configuration Validation

- **Chunk Size**: 100-5000
- **Chunk Overlap**: 0-1000
- **Top K**: 1-20

## User Workflow

### Creating a Workspace

1. Click the "+" button in the WorkspaceSelector
2. Enter workspace name (required, 3-100 chars)
3. Optionally enter description (max 500 chars)
4. Click "Create"
5. New workspace becomes active automatically if it's the first one

### Switching Workspaces

1. Click the workspace dropdown in WorkspaceSelector
2. Select desired workspace
3. Active workspace ID is persisted to localStorage
4. All document and chat operations now apply to the selected workspace

### Configuring Workspace

1. Click the settings icon next to the workspace selector
2. Modify workspace name and description
3. Configure RAG parameters
4. Click "Save Changes"

### Deleting a Workspace

1. Open workspace settings
2. Click "Delete Workspace"
3. Confirm deletion in the dialog
4. All associated documents and chat sessions are deleted
5. If deleted workspace was active, switches to first remaining workspace

## Testing

### Unit Tests

Located at:
- `src/store/slices/workspaceSlice.test.ts` - Redux slice tests
- `src/components/workspace/WorkspaceSelector.test.tsx` - Component tests
- `src/lib/validation.test.ts` - Validation utility tests
- `src/services/api.test.ts` - API service tests

Run tests:
```bash
task test
# or
bun run test:run
```

### Storybook Stories

Located at:
- `src/components/workspace/WorkspaceSelector.stories.tsx`
- `src/components/workspace/WorkspaceSettings.stories.tsx`

Run Storybook:
```bash
task storybook
# or
bun run storybook
```

## Security Considerations

### Input Sanitization

All user inputs are validated and sanitized:
- Maximum length limits prevent buffer overflow attacks
- Character whitelisting prevents injection attacks
- HTML/script tags are not allowed in any text fields

### API Authentication

All API requests include authentication headers:
- JWT token stored in localStorage
- Automatically included in all requests via Axios interceptor
- 401 responses trigger automatic logout and redirect to login

### Authorization

Backend enforces workspace ownership:
- Users can only access their own workspaces
- Workspace ID validation on all operations
- Cascading deletes ensure data consistency

## Performance Optimizations

### State Management

- Active workspace ID persisted to localStorage to avoid re-fetching on page reload
- Workspace list cached in Redux to minimize API calls
- Optimistic updates for better UX

### Component Rendering

- React.memo could be applied to WorkspaceSelector if re-render performance becomes an issue
- Form state managed locally to avoid Redux updates on every keystroke

## Future Enhancements

### Planned Features

1. **Workspace Templates**: Pre-configured workspace settings for common use cases
2. **Workspace Sharing**: Allow multiple users to collaborate in shared workspaces
3. **Workspace Import/Export**: Backup and restore workspace configurations
4. **Workspace Analytics**: Usage statistics and insights per workspace
5. **Workspace Tags**: Organize workspaces with custom tags and filters

### API Improvements

1. Bulk workspace operations
2. Workspace search and filtering
3. Workspace activity logs
4. Workspace quotas and limits
