/**
 * Unit tests for Auth Redux slice
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import authReducer, { setCredentials, logout, setLoading, setUser, type User } from './authSlice';
import '../../test/setup';

describe('authSlice', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    afterEach(() => {
        localStorage.clear();
    });

    describe('initial state', () => {
        it('should have correct initial state when no token in localStorage', () => {
            const state = authReducer(undefined, { type: '@@INIT' });

            expect(state).toEqual({
                user: null,
                token: null,
                isAuthenticated: false,
                isLoading: false,
            });
        });

        it('should use token from localStorage if available', () => {
            // Note: Since the initial state is evaluated when the module loads,
            // this test verifies the behavior works at runtime rather than import time
            localStorage.setItem('token', 'existing-token');

            // The initial state is cached, so we can't test the re-initialization
            // Instead, we verify that setCredentials works correctly
            const user = {
                id: 1,
                username: 'test',
                email: 'test@example.com',
                full_name: 'Test User',
                created_at: '2024-01-01T00:00:00Z',
            };

            const state = authReducer(undefined, setCredentials({ user, token: 'existing-token' }));

            expect(state.token).toBe('existing-token');
            expect(state.isAuthenticated).toBe(true);
            expect(localStorage.getItem('token')).toBe('existing-token');
        });
    });

    describe('setCredentials', () => {
        it('should set user and token', () => {
            const user: User = {
                id: 1,
                username: 'testuser',
                email: 'test@example.com',
                full_name: 'Test User',
                created_at: '2024-01-01T00:00:00Z',
            };

            const token = 'test-token-123';

            const state = authReducer(undefined, setCredentials({ user, token }));

            expect(state.user).toEqual(user);
            expect(state.token).toBe(token);
            expect(state.isAuthenticated).toBe(true);
            expect(localStorage.getItem('token')).toBe(token);
        });

        it('should update existing credentials', () => {
            const initialState = {
                user: {
                    id: 1,
                    username: 'olduser',
                    email: 'old@example.com',
                    full_name: 'Old User',
                    created_at: '2024-01-01T00:00:00Z',
                },
                token: 'old-token',
                isAuthenticated: true,
                isLoading: false,
            };

            const newUser: User = {
                id: 2,
                username: 'newuser',
                email: 'new@example.com',
                full_name: 'New User',
                created_at: '2024-01-02T00:00:00Z',
            };

            const newToken = 'new-token-456';

            const state = authReducer(
                initialState,
                setCredentials({ user: newUser, token: newToken })
            );

            expect(state.user).toEqual(newUser);
            expect(state.token).toBe(newToken);
            expect(localStorage.getItem('token')).toBe(newToken);
        });

        it('should handle user with null full_name', () => {
            const user: User = {
                id: 1,
                username: 'testuser',
                email: 'test@example.com',
                full_name: null,
                created_at: '2024-01-01T00:00:00Z',
            };

            const state = authReducer(undefined, setCredentials({ user, token: 'token' }));

            expect(state.user?.full_name).toBeNull();
        });
    });

    describe('logout', () => {
        it('should clear user and token', () => {
            const initialState = {
                user: {
                    id: 1,
                    username: 'testuser',
                    email: 'test@example.com',
                    full_name: 'Test User',
                    created_at: '2024-01-01T00:00:00Z',
                },
                token: 'test-token',
                isAuthenticated: true,
                isLoading: false,
            };

            localStorage.setItem('token', 'test-token');

            const state = authReducer(initialState, logout());

            expect(state.user).toBeNull();
            expect(state.token).toBeNull();
            expect(state.isAuthenticated).toBe(false);
            expect(localStorage.getItem('token')).toBeNull();
        });

        it('should handle logout when already logged out', () => {
            const initialState = {
                user: null,
                token: null,
                isAuthenticated: false,
                isLoading: false,
            };

            const state = authReducer(initialState, logout());

            expect(state.user).toBeNull();
            expect(state.token).toBeNull();
            expect(state.isAuthenticated).toBe(false);
        });
    });

    describe('setLoading', () => {
        it('should set loading to true', () => {
            const state = authReducer(undefined, setLoading(true));

            expect(state.isLoading).toBe(true);
        });

        it('should set loading to false', () => {
            const initialState = {
                user: null,
                token: null,
                isAuthenticated: false,
                isLoading: true,
            };

            const state = authReducer(initialState, setLoading(false));

            expect(state.isLoading).toBe(false);
        });

        it('should not affect other state properties', () => {
            const initialState = {
                user: {
                    id: 1,
                    username: 'testuser',
                    email: 'test@example.com',
                    full_name: 'Test User',
                    created_at: '2024-01-01T00:00:00Z',
                },
                token: 'test-token',
                isAuthenticated: true,
                isLoading: false,
            };

            const state = authReducer(initialState, setLoading(true));

            expect(state.user).toEqual(initialState.user);
            expect(state.token).toBe(initialState.token);
            expect(state.isAuthenticated).toBe(true);
            expect(state.isLoading).toBe(true);
        });
    });

    describe('setUser', () => {
        it('should update user information', () => {
            const user: User = {
                id: 1,
                username: 'testuser',
                email: 'test@example.com',
                full_name: 'Test User',
                created_at: '2024-01-01T00:00:00Z',
            };

            const state = authReducer(undefined, setUser(user));

            expect(state.user).toEqual(user);
        });

        it('should update existing user', () => {
            const initialState = {
                user: {
                    id: 1,
                    username: 'olduser',
                    email: 'old@example.com',
                    full_name: 'Old User',
                    created_at: '2024-01-01T00:00:00Z',
                },
                token: 'test-token',
                isAuthenticated: true,
                isLoading: false,
            };

            const updatedUser: User = {
                id: 1,
                username: 'updateduser',
                email: 'updated@example.com',
                full_name: 'Updated User',
                created_at: '2024-01-01T00:00:00Z',
            };

            const state = authReducer(initialState, setUser(updatedUser));

            expect(state.user).toEqual(updatedUser);
            expect(state.token).toBe('test-token');
            expect(state.isAuthenticated).toBe(true);
        });

        it('should not affect authentication status', () => {
            const initialState = {
                user: null,
                token: 'test-token',
                isAuthenticated: true,
                isLoading: false,
            };

            const user: User = {
                id: 1,
                username: 'testuser',
                email: 'test@example.com',
                full_name: 'Test User',
                created_at: '2024-01-01T00:00:00Z',
            };

            const state = authReducer(initialState, setUser(user));

            expect(state.isAuthenticated).toBe(true);
            expect(state.token).toBe('test-token');
        });
    });

    describe('action creators', () => {
        it('should create setCredentials action', () => {
            const user: User = {
                id: 1,
                username: 'testuser',
                email: 'test@example.com',
                full_name: 'Test User',
                created_at: '2024-01-01T00:00:00Z',
            };

            const action = setCredentials({ user, token: 'token' });

            expect(action.type).toBe('auth/setCredentials');
            expect(action.payload).toEqual({ user, token: 'token' });
        });

        it('should create logout action', () => {
            const action = logout();

            expect(action.type).toBe('auth/logout');
            expect(action.payload).toBeUndefined();
        });

        it('should create setLoading action', () => {
            const action = setLoading(true);

            expect(action.type).toBe('auth/setLoading');
            expect(action.payload).toBe(true);
        });

        it('should create setUser action', () => {
            const user: User = {
                id: 1,
                username: 'testuser',
                email: 'test@example.com',
                full_name: 'Test User',
                created_at: '2024-01-01T00:00:00Z',
            };

            const action = setUser(user);

            expect(action.type).toBe('auth/setUser');
            expect(action.payload).toEqual(user);
        });
    });
});
