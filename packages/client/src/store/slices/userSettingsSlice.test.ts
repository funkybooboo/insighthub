import { describe, it, expect, vi, beforeEach } from 'vitest';
import userSettingsReducer, {
    fetchDefaultRagConfig,
    updateDefaultRagConfig,
    clearUserSettingsError,
    selectDefaultRagConfig,
    selectUserSettingsLoading,
    selectUserSettingsError,
} from './userSettingsSlice';
import apiService from '../../services/api';
import type { RagConfig } from '../../types/workspace';

// Mock the API service
vi.mock('../../services/api', () => ({
    default: {
        getDefaultRagConfig: vi.fn(),
        saveDefaultRagConfig: vi.fn(),
    },
}));

const mockRagConfig: RagConfig = {
    id: 1,
    workspace_id: 1,
    retriever_type: 'vector',
    embedding_model: 'nomic-embed-text',
    chunk_size: 1000,
    chunk_overlap: 200,
    top_k: 8,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
};

describe('userSettingsSlice', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('initial state', () => {
        it('should return the initial state', () => {
            const state = userSettingsReducer(undefined, { type: 'unknown' });
            expect(state).toEqual({
                defaultRagConfig: null,
                isLoading: false,
                error: null,
            });
        });
    });

    describe('clearUserSettingsError', () => {
        it('should clear the error', () => {
            const initialState = {
                defaultRagConfig: null,
                isLoading: false,
                error: 'Test error',
            };
            const state = userSettingsReducer(initialState, clearUserSettingsError());
            expect(state.error).toBeNull();
        });
    });

    describe('fetchDefaultRagConfig', () => {
        it('should handle pending state', () => {
            const action = { type: fetchDefaultRagConfig.pending.type };
            const state = userSettingsReducer(undefined, action);
            expect(state.isLoading).toBe(true);
            expect(state.error).toBeNull();
        });

        it('should handle fulfilled state', () => {
            const action = {
                type: fetchDefaultRagConfig.fulfilled.type,
                payload: mockRagConfig,
            };
            const state = userSettingsReducer(undefined, action);
            expect(state.isLoading).toBe(false);
            expect(state.defaultRagConfig).toEqual(mockRagConfig);
        });

        it('should handle rejected state', () => {
            const action = {
                type: fetchDefaultRagConfig.rejected.type,
                payload: 'Fetch failed',
            };
            const state = userSettingsReducer(undefined, action);
            expect(state.isLoading).toBe(false);
            expect(state.error).toBe('Fetch failed');
        });

        it('should call apiService.getDefaultRagConfig', async () => {
            const mockApi = vi.mocked(apiService);
            mockApi.getDefaultRagConfig.mockResolvedValue(mockRagConfig);

            const result = await fetchDefaultRagConfig()(vi.fn(), vi.fn(), undefined);
            expect(mockApi.getDefaultRagConfig).toHaveBeenCalled();
            expect(result.payload).toEqual(mockRagConfig);
        });

        it('should handle API errors', async () => {
            const mockApi = vi.mocked(apiService);
            const error = new Error('API Error');
            mockApi.getDefaultRagConfig.mockRejectedValue(error);

            const result = await fetchDefaultRagConfig()(vi.fn(), vi.fn(), undefined);
            expect(result.payload).toBe('API Error');
        });
    });

    describe('updateDefaultRagConfig', () => {
        it('should handle pending state', () => {
            const action = { type: updateDefaultRagConfig.pending.type };
            const state = userSettingsReducer(undefined, action);
            expect(state.isLoading).toBe(true);
            expect(state.error).toBeNull();
        });

        it('should handle fulfilled state', () => {
            const action = {
                type: updateDefaultRagConfig.fulfilled.type,
                payload: mockRagConfig,
            };
            const state = userSettingsReducer(undefined, action);
            expect(state.isLoading).toBe(false);
            expect(state.defaultRagConfig).toEqual(mockRagConfig);
        });

        it('should handle rejected state', () => {
            const action = {
                type: updateDefaultRagConfig.rejected.type,
                payload: 'Update failed',
            };
            const state = userSettingsReducer(undefined, action);
            expect(state.isLoading).toBe(false);
            expect(state.error).toBe('Update failed');
        });

        it('should call apiService.saveDefaultRagConfig', async () => {
            const mockApi = vi.mocked(apiService);
            mockApi.saveDefaultRagConfig.mockResolvedValue(mockRagConfig);

            const result = await updateDefaultRagConfig(mockRagConfig)(vi.fn(), vi.fn(), undefined);
            expect(mockApi.saveDefaultRagConfig).toHaveBeenCalledWith(mockRagConfig);
            expect(result.payload).toEqual(mockRagConfig);
        });

        it('should handle API errors', async () => {
            const mockApi = vi.mocked(apiService);
            const error = new Error('API Error');
            mockApi.saveDefaultRagConfig.mockRejectedValue(error);

            const result = await updateDefaultRagConfig(mockRagConfig)(vi.fn(), vi.fn(), undefined);
            expect(result.payload).toBe('API Error');
        });
    });

    describe('selectors', () => {
        const mockState = {
            userSettings: {
                defaultRagConfig: mockRagConfig,
                isLoading: true,
                error: 'Test error',
            },
        };

        it('should select default RAG config', () => {
            expect(selectDefaultRagConfig(mockState)).toEqual(mockRagConfig);
        });

        it('should select loading state', () => {
            expect(selectUserSettingsLoading(mockState)).toBe(true);
        });

        it('should select error', () => {
            expect(selectUserSettingsError(mockState)).toBe('Test error');
        });
    });
});