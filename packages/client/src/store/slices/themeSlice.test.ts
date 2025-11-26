import { describe, it, expect, beforeEach, vi } from 'vitest';
import { configureStore } from '@reduxjs/toolkit';
import themeReducer, { toggleTheme, setTheme } from './themeSlice';
import '../../test/setup';

describe('themeSlice', () => {
    let store: ReturnType<typeof configureStore>;

    beforeEach(() => {
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

    // TODO: Add tests for toggleThemeAndSave async thunk
});
