import type { Meta, StoryObj } from '@storybook/react-vite';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import themeSlice from '../../store/slices/themeSlice';
import ThemeToggle from './ThemeToggle';

// Create a mock store for Storybook
const createMockStore = (initialState = { theme: { theme: 'light' } }) => {
    return configureStore({
        reducer: {
            theme: themeSlice,
        },
        preloadedState: initialState,
    });
};

const meta: Meta<typeof ThemeToggle> = {
    title: 'UI/ThemeToggle',
    component: ThemeToggle,
    parameters: {
        layout: 'centered',
        docs: {
            description: {
                component: 'Theme toggle button that switches between light and dark modes.',
            },
        },
    },
    tags: ['autodocs'],
    decorators: [
        (Story, context) => {
            const store = createMockStore(
                context.args?.initialState || { theme: { theme: 'light' } }
            );
            return (
                <Provider store={store}>
                    <Story />
                </Provider>
            );
        },
    ],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const LightMode: Story = {
    args: {
        initialState: { theme: { theme: 'light' } },
    },
    parameters: {
        docs: {
            description: {
                story: 'Theme toggle in light mode. Click to switch to dark mode.',
            },
        },
    },
};

export const DarkMode: Story = {
    args: {
        initialState: { theme: { theme: 'dark' } },
    },
    parameters: {
        docs: {
            description: {
                story: 'Theme toggle in dark mode. Click to switch to light mode.',
            },
        },
    },
};

export const InContainer: Story = {
    args: {
        initialState: { theme: { theme: 'light' } },
    },
    render: () => (
        <div className="p-8 bg-gradient-to-br from-blue-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 rounded-lg">
            <div className="flex justify-end mb-4">
                <ThemeToggle />
            </div>
            <div className="bg-white dark:bg-gray-800 p-4 rounded shadow">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    Sample Content
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                    This content changes appearance based on the theme toggle above.
                </p>
            </div>
        </div>
    ),
    parameters: {
        docs: {
            description: {
                story: 'Theme toggle shown in a sample container to demonstrate the UI context and theme switching.',
            },
        },
    },
};
