import type { Meta, StoryObj } from '@storybook/react-vite';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import authSlice from '../../store/slices/authSlice';
import themeSlice from '../../store/slices/themeSlice';
import SignupForm from './SignupForm';

// Create a mock store for Storybook
const createMockStore = (
    initialState = {
        auth: { user: null, token: null },
        theme: { theme: 'light' },
    }
) => {
    return configureStore({
        reducer: {
            auth: authSlice,
            theme: themeSlice,
        },
        preloadedState: initialState,
    });
};

const meta: Meta<typeof SignupForm> = {
    title: 'Auth/SignupForm',
    component: SignupForm,
    parameters: {
        layout: 'fullscreen',
        docs: {
            description: {
                component: 'User registration form component with validation and authentication.',
            },
        },
    },
    tags: ['autodocs'],
    argTypes: {
        initialState: {
            control: { type: 'object' },
            description: 'Initial Redux state',
        },
    },
    decorators: [
        (Story, context) => {
            const store = createMockStore(
                context.args?.initialState || {
                    auth: { user: null, token: null },
                    theme: { theme: 'light' },
                }
            );
            return (
                <Provider store={store}>
                    <BrowserRouter>
                        <Story />
                    </BrowserRouter>
                </Provider>
            );
        },
    ],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    args: {
        initialState: {
            auth: { user: null, token: null },
            theme: { theme: 'light' },
        },
    },
    parameters: {
        docs: {
            description: {
                story: 'Basic signup form display with light theme.',
            },
        },
    },
};

export const DarkMode: Story = {
    args: {
        initialState: {
            auth: { user: null, token: null },
            theme: { theme: 'dark' },
        },
    },
    parameters: {
        docs: {
            description: {
                story: 'Signup form display with dark theme.',
            },
        },
    },
};
