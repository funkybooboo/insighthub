/**
 * Storybook stories for UserMenu component
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { within, userEvent, expect } from '@storybook/test';
import UserMenu from './UserMenu';
import authReducer, { setCredentials } from '../../store/slices/authSlice';
import chatReducer from '../../store/slices/chatSlice';
import type { User } from '../../types/auth';

// Create a store with user data
const createMockStore = (user: User | null = null) => {
    const store = configureStore({
        reducer: {
            auth: authReducer,
            chat: chatReducer,
        },
    });

    if (user) {
        store.dispatch(
            setCredentials({
                user,
                token: 'mock-token',
            })
        );
    }

    return store;
};

const mockUser: User = {
    id: 1,
    username: 'johndoe',
    email: 'john.doe@example.com',
    full_name: 'John Doe',
    created_at: '2024-01-01T00:00:00Z',
};

const meta: Meta<typeof UserMenu> = {
    title: 'Auth/UserMenu',
    component: UserMenu,
    parameters: {
        layout: 'padded',
    },
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof UserMenu>;

export const Default: Story = {
    name: 'Default with User',
    decorators: [
        (Story) => (
            <Provider store={createMockStore(mockUser)}>
                <Story />
            </Provider>
        ),
    ],
};

export const WithLongUsername: Story = {
    name: 'With Long Username',
    decorators: [
        (Story) => (
            <Provider
                store={createMockStore({
                    ...mockUser,
                    username: 'verylongusernamethatmightoverflow',
                    email: 'verylongemail@example.com',
                })}
            >
                <Story />
            </Provider>
        ),
    ],
};

export const WithoutFullName: Story = {
    name: 'Without Full Name',
    decorators: [
        (Story) => (
            <Provider
                store={createMockStore({
                    ...mockUser,
                    full_name: null,
                })}
            >
                <Story />
            </Provider>
        ),
    ],
};

export const NoUser: Story = {
    name: 'No User (Logged Out)',
    decorators: [
        (Story) => (
            <Provider store={createMockStore(null)}>
                <Story />
            </Provider>
        ),
    ],
};

export const LogoutInteraction: Story = {
    name: 'Logout Button Interaction',
    decorators: [
        (Story) => (
            <Provider store={createMockStore(mockUser)}>
                <Story />
            </Provider>
        ),
    ],
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const logoutButton = canvas.getByRole('button', { name: /logout/i });

        // Hover over logout button
        await userEvent.hover(logoutButton);

        // Button should be visible and accessible
        expect(logoutButton).toBeInTheDocument();
    },
};

export const MultipleUsers: Story = {
    name: 'Different Users',
    decorators: [
        (Story) => (
            <div className="space-y-4">
                <Provider
                    store={createMockStore({
                        id: 1,
                        username: 'alice',
                        email: 'alice@example.com',
                        full_name: 'Alice Smith',
                        created_at: '2024-01-01T00:00:00Z',
                    })}
                >
                    <Story />
                </Provider>
                <Provider
                    store={createMockStore({
                        id: 2,
                        username: 'bob',
                        email: 'bob@example.com',
                        full_name: 'Bob Johnson',
                        created_at: '2024-01-01T00:00:00Z',
                    })}
                >
                    <Story />
                </Provider>
                <Provider
                    store={createMockStore({
                        id: 3,
                        username: 'charlie',
                        email: 'charlie@example.com',
                        full_name: null,
                        created_at: '2024-01-01T00:00:00Z',
                    })}
                >
                    <Story />
                </Provider>
            </div>
        ),
    ],
};
