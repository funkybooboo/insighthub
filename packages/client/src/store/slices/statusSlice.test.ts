import { describe, it, expect } from 'vitest';
import statusReducer, {
    updateDocumentStatus,
    updateWorkspaceStatus,
    updateWikipediaFetchStatus,
    clearDocumentStatus,
    clearWorkspaceStatus,
    clearWikipediaFetchStatus,
    clearAllStatus,
    type DocumentStatus,
    type WorkspaceStatus,
    type WikipediaFetchStatus,
} from './statusSlice';

describe('statusSlice', () => {
    const initialState = {
        documents: {},
        workspaces: {},
        wikipediaFetches: {},
    };

    describe('document status', () => {
        it('should update document status', () => {
            const documentUpdate = {
                document_id: 1,
                user_id: 1,
                workspace_id: 1,
                status: 'ready' as DocumentStatus,
                error: null,
                chunk_count: 5,
                filename: 'test.pdf',
                metadata: { pages: 10 },
                progress: 100,
                message: 'Processing complete',
            };

            const result = statusReducer(initialState, updateDocumentStatus(documentUpdate));

            expect(result.documents[1]).toEqual(documentUpdate);
        });

        it('should clear document status', () => {
            const stateWithDocument = {
                ...initialState,
                documents: {
                    1: {
                        document_id: 1,
                        user_id: 1,
                        workspace_id: 1,
                        status: 'ready' as DocumentStatus,
                        error: null,
                        chunk_count: 5,
                        filename: 'test.pdf',
                    },
                },
            };

            const result = statusReducer(stateWithDocument, clearDocumentStatus(1));

            expect(result.documents[1]).toBeUndefined();
        });
    });

    describe('workspace status', () => {
        it('should update workspace status', () => {
            const workspaceUpdate = {
                workspace_id: 1,
                user_id: 1,
                status: 'ready' as WorkspaceStatus,
                message: 'Workspace ready',
                name: 'Test Workspace',
                metadata: { documents: 5 },
            };

            const result = statusReducer(initialState, updateWorkspaceStatus(workspaceUpdate));

            expect(result.workspaces[1]).toEqual(workspaceUpdate);
        });

        it('should clear workspace status', () => {
            const stateWithWorkspace = {
                ...initialState,
                workspaces: {
                    1: {
                        workspace_id: 1,
                        user_id: 1,
                        status: 'ready' as WorkspaceStatus,
                        message: 'Workspace ready',
                    },
                },
            };

            const result = statusReducer(stateWithWorkspace, clearWorkspaceStatus(1));

            expect(result.workspaces[1]).toBeUndefined();
        });
    });

    describe('wikipedia fetch status', () => {
        it('should update wikipedia fetch status', () => {
            const wikipediaUpdate = {
                id: 'fetch-1',
                user_id: 1,
                workspace_id: 1,
                query: 'machine learning',
                status: 'ready' as WikipediaFetchStatus,
                message: 'Fetch complete',
                error: null,
                timestamp: 1234567890,
            };

            const result = statusReducer(initialState, updateWikipediaFetchStatus(wikipediaUpdate));

            expect(result.wikipediaFetches['fetch-1']).toEqual(wikipediaUpdate);
        });

        it('should clear wikipedia fetch status', () => {
            const stateWithFetch = {
                ...initialState,
                wikipediaFetches: {
                    'fetch-1': {
                        id: 'fetch-1',
                        user_id: 1,
                        workspace_id: 1,
                        query: 'machine learning',
                        status: 'ready' as WikipediaFetchStatus,
                        message: 'Fetch complete',
                        error: null,
                        timestamp: 1234567890,
                    },
                },
            };

            const result = statusReducer(stateWithFetch, clearWikipediaFetchStatus('fetch-1'));

            expect(result.wikipediaFetches['fetch-1']).toBeUndefined();
        });
    });

    describe('clear all status', () => {
        it('should clear all status data', () => {
            const fullState = {
                documents: {
                    1: {
                        document_id: 1,
                        user_id: 1,
                        workspace_id: 1,
                        status: 'ready' as DocumentStatus,
                        error: null,
                        chunk_count: 5,
                        filename: 'test.pdf',
                    },
                },
                workspaces: {
                    1: {
                        workspace_id: 1,
                        user_id: 1,
                        status: 'ready' as WorkspaceStatus,
                        message: 'Workspace ready',
                    },
                },
                wikipediaFetches: {
                    'fetch-1': {
                        id: 'fetch-1',
                        user_id: 1,
                        workspace_id: 1,
                        query: 'machine learning',
                        status: 'ready' as WikipediaFetchStatus,
                        message: 'Fetch complete',
                        error: null,
                        timestamp: 1234567890,
                    },
                },
            };

            const result = statusReducer(fullState, clearAllStatus());

            expect(result.documents).toEqual({});
            expect(result.workspaces).toEqual({});
            expect(result.wikipediaFetches).toEqual({});
        });
    });
});
