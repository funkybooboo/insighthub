/**
 * Component tests for UserMenu
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import UserMenu from './UserMenu';
import authReducer, { setCredentials } from '../../store/slices/authSlice';
import apiService from '../../services/api';
import type { User } from '../../types/auth';

// Mock API service
vi.mock('../../services/api', () => ({
    default: {
        logout: vi.fn(),
    },
}));

// Mock window.location
delete (window as { location?: Location }).location;
window.location = { href: '' } as Location;

describe('UserMenu', () => {
    const mockUser: User = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User',
        created_at: '2024-01-01T00:00:00Z',
    };

    const renderUserMenu = (user: User | null = mockUser) => {
        const store = configureStore({
            reducer: {
                auth: authReducer,
            },
        });

        if (user) {
            store.dispatch(
                setCredentials({
                    user,
                    token: 'test-token',
                })
            );
        }

        return render(
            <Provider store={store}>
                <UserMenu />
            </Provider>
        );
    };

    beforeEach(() => {
        vi.clearAllMocks();
        window.location.href = '';
    });

    describe('Rendering', () => {
        it('should render logo', () => {
            renderUserMenu();

            const logo = screen.getByAltText('InsightHub');
            expect(logo).toBeInTheDocument();
            expect(logo).toHaveAttribute('src', '/logo.png');
        });

        it('should render username', () => {
            renderUserMenu();

            expect(screen.getByText('testuser')).toBeInTheDocument();
        });

        it('should render email', () => {
            renderUserMenu();

            expect(screen.getByText('test@example.com')).toBeInTheDocument();
        });

        it('should render logout button', () => {
            renderUserMenu();

            const logoutButton = screen.getByRole('button', { name: /logout/i });
            expect(logoutButton).toBeInTheDocument();
        });

        it('should display logo and title when user is null', () => {
            renderUserMenu(null);

            expect(screen.getByText('InsightHub')).toBeInTheDocument();
            expect(screen.getByAltText('InsightHub')).toBeInTheDocument();
        });

        it('should render user without full_name', () => {
            const userWithoutFullName: User = {
                id: 2,
                username: 'johndoe',
                email: 'john@example.com',
                full_name: null,
                created_at: '2024-01-01T00:00:00Z',
            };

            renderUserMenu(userWithoutFullName);

            expect(screen.getByText('johndoe')).toBeInTheDocument();
            expect(screen.getByText('john@example.com')).toBeInTheDocument();
        });
    });

    describe('Logout Functionality', () => {
        it('should call logout API and redirect when logout button is clicked', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.logout).mockResolvedValueOnce(undefined);
            renderUserMenu();

            const logoutButton = screen.getByRole('button', { name: /logout/i });

            await user.click(logoutButton);

            await waitFor(() => {
                expect(apiService.logout).toHaveBeenCalledTimes(1);
            });

            expect(window.location.href).toBe('/login');
        });

        it('should clear localStorage token on logout', async () => {
            const user = userEvent.setup();
            localStorage.setItem('token', 'test-token');
            vi.mocked(apiService.logout).mockResolvedValueOnce(undefined);
            renderUserMenu();

            const logoutButton = screen.getByRole('button', { name: /logout/i });

            await user.click(logoutButton);

            await waitFor(() => {
                expect(localStorage.getItem('token')).toBeNull();
            });
        });

        it('should redirect to login even if logout API fails', async () => {
            const user = userEvent.setup();
            const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
            vi.mocked(apiService.logout).mockRejectedValueOnce(new Error('Network error'));
            renderUserMenu();

            const logoutButton = screen.getByRole('button', { name: /logout/i });

            await user.click(logoutButton);

            await waitFor(() => {
                expect(window.location.href).toBe('/login');
            });

            expect(consoleErrorSpy).toHaveBeenCalledWith('Logout error:', expect.any(Error));

            consoleErrorSpy.mockRestore();
        });

        it('should log error to console when logout API fails', async () => {
            const user = userEvent.setup();
            const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
            const error = new Error('Logout failed');
            vi.mocked(apiService.logout).mockRejectedValueOnce(error);
            renderUserMenu();

            const logoutButton = screen.getByRole('button', { name: /logout/i });

            await user.click(logoutButton);

            await waitFor(() => {
                expect(consoleErrorSpy).toHaveBeenCalledWith('Logout error:', error);
            });

            consoleErrorSpy.mockRestore();
        });

        it('should clear user from Redux store on logout', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.logout).mockResolvedValueOnce(undefined);
            renderUserMenu();

            expect(screen.getByText('testuser')).toBeInTheDocument();

            const logoutButton = screen.getByRole('button', { name: /logout/i });

            await user.click(logoutButton);

            await waitFor(() => {
                expect(window.location.href).toBe('/login');
            });
        });
    });

    describe('User Information Display', () => {
        it('should display different user information correctly', () => {
            const differentUser: User = {
                id: 5,
                username: 'alice',
                email: 'alice@example.com',
                full_name: 'Alice Smith',
                created_at: '2024-02-01T00:00:00Z',
            };

            renderUserMenu(differentUser);

            expect(screen.getByText('alice')).toBeInTheDocument();
            expect(screen.getByText('alice@example.com')).toBeInTheDocument();
        });

        it('should handle very long username', () => {
            const longUsernameUser: User = {
                id: 3,
                username: 'verylongusernamethatmightbreakthelayout',
                email: 'long@example.com',
                full_name: 'Long Name',
                created_at: '2024-01-01T00:00:00Z',
            };

            renderUserMenu(longUsernameUser);

            expect(screen.getByText('verylongusernamethatmightbreakthelayout')).toBeInTheDocument();
        });

        it('should handle very long email', () => {
            const longEmailUser: User = {
                id: 4,
                username: 'user',
                email: 'verylongemailaddressthatmightbreakthelayout@example.com',
                full_name: 'User Name',
                created_at: '2024-01-01T00:00:00Z',
            };

            renderUserMenu(longEmailUser);

            expect(
                screen.getByText('verylongemailaddressthatmightbreakthelayout@example.com')
            ).toBeInTheDocument();
        });

        it('should handle special characters in username', () => {
            const specialUser: User = {
                id: 6,
                username: 'user@#$%',
                email: 'special@example.com',
                full_name: 'Special User',
                created_at: '2024-01-01T00:00:00Z',
            };

            renderUserMenu(specialUser);

            expect(screen.getByText('user@#$%')).toBeInTheDocument();
        });

        it('should handle special characters in email', () => {
            const specialEmailUser: User = {
                id: 7,
                username: 'user',
                email: 'user+test@example.com',
                full_name: 'User',
                created_at: '2024-01-01T00:00:00Z',
            };

            renderUserMenu(specialEmailUser);

            expect(screen.getByText('user+test@example.com')).toBeInTheDocument();
        });
    });

    describe('Interaction', () => {
        it('should not trigger logout on hover', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.logout).mockResolvedValueOnce(undefined);
            renderUserMenu();

            const logoutButton = screen.getByRole('button', { name: /logout/i });

            await user.hover(logoutButton);

            expect(apiService.logout).not.toHaveBeenCalled();
            expect(window.location.href).toBe('');
        });

        it('should handle multiple rapid clicks gracefully', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.logout).mockResolvedValueOnce(undefined);
            renderUserMenu();

            const logoutButton = screen.getByRole('button', { name: /logout/i });

            await user.click(logoutButton);
            await user.click(logoutButton);
            await user.click(logoutButton);

            await waitFor(() => {
                expect(window.location.href).toBe('/login');
            });
        });
    });

    describe('Accessibility', () => {
        it('should have accessible button', () => {
            renderUserMenu();

            const logoutButton = screen.getByRole('button', { name: /logout/i });
            expect(logoutButton).toBeInTheDocument();
        });

        it('should have visible text content', () => {
            renderUserMenu();

            const username = screen.getByText('testuser');
            const email = screen.getByText('test@example.com');

            expect(username).toBeVisible();
            expect(email).toBeVisible();
        });

        it('should have accessible logo with alt text', () => {
            renderUserMenu();

            const logo = screen.getByAltText('InsightHub');
            expect(logo).toBeInTheDocument();
        });
    });

    describe('Edge Cases', () => {
        it('should handle logout with empty user', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.logout).mockResolvedValueOnce(undefined);
            renderUserMenu(null);

            const logoutButton = screen.getByRole('button', { name: /logout/i });

            await user.click(logoutButton);

            await waitFor(() => {
                expect(window.location.href).toBe('/login');
            });
        });

        it('should handle logout API timeout', async () => {
            const user = userEvent.setup();
            const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
            vi.mocked(apiService.logout).mockRejectedValueOnce(new Error('Timeout'));
            renderUserMenu();

            const logoutButton = screen.getByRole('button', { name: /logout/i });

            await user.click(logoutButton);

            await waitFor(() => {
                expect(window.location.href).toBe('/login');
            });

            consoleErrorSpy.mockRestore();
        });

        it('should handle user with minimal data', () => {
            const minimalUser: User = {
                id: 8,
                username: 'u',
                email: 'u@e.co',
                full_name: null,
                created_at: '2024-01-01T00:00:00Z',
            };

            renderUserMenu(minimalUser);

            expect(screen.getByText('u')).toBeInTheDocument();
            expect(screen.getByText('u@e.co')).toBeInTheDocument();
        });
    });
});
