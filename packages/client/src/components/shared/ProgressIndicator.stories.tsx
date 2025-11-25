import type { Meta, StoryObj } from '@storybook/react';
import ProgressIndicator from './ProgressIndicator';

const meta: Meta<typeof ProgressIndicator> = {
  title: 'Shared/ProgressIndicator',
  component: ProgressIndicator,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Progress indicator with optional steps showing completion status.',
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: 'text',
    },
    description: {
      control: 'text',
    },
    steps: {
      control: 'object',
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Simple: Story = {
  args: {
    title: 'Processing document...',
    description: 'Please wait while we analyze your document',
  },
};

export const WithSteps: Story = {
  args: {
    title: 'Document Processing',
    description: 'Converting your document for AI analysis',
    steps: [
      { label: 'Parsing document', completed: true },
      { label: 'Extracting text', completed: true },
      { label: 'Chunking content', completed: false },
      { label: 'Generating embeddings', completed: false },
    ],
  },
};

export const AllCompleted: Story = {
  args: {
    title: 'Processing Complete',
    description: 'Your document has been successfully processed',
    steps: [
      { label: 'Parsing document', completed: true },
      { label: 'Extracting text', completed: true },
      { label: 'Chunking content', completed: true },
      { label: 'Generating embeddings', completed: true },
    ],
  },
};

export const InContext: Story = {
  render: () => (
    <div className="space-y-4 p-6">
      <ProgressIndicator
        title="Uploading document..."
        description="Large files may take a few minutes to process"
      />

      <ProgressIndicator
        title="Document Analysis"
        description="Analyzing content and extracting insights"
        steps={[
          { label: 'Reading file', completed: true },
          { label: 'Extracting text', completed: true },
          { label: 'Analyzing content', completed: false },
          { label: 'Generating summary', completed: false },
        ]}
      />
    </div>
  ),
};