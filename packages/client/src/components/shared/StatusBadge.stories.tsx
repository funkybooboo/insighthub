import type { Meta, StoryObj } from '@storybook/react-vite';
import StatusBadge, { type Status } from './StatusBadge';

const meta: Meta<typeof StatusBadge> = {
    title: 'Shared/StatusBadge',
    component: StatusBadge,
    parameters: {
        layout: 'centered',
    },
    tags: ['autodocs'],
    argTypes: {
        status: {
            control: { type: 'select' },
            options: [
                'pending',
                'processing',
                'provisioning',
                'parsing',
                'chunking',
                'embedding',
                'indexing',
                'ready',
                'failed',
                'error',
                'deleting',
            ] as Status[],
        },
        message: {
            control: 'text',
        },
        size: {
            control: { type: 'select' },
            options: ['sm', 'md'],
        },
    },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Pending: Story = {
    args: {
        status: 'pending',
    },
};

export const Processing: Story = {
    args: {
        status: 'processing',
    },
};

export const Ready: Story = {
    args: {
        status: 'ready',
    },
};

export const Failed: Story = {
    args: {
        status: 'failed',
    },
};

export const WithMessage: Story = {
    args: {
        status: 'processing',
        message: 'Processing document chunks...',
    },
};

export const LargeSize: Story = {
    args: {
        status: 'ready',
        size: 'md',
        message: 'Document successfully processed',
    },
};

export const AllStatuses: Story = {
    render: () => (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4">
            {[
                'pending',
                'processing',
                'provisioning',
                'parsing',
                'chunking',
                'embedding',
                'indexing',
                'ready',
                'failed',
                'error',
                'deleting',
            ].map((status) => (
                <div key={status} className="flex flex-col items-center gap-2">
                    <StatusBadge status={status as Status} />
                    <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                        {status}
                    </span>
                </div>
            ))}
        </div>
    ),
};
