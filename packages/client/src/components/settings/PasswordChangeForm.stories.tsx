import type { Meta, StoryObj } from '@storybook/react';
import PasswordChangeForm from './PasswordChangeForm';

const meta: Meta<typeof PasswordChangeForm> = {
  title: 'Settings/PasswordChangeForm',
  component: PasswordChangeForm,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Password change form with validation and confirmation.',
      },
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  parameters: {
    docs: {
      description: {
        story: 'Basic password change form with validation.',
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
            <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              Profile
            </button>
            <button className="px-6 py-4 text-sm font-medium text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400">
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
              Change Password
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Update your password to keep your account secure.
            </p>
          </div>

          <PasswordChangeForm />
        </div>
      </div>
    </div>
  ),
};