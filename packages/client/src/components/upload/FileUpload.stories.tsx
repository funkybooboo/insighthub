import type { Meta, StoryObj } from '@storybook/react';
import FileUpload from './FileUpload';

const meta: Meta<typeof FileUpload> = {
  title: 'Upload/FileUpload',
  component: FileUpload,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
  argTypes: {
    workspaceId: {
      control: 'number',
    },
    disabled: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    workspaceId: 1,
    onUploadSuccess: () => console.log('Upload success'),
  },
};

export const Disabled: Story = {
  args: {
    workspaceId: 1,
    disabled: true,
    onUploadSuccess: () => console.log('Upload success'),
  },
};

export const InDocumentManager: Story = {
  render: () => (
    <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Document Manager
        </h2>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Upload and manage your documents for RAG processing
        </p>
      </div>

      <FileUpload
        workspaceId={1}
        onUploadSuccess={() => console.log('Document uploaded successfully')}
      />

      <div className="p-6">
        <div className="text-center text-gray-500 dark:text-gray-400">
          <p className="text-sm">No documents uploaded yet</p>
        </div>
      </div>
    </div>
  ),
};