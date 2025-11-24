import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { Workspace, WorkspaceState } from '../../types/workspace';
import type { RootState } from '../index';

const ACTIVE_WORKSPACE_KEY = 'activeWorkspaceId';

const loadActiveWorkspaceId = (): number | null => {
    try {
        const stored = localStorage.getItem(ACTIVE_WORKSPACE_KEY);
        return stored ? parseInt(stored, 10) : null;
    } catch {
        // localStorage not available (e.g., in tests or SSR)
        return null;
    }
};

const saveActiveWorkspaceId = (id: number | null): void => {
    try {
        if (id === null) {
            localStorage.removeItem(ACTIVE_WORKSPACE_KEY);
        } else {
            localStorage.setItem(ACTIVE_WORKSPACE_KEY, id.toString());
        }
    } catch {
        // localStorage not available (e.g., in tests or SSR)
        // Silently ignore
    }
};

const initialState: WorkspaceState = {
    workspaces: [],
    activeWorkspaceId: loadActiveWorkspaceId(),
    isLoading: false,
    error: null,
};

const workspaceSlice = createSlice({
    name: 'workspace',
    initialState,
    reducers: {
        setWorkspaces: (state, action: PayloadAction<Workspace[]>) => {
            state.workspaces = action.payload;
            state.isLoading = false;
            state.error = null;
        },
        addWorkspace: (state, action: PayloadAction<Workspace>) => {
            state.workspaces.push(action.payload);
            if (state.workspaces.length === 1) {
                state.activeWorkspaceId = action.payload.id;
                saveActiveWorkspaceId(action.payload.id);
            }
        },
        updateWorkspace: (state, action: PayloadAction<Workspace>) => {
            const index = state.workspaces.findIndex((w) => w.id === action.payload.id);
            if (index !== -1) {
                state.workspaces[index] = action.payload;
            }
        },
        removeWorkspace: (state, action: PayloadAction<number>) => {
            state.workspaces = state.workspaces.filter((w) => w.id !== action.payload);
            if (state.activeWorkspaceId === action.payload) {
                state.activeWorkspaceId =
                    state.workspaces.length > 0 ? state.workspaces[0].id : null;
                saveActiveWorkspaceId(state.activeWorkspaceId);
            }
        },
        setActiveWorkspace: (state, action: PayloadAction<number>) => {
            state.activeWorkspaceId = action.payload;
            saveActiveWorkspaceId(action.payload);
        },
        setLoading: (state, action: PayloadAction<boolean>) => {
            state.isLoading = action.payload;
        },
        setError: (state, action: PayloadAction<string | null>) => {
            state.error = action.payload;
            state.isLoading = false;
        },
        clearError: (state) => {
            state.error = null;
        },
    },
});

export const {
    setWorkspaces,
    addWorkspace,
    updateWorkspace,
    removeWorkspace,
    setActiveWorkspace,
    setLoading,
    setError,
    clearError,
} = workspaceSlice.actions;

// Selectors
export const selectActiveWorkspaceId = (state: RootState) => state.workspace.activeWorkspaceId;
export const selectWorkspaces = (state: RootState) => state.workspace.workspaces;
export const selectWorkspaceLoading = (state: RootState) => state.workspace.isLoading;
export const selectWorkspaceError = (state: RootState) => state.workspace.error;

export default workspaceSlice.reducer;
