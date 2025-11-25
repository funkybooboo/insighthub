import type { Meta, StoryObj } from '@storybook/react';
import RagConfigSettings from './RagConfigSettings';

const meta: Meta<typeof RagConfigSettings> = {
  title: 'Settings/RagConfigSettings',
  component: RagConfigSettings,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {},
  parameters: {
    docs: {
      description: {
        story: 'RAG configuration settings form for customizing default retrieval and generation parameters.',
      },
    },
  },
};

export const InSettingsPage: Story = {
  render: () => (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex">
            <button className="px-6 py-4 text-sm font-medium text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400">
              RAG Configuration
            </button>
            <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              Profile
            </button>
            <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              Password
            </button>
          </nav>
        </div>

        <RagConfigSettings />
      </div>
    </div>
  ),
};