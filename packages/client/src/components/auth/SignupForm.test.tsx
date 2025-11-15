/**
 * Component tests for SignupForm
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import SignupForm from './SignupForm';
import authReducer from '../../store/slices/authSlice';
import apiService from '../../services/api';

// Mock API service
vi.mock('../../services/api', () => ({
    default: {
        signup: vi.fn(),
    },
}));

// Mock navigation
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom');
    return {
        ...actual,
        useNavigate: () => mockNavigate,
    };
});

describe('SignupForm', () => {
    const renderSignupForm = () => {
        const store = configureStore({
            reducer: {
                auth: authReducer,
            },
        });

        return render(
            <Provider store={store}>
                <BrowserRouter>
                    <SignupForm />
                </BrowserRouter>
            </Provider>
        );
    };

    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    describe('Rendering', () => {
        it('should render all form fields', () => {
            renderSignupForm();

            expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
        });

        it('should render signup button', () => {
            renderSignupForm();

            const button = screen.getByRole('button', { name: /sign up/i });
            expect(button).toBeInTheDocument();
            expect(button).not.toBeDisabled();
        });

        it('should render logo', () => {
            renderSignupForm();

            const logo = screen.getByAltText('InsightHub');
            expect(logo).toBeInTheDocument();
            expect(logo).toHaveAttribute('src', '/logo.png');
        });

        it('should render heading', () => {
            renderSignupForm();

            expect(screen.getByText('Create your account')).toBeInTheDocument();
        });

        it('should render link to login page', () => {
            renderSignupForm();

            const link = screen.getByRole('link', { name: /already have an account/i });
            expect(link).toBeInTheDocument();
            expect(link).toHaveAttribute('href', '/login');
        });

        it('should mark required fields correctly', () => {
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const fullNameInput = screen.getByLabelText(/full name/i);

            expect(usernameInput).toBeRequired();
            expect(emailInput).toBeRequired();
            expect(passwordInput).toBeRequired();
            expect(confirmPasswordInput).toBeRequired();
            expect(fullNameInput).not.toBeRequired();
        });

        it('should have correct input types', () => {
            renderSignupForm();

            expect(screen.getByLabelText(/username/i)).toHaveAttribute('type', 'text');
            expect(screen.getByLabelText(/^email$/i)).toHaveAttribute('type', 'email');
            expect(screen.getByLabelText(/^password$/i)).toHaveAttribute('type', 'password');
            expect(screen.getByLabelText(/confirm password/i)).toHaveAttribute('type', 'password');
        });
    });

    describe('Form Validation', () => {
        it('should show error when passwords do not match', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password456');
            await user.click(submitButton);

            expect(await screen.findByText('Passwords do not match')).toBeInTheDocument();
            expect(apiService.signup).not.toHaveBeenCalled();
        });

        it('should show error when password is too short', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, '12345');
            await user.type(confirmPasswordInput, '12345');
            await user.click(submitButton);

            expect(
                await screen.findByText('Password must be at least 6 characters')
            ).toBeInTheDocument();
            expect(apiService.signup).not.toHaveBeenCalled();
        });

        it('should clear previous error when submitting again', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            // First submission with error
            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password456');
            await user.click(submitButton);

            expect(await screen.findByText('Passwords do not match')).toBeInTheDocument();

            // Clear and fix
            await user.clear(confirmPasswordInput);
            await user.type(confirmPasswordInput, 'password123');
            await user.click(submitButton);

            expect(screen.queryByText('Passwords do not match')).not.toBeInTheDocument();
        });

        it('should accept password with exactly 6 characters', async () => {
            const user = userEvent.setup();
            const mockResponse = {
                access_token: 'test-token',
                token_type: 'bearer',
                user: {
                    id: 1,
                    username: 'testuser',
                    email: 'test@example.com',
                    full_name: null,
                    created_at: '2024-01-01T00:00:00Z',
                },
            };

            vi.mocked(apiService.signup).mockResolvedValueOnce(mockResponse);
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, '123456');
            await user.type(confirmPasswordInput, '123456');
            await user.click(submitButton);

            await waitFor(() => {
                expect(apiService.signup).toHaveBeenCalled();
            });
        });
    });

    describe('Form Interaction', () => {
        it('should update username field when typing', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);

            await user.type(usernameInput, 'testuser');

            expect(usernameInput).toHaveValue('testuser');
        });

        it('should update email field when typing', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const emailInput = screen.getByLabelText(/^email$/i);

            await user.type(emailInput, 'test@example.com');

            expect(emailInput).toHaveValue('test@example.com');
        });

        it('should update password fields when typing', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password123');

            expect(passwordInput).toHaveValue('password123');
            expect(confirmPasswordInput).toHaveValue('password123');
        });

        it('should update optional full name field', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const fullNameInput = screen.getByLabelText(/full name/i);

            await user.type(fullNameInput, 'Test User');

            expect(fullNameInput).toHaveValue('Test User');
        });
    });

    describe('Form Submission', () => {
        it('should call signup API and navigate on successful signup', async () => {
            const user = userEvent.setup();
            const mockResponse = {
                access_token: 'test-token-123',
                token_type: 'bearer',
                user: {
                    id: 1,
                    username: 'testuser',
                    email: 'test@example.com',
                    full_name: 'Test User',
                    created_at: '2024-01-01T00:00:00Z',
                },
            };

            vi.mocked(apiService.signup).mockResolvedValueOnce(mockResponse);
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const fullNameInput = screen.getByLabelText(/full name/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(fullNameInput, 'Test User');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password123');
            await user.click(submitButton);

            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalledWith('/');
            });

            expect(apiService.signup).toHaveBeenCalledWith({
                username: 'testuser',
                email: 'test@example.com',
                password: 'password123',
                full_name: 'Test User',
            });
        });

        it('should omit full_name when not provided', async () => {
            const user = userEvent.setup();
            const mockResponse = {
                access_token: 'test-token',
                token_type: 'bearer',
                user: {
                    id: 1,
                    username: 'testuser',
                    email: 'test@example.com',
                    full_name: null,
                    created_at: '2024-01-01T00:00:00Z',
                },
            };

            vi.mocked(apiService.signup).mockResolvedValueOnce(mockResponse);
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password123');
            await user.click(submitButton);

            await waitFor(() => {
                expect(apiService.signup).toHaveBeenCalledWith({
                    username: 'testuser',
                    email: 'test@example.com',
                    password: 'password123',
                    full_name: undefined,
                });
            });
        });

        it('should show loading state during signup', async () => {
            const user = userEvent.setup();
            let resolveSignup: (value: unknown) => void;
            const signupPromise = new Promise((resolve) => {
                resolveSignup = resolve;
            });

            vi.mocked(apiService.signup).mockReturnValueOnce(signupPromise);
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password123');
            await user.click(submitButton);

            // Check loading state
            expect(screen.getByRole('button', { name: /creating account/i })).toBeDisabled();

            // Resolve the promise
            resolveSignup!({
                access_token: 'test-token',
                token_type: 'bearer',
                user: {
                    id: 1,
                    username: 'testuser',
                    email: 'test@example.com',
                    full_name: null,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });

            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalled();
            });
        });

        it('should handle signup error with Error instance', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.signup).mockRejectedValueOnce(
                new Error('Username already exists')
            );
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password123');
            await user.click(submitButton);

            expect(await screen.findByText('Username already exists')).toBeInTheDocument();
            expect(mockNavigate).not.toHaveBeenCalled();
        });

        it('should handle signup error with non-Error object', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.signup).mockRejectedValueOnce('Network error');
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password123');
            await user.click(submitButton);

            expect(await screen.findByText('Signup failed. Please try again.')).toBeInTheDocument();
            expect(mockNavigate).not.toHaveBeenCalled();
        });

        it('should re-enable button after error', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.signup).mockRejectedValueOnce(new Error('Signup failed'));
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password123');
            await user.click(submitButton);

            await screen.findByText('Signup failed');

            // Button should be enabled again
            expect(screen.getByRole('button', { name: /sign up/i })).not.toBeDisabled();
        });

        it('should store credentials in Redux and localStorage on success', async () => {
            const user = userEvent.setup();
            const mockResponse = {
                access_token: 'test-token-abc',
                token_type: 'bearer',
                user: {
                    id: 1,
                    username: 'testuser',
                    email: 'test@example.com',
                    full_name: 'Test User',
                    created_at: '2024-01-01T00:00:00Z',
                },
            };

            vi.mocked(apiService.signup).mockResolvedValueOnce(mockResponse);
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password123');
            await user.click(submitButton);

            await waitFor(() => {
                expect(localStorage.getItem('token')).toBe('test-token-abc');
            });
        });
    });

    describe('Edge Cases', () => {
        it('should handle very long input values', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const longUsername = 'a'.repeat(100);

            await user.type(usernameInput, longUsername);

            expect(usernameInput).toHaveValue(longUsername);
        });

        it('should handle special characters in input', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const specialUsername = 'user@#$%^&*()';

            await user.type(usernameInput, specialUsername);

            expect(usernameInput).toHaveValue(specialUsername);
        });

        it('should handle whitespace in password', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const passwordWithSpaces = 'pass word 123';

            await user.type(passwordInput, passwordWithSpaces);
            await user.type(confirmPasswordInput, passwordWithSpaces);

            expect(passwordInput).toHaveValue(passwordWithSpaces);
            expect(confirmPasswordInput).toHaveValue(passwordWithSpaces);
        });

        it('should trim full name when empty string is provided', async () => {
            const user = userEvent.setup();
            const mockResponse = {
                access_token: 'test-token',
                token_type: 'bearer',
                user: {
                    id: 1,
                    username: 'testuser',
                    email: 'test@example.com',
                    full_name: null,
                    created_at: '2024-01-01T00:00:00Z',
                },
            };

            vi.mocked(apiService.signup).mockResolvedValueOnce(mockResponse);
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const fullNameInput = screen.getByLabelText(/full name/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            // Leave fullNameInput empty by not typing anything
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password123');
            await user.click(submitButton);

            await waitFor(() => {
                expect(apiService.signup).toHaveBeenCalledWith(
                    expect.objectContaining({
                        full_name: undefined,
                    })
                );
            });
        });
    });

    describe('Accessibility', () => {
        it('should have accessible form structure', () => {
            renderSignupForm();

            const form = screen.getByRole('button', { name: /sign up/i }).closest('form');
            expect(form).toBeInTheDocument();
        });

        it('should have proper labels for all inputs', () => {
            renderSignupForm();

            expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/^email$/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
        });

        it('should have accessible error messages', async () => {
            const user = userEvent.setup();
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            const submitButton = screen.getByRole('button', { name: /sign up/i });

            // Fill in all required fields but with mismatched passwords
            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password456');
            await user.click(submitButton);

            const errorMessage = await screen.findByText('Passwords do not match');
            expect(errorMessage).toBeInTheDocument();
            expect(errorMessage).toBeVisible();
        });

        it('should have accessible button states', async () => {
            const user = userEvent.setup();
            let resolveSignup: (value: unknown) => void;
            const signupPromise = new Promise((resolve) => {
                resolveSignup = resolve;
            });

            vi.mocked(apiService.signup).mockReturnValueOnce(signupPromise);
            renderSignupForm();

            const usernameInput = screen.getByLabelText(/username/i);
            const emailInput = screen.getByLabelText(/^email$/i);
            const passwordInput = screen.getByLabelText(/^password$/i);
            const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
            let submitButton = screen.getByRole('button', { name: /sign up/i });

            expect(submitButton).not.toBeDisabled();

            await user.type(usernameInput, 'testuser');
            await user.type(emailInput, 'test@example.com');
            await user.type(passwordInput, 'password123');
            await user.type(confirmPasswordInput, 'password123');
            await user.click(submitButton);

            submitButton = screen.getByRole('button', { name: /creating account/i });
            expect(submitButton).toBeDisabled();

            resolveSignup!({
                access_token: 'test-token',
                token_type: 'bearer',
                user: {
                    id: 1,
                    username: 'testuser',
                    email: 'test@example.com',
                    full_name: null,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });

            await waitFor(() => {
                expect(mockNavigate).toHaveBeenCalled();
            });
        });
    });
});
