import type { Preview } from '@storybook/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../src/store/slices/authSlice';
import chatReducer from '../src/store/slices/chatSlice';
import '../src/index.css';

// Create a mock store for Storybook
const mockStore = configureStore({
    reducer: {
        auth: authReducer,
        chat: chatReducer,
    },
});

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: false,
        },
    },
});

const preview: Preview = {
    parameters: {
        controls: {
            matchers: {
                color: /(background|color)$/i,
                date: /Date$/i,
            },
        },
        backgrounds: {
            default: 'light',
            values: [
                {
                    name: 'light',
                    value: '#ffffff',
                },
                {
                    name: 'dark',
                    value: '#1a1a1a',
                },
            ],
        },
    },
    decorators: [
        (Story) => (
            <Provider store={mockStore}>
                <QueryClientProvider client={queryClient}>
                    <BrowserRouter>
                        <Story />
                    </BrowserRouter>
                </QueryClientProvider>
            </Provider>
        ),
    ],
};

export default preview;
