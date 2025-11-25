import type { Meta, StoryObj } from '@storybook/react';
import LoadingSpinner from './LoadingSpinner';

const meta: Meta<typeof LoadingSpinner> = {
  title: 'Shared/LoadingSpinner',
  component: LoadingSpinner,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    size: {
      control: { type: 'select' },
      options: ['sm', 'md', 'lg'],
    },
    className: {
      control: 'text',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Small: Story = {
  args: {
    size: 'sm',
  },
};

export const Medium: Story = {
  args: {
    size: 'md',
  },
};

export const Large: Story = {
  args: {
    size: 'lg',
  },
};

export const WithCustomClass: Story = {
  args: {
    size: 'md',
    className: 'border-purple-500',
  },
};

export const InContext: Story = {
  render: () => (
    <div className="flex flex-col items-center gap-4 p-8">
      <div className="flex items-center gap-4">
        <LoadingSpinner size="sm" />
        <span className="text-sm text-gray-600 dark:text-gray-400">Loading small items...</span>
      </div>
      <div className="flex items-center gap-4">
        <LoadingSpinner size="md" />
        <span className="text-gray-600 dark:text-gray-400">Loading content...</span>
      </div>
      <div className="flex items-center gap-4">
        <LoadingSpinner size="lg" />
        <span className="text-lg text-gray-600 dark:text-gray-400">Loading page...</span>
      </div>
    </div>
  ),
};