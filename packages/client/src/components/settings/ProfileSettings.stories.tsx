import type { Meta, StoryObj } from '@storybook/react-vite';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import authSlice from '../../store/slices/authSlice';
import ProfileSettings from './ProfileSettings';

// Create a mock store for Storybook
const createMockStore = (
    initialState = {
        auth: { user: null, token: null },
    }
) => {
    return configureStore({
        reducer: {
            auth: authSlice,
        },
        preloadedState: initialState,
    });
};

const meta: Meta<typeof ProfileSettings> = {
    title: 'Settings/ProfileSettings',
    component: ProfileSettings,
    parameters: {
        layout: 'padded',
        docs: {
            description: {
                component: 'User profile settings form for updating personal information.',
            },
        },
    },
    tags: ['autodocs'],
    argTypes: {
        user: {
            control: 'object',
        },
    },
    decorators: [
        (Story, context) => {
            const store = createMockStore({
                auth: { user: context.args?.user || null, token: 'mock-token' },
            });
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

export const WithUser: Story = {
    args: {
        user: {
            id: 1,
            username: 'johndoe',
            email: 'john.doe@example.com',
            full_name: 'John Doe',
        },
    },
};

export const WithoutFullName: Story = {
    args: {
        user: {
            id: 2,
            username: 'janedoe',
            email: 'jane.doe@example.com',
            full_name: null,
        },
    },
};

export const EmptyUser: Story = {
    args: {
        user: null,
    },
};

export const InSettingsPage: Story = {
    args: {
        user: {
            id: 1,
            username: 'johndoe',
            email: 'john.doe@example.com',
            full_name: 'John Doe',
        },
    },
    render: (args) => (
        <div className="max-w-4xl mx-auto">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                <div className="border-b border-gray-200 dark:border-gray-700">
                    <nav className="flex">
                        <button className="px-6 py-4 text-sm font-medium text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400">
                            Profile
                        </button>
                        <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                            Password
                        </button>
                        <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                            RAG Config
                        </button>
                    </nav>
                </div>

                <div className="p-6">
                    <div className="mb-6">
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                            Profile Settings
                        </h2>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Update your personal information and preferences.
                        </p>
                    </div>

                    <ProfileSettings user={args.user} />
                </div>
            </div>
        </div>
    ),
};
