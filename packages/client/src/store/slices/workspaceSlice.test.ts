import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import workspaceReducer, {
    setWorkspaces,
    addWorkspace,
    updateWorkspace,
    removeWorkspace,
    setActiveWorkspace,
    setLoading,
    setError,
    clearError,
} from './workspaceSlice';
import type { WorkspaceState, Workspace } from '../../types/workspace';

const ACTIVE_WORKSPACE_KEY = 'activeWorkspaceId';

describe('workspaceSlice', () => {
    const mockWorkspace: Workspace = {
        id: 1,
        name: 'Test Workspace',
        description: 'A test workspace',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        document_count: 0,
        session_count: 0,
    };

    const mockWorkspace2: Workspace = {
        id: 2,
        name: 'Another Workspace',
        created_at: '2025-01-02T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z',
        document_count: 5,
        session_count: 3,
    };

    const initialState: WorkspaceState = {
        workspaces: [],
        activeWorkspaceId: null,
        isLoading: false,
        error: null,
    };

    beforeEach(() => {
        localStorage.clear();
    });

    afterEach(() => {
        localStorage.clear();
    });

    describe('initial state', () => {
        it('should return the initial state with no active workspace', () => {
            const state = workspaceReducer(undefined, { type: 'unknown' });
            expect(state.workspaces).toEqual([]);
            expect(state.isLoading).toBe(false);
            expect(state.error).toBe(null);
        });

        it('should persist and load active workspace id from localStorage', () => {
            localStorage.setItem(ACTIVE_WORKSPACE_KEY, '42');
            const loadedId = localStorage.getItem(ACTIVE_WORKSPACE_KEY);
            expect(loadedId).toBe('42');
            expect(parseInt(loadedId || '0', 10)).toBe(42);
        });
    });

    describe('setWorkspaces', () => {
        it('should set workspaces and clear loading state', () => {
            const previousState: WorkspaceState = {
                ...initialState,
                isLoading: true,
                error: 'Some error',
            };

            const state = workspaceReducer(
                previousState,
                setWorkspaces([mockWorkspace, mockWorkspace2])
            );

            expect(state.workspaces).toEqual([mockWorkspace, mockWorkspace2]);
            expect(state.isLoading).toBe(false);
            expect(state.error).toBe(null);
        });
    });

    describe('addWorkspace', () => {
        it('should add a workspace to the list', () => {
            const state = workspaceReducer(
                { ...initialState, workspaces: [mockWorkspace] },
                addWorkspace(mockWorkspace2)
            );

            expect(state.workspaces).toHaveLength(2);
            expect(state.workspaces[1]).toEqual(mockWorkspace2);
        });

        it('should set active workspace if it is the first one', () => {
            const state = workspaceReducer(initialState, addWorkspace(mockWorkspace));

            expect(state.workspaces).toHaveLength(1);
            expect(state.activeWorkspaceId).toBe(mockWorkspace.id);
            expect(localStorage.getItem(ACTIVE_WORKSPACE_KEY)).toBe(mockWorkspace.id.toString());
        });

        it('should not change active workspace if workspaces already exist', () => {
            const previousState: WorkspaceState = {
                ...initialState,
                workspaces: [mockWorkspace],
                activeWorkspaceId: mockWorkspace.id,
            };

            const state = workspaceReducer(previousState, addWorkspace(mockWorkspace2));

            expect(state.workspaces).toHaveLength(2);
            expect(state.activeWorkspaceId).toBe(mockWorkspace.id);
        });
    });

    describe('updateWorkspace', () => {
        it('should update an existing workspace', () => {
            const updatedWorkspace: Workspace = {
                ...mockWorkspace,
                name: 'Updated Name',
                description: 'Updated description',
            };

            const previousState: WorkspaceState = {
                ...initialState,
                workspaces: [mockWorkspace, mockWorkspace2],
            };

            const state = workspaceReducer(previousState, updateWorkspace(updatedWorkspace));

            expect(state.workspaces[0]).toEqual(updatedWorkspace);
            expect(state.workspaces[1]).toEqual(mockWorkspace2);
        });

        it('should not change state if workspace id not found', () => {
            const nonExistentWorkspace: Workspace = {
                ...mockWorkspace,
                id: 999,
            };

            const previousState: WorkspaceState = {
                ...initialState,
                workspaces: [mockWorkspace],
            };

            const state = workspaceReducer(previousState, updateWorkspace(nonExistentWorkspace));

            expect(state.workspaces).toEqual([mockWorkspace]);
        });
    });

    describe('removeWorkspace', () => {
        it('should remove a workspace from the list', () => {
            const previousState: WorkspaceState = {
                ...initialState,
                workspaces: [mockWorkspace, mockWorkspace2],
                activeWorkspaceId: mockWorkspace2.id,
            };

            const state = workspaceReducer(previousState, removeWorkspace(mockWorkspace.id));

            expect(state.workspaces).toHaveLength(1);
            expect(state.workspaces[0]).toEqual(mockWorkspace2);
            expect(state.activeWorkspaceId).toBe(mockWorkspace2.id);
        });

        it('should set active workspace to first remaining if active was deleted', () => {
            const previousState: WorkspaceState = {
                ...initialState,
                workspaces: [mockWorkspace, mockWorkspace2],
                activeWorkspaceId: mockWorkspace.id,
            };

            const state = workspaceReducer(previousState, removeWorkspace(mockWorkspace.id));

            expect(state.workspaces).toHaveLength(1);
            expect(state.activeWorkspaceId).toBe(mockWorkspace2.id);
            expect(localStorage.getItem(ACTIVE_WORKSPACE_KEY)).toBe(mockWorkspace2.id.toString());
        });

        it('should set active workspace to null if all workspaces removed', () => {
            const previousState: WorkspaceState = {
                ...initialState,
                workspaces: [mockWorkspace],
                activeWorkspaceId: mockWorkspace.id,
            };

            const state = workspaceReducer(previousState, removeWorkspace(mockWorkspace.id));

            expect(state.workspaces).toHaveLength(0);
            expect(state.activeWorkspaceId).toBe(null);
            expect(localStorage.getItem(ACTIVE_WORKSPACE_KEY)).toBe(null);
        });
    });

    describe('setActiveWorkspace', () => {
        it('should set the active workspace id and persist to localStorage', () => {
            const state = workspaceReducer(initialState, setActiveWorkspace(mockWorkspace.id));

            expect(state.activeWorkspaceId).toBe(mockWorkspace.id);
            expect(localStorage.getItem(ACTIVE_WORKSPACE_KEY)).toBe(mockWorkspace.id.toString());
        });
    });

    describe('loading and error states', () => {
        it('should set loading state', () => {
            const state = workspaceReducer(initialState, setLoading(true));
            expect(state.isLoading).toBe(true);

            const state2 = workspaceReducer(state, setLoading(false));
            expect(state2.isLoading).toBe(false);
        });

        it('should set error and clear loading state', () => {
            const previousState: WorkspaceState = {
                ...initialState,
                isLoading: true,
            };

            const state = workspaceReducer(previousState, setError('Test error'));

            expect(state.error).toBe('Test error');
            expect(state.isLoading).toBe(false);
        });

        it('should clear error', () => {
            const previousState: WorkspaceState = {
                ...initialState,
                error: 'Some error',
            };

            const state = workspaceReducer(previousState, clearError());

            expect(state.error).toBe(null);
        });

        it('should handle null error', () => {
            const previousState: WorkspaceState = {
                ...initialState,
                isLoading: true,
                error: 'Previous error',
            };

            const state = workspaceReducer(previousState, setError(null));

            expect(state.error).toBe(null);
            expect(state.isLoading).toBe(false);
        });
    });
});
