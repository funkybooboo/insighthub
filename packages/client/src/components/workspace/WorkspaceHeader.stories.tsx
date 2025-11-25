import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';

// Mock WorkspaceHeader component for Storybook to avoid shared package import issues
const MockWorkspaceHeader = ({
    activeWorkspace,
    workspacesLoading,
    showWorkspaceDropdown,
    setShowWorkspaceDropdown,
}: {
    activeWorkspace?: { id: number; name: string; description?: string; status: string };
    workspacesLoading: boolean;
    showWorkspaceDropdown: boolean;
    setShowWorkspaceDropdown: (show: boolean) => void;
}) => {
    return (
        <div className="relative">
            <button
                onClick={() => setShowWorkspaceDropdown(!showWorkspaceDropdown)}
                className="w-full flex items-center justify-between px-3 py-2.5 bg-gray-50 dark:bg-gray-800 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700/70 transition-colors border border-gray-200/60 dark:border-gray-700/50"
                disabled={workspacesLoading}
            >
                <div className="flex items-center gap-2.5 min-w-0">
                    <svg
                        className="text-blue-500 dark:text-blue-400 flex-shrink-0 w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                    >
                        <path d="M2 6a2 2 0 012-2h5a2 2 0 012 2v2H2V6zM2 10h10v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                    </svg>
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                        {activeWorkspace?.name || 'Select Workspace'}
                    </span>
                </div>
                {workspacesLoading ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500 flex-shrink-0"></div>
                ) : (
                    <svg
                        className={`w-3 h-3 text-gray-400 transition-transform flex-shrink-0 ${
                            showWorkspaceDropdown ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 9l-7 7-7-7"
                        />
                    </svg>
                )}
            </button>
        </div>
    );
};

const meta: Meta<typeof MockWorkspaceHeader> = {
    title: 'Workspace/WorkspaceHeader',
    component: MockWorkspaceHeader,
    parameters: {
        layout: 'centered',
        docs: {
            description: {
                component:
                    'Workspace selector header with dropdown toggle functionality. (Mock implementation for Storybook)',
            },
        },
    },
    tags: ['autodocs'],
    argTypes: {
        activeWorkspace: {
            control: 'object',
        },
        workspacesLoading: {
            control: 'boolean',
        },
        showWorkspaceDropdown: {
            control: 'boolean',
        },
    },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const NoWorkspace: Story = {
    args: {
        workspacesLoading: false,
        showWorkspaceDropdown: false,
        setShowWorkspaceDropdown: () => {},
    },
};

export const WithWorkspace: Story = {
    args: {
        activeWorkspace: {
            id: 1,
            name: 'Research Papers',
            description: 'Academic research documents',
            status: 'ready',
        },
        workspacesLoading: false,
        showWorkspaceDropdown: false,
        setShowWorkspaceDropdown: () => {},
    },
};

export const Loading: Story = {
    args: {
        workspacesLoading: true,
        showWorkspaceDropdown: false,
        setShowWorkspaceDropdown: () => {},
    },
};

export const DropdownOpen: Story = {
    args: {
        activeWorkspace: {
            id: 1,
            name: 'Research Papers',
            description: 'Academic research documents',
            status: 'ready',
        },
        workspacesLoading: false,
        showWorkspaceDropdown: true,
        setShowWorkspaceDropdown: () => {},
    },
};

export const Interactive: Story = {
    render: () => {
        const [showDropdown, setShowDropdown] = useState(false);

        return (
            <div className="w-80">
                <MockWorkspaceHeader
                    activeWorkspace={{
                        id: 1,
                        name: 'My Research Workspace',
                        description: 'Collection of academic papers',
                        status: 'ready',
                    }}
                    workspacesLoading={false}
                    showWorkspaceDropdown={showDropdown}
                    setShowWorkspaceDropdown={setShowDropdown}
                />
                <p className="text-xs text-gray-500 mt-2">
                    Click the header to toggle dropdown state
                </p>
            </div>
        );
    },
};
