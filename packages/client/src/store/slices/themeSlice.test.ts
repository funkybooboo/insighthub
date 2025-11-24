import { describe, it, expect, beforeEach, vi } from 'vitest';
import { configureStore } from '@reduxjs/toolkit';
import themeReducer, { toggleTheme, setTheme, toggleThemeAndSave } from './themeSlice';
import apiService from '../../services/api';
import '../../test/setup';

vi.mock('../../services/api', () => ({
    default: {
        updatePreferences: vi.fn(),
    },
}));

describe('themeSlice', () => {
    let store: ReturnType<typeof configureStore>;

    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
        store = configureStore({
            reducer: {
                theme: themeReducer,
            },
        });
    });

    describe('initial state', () => {
        it('should use dark theme as default when nothing is stored', () => {
            localStorage.clear();
            const freshStore = configureStore({
                reducer: {
                    theme: themeReducer,
                },
            });
            const state = freshStore.getState().theme;
            expect(state.theme).toBe('dark');
        });

        it('should persist theme to localStorage when changed', () => {
            localStorage.clear();
            const newStore = configureStore({
                reducer: {
                    theme: themeReducer,
                },
            });

            newStore.dispatch(setTheme('light'));
            expect(localStorage.getItem('theme')).toBe('light');
            expect(newStore.getState().theme.theme).toBe('light');
        });

        it('should load dark theme from localStorage', () => {
            localStorage.setItem('theme', 'dark');
            const newStore = configureStore({
                reducer: {
                    theme: themeReducer,
                },
            });
            expect(newStore.getState().theme.theme).toBe('dark');
        });

        it('should default to dark when invalid value in localStorage', () => {
            localStorage.setItem('theme', 'invalid');
            const newStore = configureStore({
                reducer: {
                    theme: themeReducer,
                },
            });
            expect(newStore.getState().theme.theme).toBe('dark');
        });
    });

    describe('toggleTheme', () => {
        it('should toggle from dark to light', () => {
            store.dispatch(toggleTheme());
            expect(store.getState().theme.theme).toBe('light');
            expect(localStorage.getItem('theme')).toBe('light');
        });

        it('should toggle from light to dark', () => {
            store.dispatch(setTheme('light'));
            store.dispatch(toggleTheme());
            expect(store.getState().theme.theme).toBe('dark');
            expect(localStorage.getItem('theme')).toBe('dark');
        });

        it('should persist theme to localStorage', () => {
            store.dispatch(toggleTheme());
            expect(localStorage.getItem('theme')).toBe('light');
            store.dispatch(toggleTheme());
            expect(localStorage.getItem('theme')).toBe('dark');
        });
    });

    describe('setTheme', () => {
        it('should set theme to light', () => {
            store.dispatch(setTheme('light'));
            expect(store.getState().theme.theme).toBe('light');
            expect(localStorage.getItem('theme')).toBe('light');
        });

        it('should set theme to dark', () => {
            store.dispatch(setTheme('dark'));
            expect(store.getState().theme.theme).toBe('dark');
            expect(localStorage.getItem('theme')).toBe('dark');
        });

        it('should overwrite existing theme', () => {
            store.dispatch(setTheme('light'));
            store.dispatch(setTheme('dark'));
            expect(store.getState().theme.theme).toBe('dark');
            expect(localStorage.getItem('theme')).toBe('dark');
        });
    });

    describe('toggleThemeAndSave', () => {
        it('should toggle theme and call API successfully', async () => {
            apiService.updatePreferences.mockResolvedValue({
                id: 1,
                username: 'testuser',
                email: 'test@example.com',
                full_name: 'Test User',
                created_at: '2024-01-01',
                theme_preference: 'light',
            });

            await store.dispatch(toggleThemeAndSave());

            expect(store.getState().theme.theme).toBe('light');
            expect(apiService.updatePreferences).toHaveBeenCalledWith({
                theme_preference: 'light',
            });
        });

        it('should toggle theme even if API fails', async () => {
            const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
            apiService.updatePreferences.mockRejectedValue(new Error('API error'));

            await store.dispatch(toggleThemeAndSave());

            expect(store.getState().theme.theme).toBe('light');
            expect(consoleError).toHaveBeenCalledWith(
                'Failed to save theme preference:',
                expect.any(Error)
            );
            consoleError.mockRestore();
        });

        it('should toggle from light to dark and save', async () => {
            store.dispatch(setTheme('light'));
            apiService.updatePreferences.mockResolvedValue({
                id: 1,
                username: 'testuser',
                email: 'test@example.com',
                full_name: 'Test User',
                created_at: '2024-01-01',
                theme_preference: 'dark',
            });

            await store.dispatch(toggleThemeAndSave());

            expect(store.getState().theme.theme).toBe('dark');
            expect(apiService.updatePreferences).toHaveBeenCalledWith({
                theme_preference: 'dark',
            });
        });

        it('should handle non-Error exceptions gracefully', async () => {
            const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
            apiService.updatePreferences.mockRejectedValue('String error');

            await store.dispatch(toggleThemeAndSave());

            expect(store.getState().theme.theme).toBe('light');
            expect(consoleError).toHaveBeenCalled();
            consoleError.mockRestore();
        });
    });
});
