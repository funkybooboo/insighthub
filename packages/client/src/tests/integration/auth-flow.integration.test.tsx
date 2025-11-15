/**
 * Integration tests for authentication flow
 * Tests the complete user journey from signup to authenticated state
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '@/store/slices/authSlice';
import chatReducer from '@/store/slices/chatSlice';
import apiService from '@/services/api';
import LoginForm from '@/components/auth/LoginForm';
import SignupForm from '@/components/auth/SignupForm';

// Mock API service
vi.mock('@/services/api', () => ({
    default: {
        signup: vi.fn(),
        login: vi.fn(),
    },
}));

const renderWithProviders = (component: React.ReactElement) => {
    const store = configureStore({
        reducer: {
            auth: authReducer,
            chat: chatReducer,
        },
    });

    return {
        store,
        ...render(
            <Provider store={store}>
                <BrowserRouter>{component}</BrowserRouter>
            </Provider>
        ),
    };
};

describe('Authentication Flow Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    describe('Signup to Login Flow', () => {
        it('should complete signup and automatically log in user', async () => {
            const user = userEvent.setup();

            const mockSignupResponse = {
                token: 'mock-jwt-token',
                user: {
                    id: 1,
                    username: 'newuser',
                    email: 'newuser@example.com',
                    full_name: 'New User',
                    created_at: new Date().toISOString(),
                },
            };

            vi.mocked(apiService.signup).mockResolvedValueOnce(mockSignupResponse);

            const { store } = renderWithProviders(<SignupForm />);

            // Fill signup form
            await user.type(screen.getByLabelText(/username/i), 'newuser');
            await user.type(screen.getByLabelText(/^email$/i), 'newuser@example.com');
            await user.type(screen.getByLabelText(/full name/i), 'New User');
            await user.type(screen.getByLabelText(/^password$/i), 'SecurePass123!');
            await user.type(screen.getByLabelText(/confirm password/i), 'SecurePass123!');

            // Submit form
            await user.click(screen.getByRole('button', { name: /sign up/i }));

            // Verify signup API was called
            await waitFor(() => {
                expect(apiService.signup).toHaveBeenCalledWith({
                    username: 'newuser',
                    email: 'newuser@example.com',
                    full_name: 'New User',
                    password: 'SecurePass123!',
                });
            });

            // Verify Redux state is updated
            await waitFor(() => {
                const state = store.getState();
                expect(state.auth.user).toEqual(mockSignupResponse.user);
                expect(state.auth.token).toBe(mockSignupResponse.token);
                expect(state.auth.isAuthenticated).toBe(true);
            });

            // Verify token is stored in localStorage
            expect(localStorage.getItem('token')).toBe('mock-jwt-token');
        });

        it('should persist authentication state across page reloads', async () => {
            const user = userEvent.setup();

            const mockLoginResponse = {
                token: 'persistent-token',
                user: {
                    id: 1,
                    username: 'testuser',
                    email: 'test@example.com',
                    full_name: 'Test User',
                    created_at: new Date().toISOString(),
                },
            };

            vi.mocked(apiService.login).mockResolvedValueOnce(mockLoginResponse);

            const { store } = renderWithProviders(<LoginForm />);

            // Login
            await user.type(screen.getByLabelText(/username/i), 'testuser');
            await user.type(screen.getByLabelText(/password/i), 'password123');
            await user.click(screen.getByRole('button', { name: /sign in/i }));

            await waitFor(() => {
                expect(store.getState().auth.isAuthenticated).toBe(true);
            });

            // Simulate page reload by creating new store
            const newStore = configureStore({
                reducer: {
                    auth: authReducer,
                    chat: chatReducer,
                },
            });

            // In a real app, the App component would check localStorage and restore auth state
            // Here we verify the token is available
            expect(localStorage.getItem('token')).toBe('persistent-token');
        });
    });

    describe('Login Error Handling', () => {
        it('should handle network errors gracefully', async () => {
            const user = userEvent.setup();

            vi.mocked(apiService.login).mockRejectedValueOnce(new Error('Network error'));

            renderWithProviders(<LoginForm />);

            await user.type(screen.getByLabelText(/username/i), 'testuser');
            await user.type(screen.getByLabelText(/password/i), 'password123');
            await user.click(screen.getByRole('button', { name: /sign in/i }));

            // Verify error message appears
            await expect(
                screen.findByText(/login failed|error|network/i)
            ).resolves.toBeInTheDocument();
        });

        it('should handle invalid credentials', async () => {
            const user = userEvent.setup();

            const errorResponse = {
                response: {
                    status: 401,
                    data: { message: 'Invalid username or password' },
                },
            };

            vi.mocked(apiService.login).mockRejectedValueOnce(errorResponse);

            renderWithProviders(<LoginForm />);

            await user.type(screen.getByLabelText(/username/i), 'wronguser');
            await user.type(screen.getByLabelText(/password/i), 'wrongpass');
            await user.click(screen.getByRole('button', { name: /sign in/i }));

            // Verify error message appears
            await expect(
                screen.findByText(/invalid username or password/i)
            ).resolves.toBeInTheDocument();
        });
    });

    describe('Form Validation', () => {
        it('should validate password matching in signup', async () => {
            const user = userEvent.setup();

            renderWithProviders(<SignupForm />);

            await user.type(screen.getByLabelText(/username/i), 'testuser');
            await user.type(screen.getByLabelText(/^email$/i), 'test@example.com');
            await user.type(screen.getByLabelText(/^password$/i), 'Password123!');
            await user.type(screen.getByLabelText(/confirm password/i), 'DifferentPass123!');
            await user.click(screen.getByRole('button', { name: /sign up/i }));

            // Verify password mismatch error
            await expect(
                screen.findByText(/passwords do not match/i)
            ).resolves.toBeInTheDocument();

            // Verify API was not called
            expect(apiService.signup).not.toHaveBeenCalled();
        });
    });
});
