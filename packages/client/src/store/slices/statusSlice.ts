import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

export type DocumentStatus = 'pending' | 'processing' | 'ready' | 'failed';
export type WorkspaceStatus = 'provisioning' | 'ready' | 'error';

interface DocumentStatusUpdate {
    document_id: number;
    user_id: number;
    workspace_id: number | null;
    status: DocumentStatus;
    error: string | null;
    chunk_count: number | null;
    filename: string;
    metadata: Record<string, unknown>;
}

interface WorkspaceStatusUpdate {
    workspace_id: number;
    user_id: number;
    status: WorkspaceStatus;
    message: string | null;
    name: string;
    metadata: Record<string, unknown>;
}

interface StatusState {
    documents: Record<number, DocumentStatusUpdate>;
    workspaces: Record<number, WorkspaceStatusUpdate>;
}

const initialState: StatusState = {
    documents: {},
    workspaces: {},
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
        clearDocumentStatus: (state, action: PayloadAction<number>) => {
            delete state.documents[action.payload];
        },
        clearWorkspaceStatus: (state, action: PayloadAction<number>) => {
            delete state.workspaces[action.payload];
        },
        clearAllStatus: (state) => {
            state.documents = {};
            state.workspaces = {};
        },
    },
});

export const {
    updateDocumentStatus,
    updateWorkspaceStatus,
    clearDocumentStatus,
    clearWorkspaceStatus,
    clearAllStatus,
} = statusSlice.actions;

export default statusSlice.reducer;
