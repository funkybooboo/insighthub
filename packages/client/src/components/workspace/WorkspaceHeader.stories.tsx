import type { Meta, StoryObj } from '@storybook/react';
import { useState } from 'react';
import WorkspaceHeader from './WorkspaceHeader';

const meta: Meta<typeof WorkspaceHeader> = {
  title: 'Workspace/WorkspaceHeader',
  component: WorkspaceHeader,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: 'Workspace selector header with dropdown toggle functionality.',
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
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
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
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
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
        <WorkspaceHeader
          activeWorkspace={{
            id: 1,
            name: 'My Research Workspace',
            description: 'Collection of academic papers',
            status: 'ready',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
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