import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export type DocumentStatus = 'pending' | 'parsing' | 'chunking' | 'embedding' | 'indexing' | 'ready' | 'failed';
export type WorkspaceStatus = 'provisioning' | 'ready' | 'error' | 'deleting';
export type WikipediaFetchStatus = 'pending' | 'fetching' | 'processing' | 'ready' | 'failed'; // New status type

interface DocumentStatusUpdate {
    document_id: number;
    user_id: number;
    workspace_id: number | null;
    status: DocumentStatus;
    error: string | null;
    chunk_count: number | null;
    filename: string;
    metadata?: Record<string, unknown>; // Made optional as it might not always be present
    progress?: number; // Added for percentage progress
    message?: string; // Added for more detailed messages
}

interface WorkspaceStatusUpdate {
    workspace_id: number;
    user_id: number;
    status: WorkspaceStatus;
    message: string | null;
    name?: string; // Made optional as it might not always be present
    metadata?: Record<string, unknown>; // Made optional
}

// New interface for Wikipedia fetch status updates
interface WikipediaFetchStatusUpdate {
    id: string; // Unique ID for the fetch operation, e.g., combination of workspaceId and query timestamp
    user_id: number;
    workspace_id: number;
    query: string;
    status: WikipediaFetchStatus;
    message: string | null;
    error: string | null;
    timestamp: number;
}

interface StatusState {
    documents: Record<number, DocumentStatusUpdate>;
    workspaces: Record<number, WorkspaceStatusUpdate>;
    wikipediaFetches: Record<string, WikipediaFetchStatusUpdate>; // New field for Wikipedia fetches
}

const initialState: StatusState = {
    documents: {},
    workspaces: {},
    wikipediaFetches: {}, // Initialize new field
};

const statusSlice = createSlice({
    name: 'status',
    initialState,
    reducers: {
        updateDocumentStatus: (state, action: PayloadAction<DocumentStatusUpdate>) => {
            state.documents[action.payload.document_id] = action.payload;
        },
        updateWorkspaceStatus: (state, action: PayloadAction<WorkspaceStatusUpdate>) => {
            state.workspaces[action.payload.workspace_id] = action.payload;
        },
        updateWikipediaFetchStatus: (state, action: PayloadAction<WikipediaFetchStatusUpdate>) => {
            state.wikipediaFetches[action.payload.id] = action.payload;
        },
        clearDocumentStatus: (state, action: PayloadAction<number>) => {
            delete state.documents[action.payload];
        },
        clearWorkspaceStatus: (state, action: PayloadAction<number>) => {
            delete state.workspaces[action.payload];
        },
        clearWikipediaFetchStatus: (state, action: PayloadAction<string>) => {
            delete state.wikipediaFetches[action.payload];
        },
        clearAllStatus: (state) => {
            state.documents = {};
            state.workspaces = {};
            state.wikipediaFetches = {}; // Clear new field
        },
    },
});

export const {
    updateDocumentStatus,
    updateWorkspaceStatus,
    updateWikipediaFetchStatus, // Export new action
    clearDocumentStatus,
    clearWorkspaceStatus,
    clearWikipediaFetchStatus, // Export new action
    clearAllStatus,
} = statusSlice.actions;

export const selectIsWorkspaceProcessing = (workspaceId: number) => (state: RootState) => {
    // Check if the workspace itself is provisioning or deleting
    if (
        state.status.workspaces[workspaceId]?.status === 'provisioning' ||
        state.status.workspaces[workspaceId]?.status === 'deleting'
    ) {
        return true;
    }

    // Check if any document in the workspace is processing
    const isDocumentProcessing = Object.values(state.status.documents).some(
        (doc) =>
            doc.workspace_id === workspaceId &&
            (doc.status === 'pending' ||
                doc.status === 'parsing' ||
                doc.status === 'chunking' ||
                doc.status === 'embedding' ||
                doc.status === 'indexing'),
    );

    // Check if any Wikipedia fetch for this workspace is processing
    const isWikipediaFetchProcessing = Object.values(state.status.wikipediaFetches).some(
        (fetch) =>
            fetch.workspace_id === workspaceId &&
            (fetch.status === 'pending' || fetch.status === 'fetching' || fetch.status === 'processing'),
    );

    return isDocumentProcessing || isWikipediaFetchProcessing;
};

export const selectIsWorkspaceDeleting = (workspaceId: number) => (state: RootState) => {
    return state.status.workspaces[workspaceId]?.status === 'deleting';
};

export default statusSlice.reducer;
