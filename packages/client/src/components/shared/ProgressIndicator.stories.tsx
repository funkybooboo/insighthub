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
  parameters: {
    docs: {
      description: {
        story: 'Basic progress indicator with title and description.',
      },
    },
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
  parameters: {
    docs: {
      description: {
        story: 'Progress indicator with step-by-step completion status.',
      },
    },
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
  parameters: {
    docs: {
      description: {
        story: 'Progress indicator showing all steps completed.',
      },
    },
  },
};

export const PartialProgress: Story = {
  args: {
    title: 'System Update',
    description: 'Updating your workspace configuration',
    steps: [
      { label: 'Downloading updates', completed: true },
      { label: 'Installing components', completed: true },
      { label: 'Configuring settings', completed: true },
      { label: 'Finalizing setup', completed: false },
    ],
  },
  parameters: {
    docs: {
      description: {
        story: 'Progress indicator with mixed completed and pending steps.',
      },
    },
  },
};

export const LongProcess: Story = {
  args: {
    title: 'Large Document Analysis',
    description: 'Processing a comprehensive research paper collection',
    steps: [
      { label: 'Loading documents', completed: true },
      { label: 'Preprocessing text', completed: true },
      { label: 'Extracting entities', completed: true },
      { label: 'Building knowledge graph', completed: false },
      { label: 'Generating embeddings', completed: false },
      { label: 'Indexing vectors', completed: false },
      { label: 'Optimizing search', completed: false },
    ],
  },
  parameters: {
    docs: {
      description: {
        story: 'Progress indicator for complex multi-step processes.',
      },
    },
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

      <ProgressIndicator
        title="Workspace Sync"
        description="Synchronizing changes across all devices"
        steps={[
          { label: 'Uploading changes', completed: true },
          { label: 'Updating remote', completed: false },
        ]}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Multiple progress indicators shown together in a realistic UI context.',
      },
    },
  },
};

export const ErrorState: Story = {
  args: {
    title: 'Processing Failed',
    description: 'An error occurred while processing your request',
  },
  parameters: {
    docs: {
      description: {
        story: 'Progress indicator for failed operations.',
      },
    },
  },
};

export const QuickTask: Story = {
  args: {
    title: 'Quick Analysis',
    description: 'Performing rapid document scan',
    steps: [
      { label: 'Scanning document', completed: true },
      { label: 'Checking for issues', completed: false },
    ],
  },
  parameters: {
    docs: {
      description: {
        story: 'Progress indicator for fast operations with minimal steps.',
      },
    },
  },
};