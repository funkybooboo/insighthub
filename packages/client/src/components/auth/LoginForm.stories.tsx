/**
 * Storybook stories for LoginForm component
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { within, userEvent, expect } from '@storybook/test';
import LoginForm from './LoginForm';
import authReducer from '../../store/slices/authSlice';
import chatReducer from '../../store/slices/chatSlice';

// Create a store for Storybook
const createMockStore = () => {
    return configureStore({
        reducer: {
            auth: authReducer,
            chat: chatReducer,
        },
    });
};

const meta: Meta<typeof LoginForm> = {
    title: 'Auth/LoginForm',
    component: LoginForm,
    parameters: {
        layout: 'fullscreen',
    },
    decorators: [
        (Story) => (
            <Provider store={createMockStore()}>
                <BrowserRouter>
                    <Story />
                </BrowserRouter>
            </Provider>
        ),
    ],
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof LoginForm>;

export const Default: Story = {
    name: 'Default State',
};

export const WithUsername: Story = {
    name: 'With Username Entered',
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const usernameInput = canvas.getByLabelText(/username/i);

        await userEvent.type(usernameInput, 'testuser', {
            delay: 100,
        });
    },
};

export const WithCredentials: Story = {
    name: 'With Both Fields Filled',
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const usernameInput = canvas.getByLabelText(/username/i);
        const passwordInput = canvas.getByLabelText(/password/i);

        await userEvent.type(usernameInput, 'testuser', {
            delay: 50,
        });
        await userEvent.type(passwordInput, 'password123', {
            delay: 50,
        });
    },
};

export const LoadingState: Story = {
    name: 'Loading State (Simulated)',
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const usernameInput = canvas.getByLabelText(/username/i);
        const passwordInput = canvas.getByLabelText(/password/i);
        const submitButton = canvas.getByRole('button', { name: /sign in/i });

        await userEvent.type(usernameInput, 'testuser', {
            delay: 50,
        });
        await userEvent.type(passwordInput, 'password123', {
            delay: 50,
        });
        await userEvent.click(submitButton);

        // Button should be disabled and show loading text
        const loadingButton = canvas.getByRole('button', { name: /signing in/i });
        expect(loadingButton).toBeDisabled();
    },
};

export const ValidationError: Story = {
    name: 'Validation Error',
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const submitButton = canvas.getByRole('button', { name: /sign in/i });

        // Try to submit without filling fields
        await userEvent.click(submitButton);

        // HTML5 validation should prevent submission
        const usernameInput = canvas.getByLabelText(/username/i);
        expect(usernameInput).toBeRequired();
    },
};

export const KeyboardNavigation: Story = {
    name: 'Keyboard Navigation',
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const usernameInput = canvas.getByLabelText(/username/i);

        // Focus username field
        usernameInput.focus();

        // Type username
        await userEvent.keyboard('testuser');

        // Tab to password
        await userEvent.keyboard('{Tab}');

        // Type password
        await userEvent.keyboard('password123');

        // Tab to submit button
        await userEvent.keyboard('{Tab}');

        // Press enter to submit
        await userEvent.keyboard('{Enter}');
    },
};
