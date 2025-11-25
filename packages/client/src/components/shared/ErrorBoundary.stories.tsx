import type { Meta, StoryObj } from '@storybook/react';
import ErrorBoundary from './ErrorBoundary';

// Component that throws an error for testing
const ErrorThrowingComponent = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('This is a test error for the ErrorBoundary component');
  }
  return <div className="p-4 bg-green-100 dark:bg-green-900/30 rounded">Component rendered successfully!</div>;
};

const meta: Meta<typeof ErrorBoundary> = {
  title: 'Shared/ErrorBoundary',
  component: ErrorBoundary,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Error boundary component that catches JavaScript errors in the component tree.',
      },
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const NormalRender: Story = {
  render: () => (
    <ErrorBoundary>
      <ErrorThrowingComponent shouldThrow={false} />
    </ErrorBoundary>
  ),
};

export const WithError: Story = {
  render: () => (
    <ErrorBoundary>
      <ErrorThrowingComponent shouldThrow={true} />
    </ErrorBoundary>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Shows the error boundary catching and displaying an error from a child component.',
      },
    },
  },
};

export const ComplexError: Story = {
  render: () => (
    <ErrorBoundary>
      <div className="p-6 space-y-4">
        <h2 className="text-xl font-semibold">Complex Component Tree</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-blue-100 dark:bg-blue-900/30 rounded">
            <h3 className="font-medium">Safe Component</h3>
            <p>This component renders normally.</p>
          </div>
          <ErrorThrowingComponent shouldThrow={true} />
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          The error boundary will catch errors from any component in this tree.
        </p>
      </div>
    </ErrorBoundary>
  ),
};

export const NestedBoundaries: Story = {
  render: () => (
    <ErrorBoundary>
      <div className="p-6 space-y-4">
        <h2 className="text-xl font-semibold">Nested Error Boundaries</h2>

        <ErrorBoundary>
          <div className="p-4 bg-green-100 dark:bg-green-900/30 rounded">
            <h3 className="font-medium">Inner Safe Section</h3>
            <ErrorThrowingComponent shouldThrow={false} />
          </div>
        </ErrorBoundary>

        <ErrorBoundary>
          <div className="p-4 bg-red-100 dark:bg-red-900/30 rounded">
            <h3 className="font-medium">Inner Error Section</h3>
            <ErrorThrowingComponent shouldThrow={true} />
          </div>
        </ErrorBoundary>

        <div className="p-4 bg-blue-100 dark:bg-blue-900/30 rounded">
          <h3 className="font-medium">Outer Safe Section</h3>
          <p>This section remains unaffected by inner errors.</p>
        </div>
      </div>
    </ErrorBoundary>
  ),
  parameters: {
    docs: {
      description: {
        story: 'Demonstrates nested error boundaries where inner boundaries catch their own errors.',
      },
    },
  },
};