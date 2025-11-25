import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import ConfirmDialog from './ConfirmDialog';

const meta: Meta<typeof ConfirmDialog> = {
    title: 'Shared/ConfirmDialog',
    component: ConfirmDialog,
    parameters: {
        layout: 'fullscreen',
    },
    tags: ['autodocs'],
    argTypes: {
        isOpen: {
            control: 'boolean',
        },
        title: {
            control: 'text',
        },
        message: {
            control: 'text',
        },
        confirmLabel: {
            control: 'text',
        },
        cancelLabel: {
            control: 'text',
        },
        variant: {
            control: { type: 'select' },
            options: ['default', 'danger', 'warning'],
        },
    },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    args: {
        isOpen: true,
        title: 'Confirm Action',
        message: 'Are you sure you want to proceed with this action?',
        confirmLabel: 'Confirm',
        cancelLabel: 'Cancel',
        variant: 'default',
        onConfirm: () => console.log('Confirmed'),
        onCancel: () => console.log('Cancelled'),
    },
};

export const Danger: Story = {
    args: {
        isOpen: true,
        title: 'Delete Document',
        message: 'This action cannot be undone. Are you sure you want to delete this document?',
        confirmLabel: 'Delete',
        cancelLabel: 'Cancel',
        variant: 'danger',
        onConfirm: () => console.log('Document deleted'),
        onCancel: () => console.log('Deletion cancelled'),
    },
};

export const Warning: Story = {
    args: {
        isOpen: true,
        title: 'Warning',
        message: 'This action may have unintended consequences. Do you want to continue?',
        confirmLabel: 'Continue',
        cancelLabel: 'Go Back',
        variant: 'warning',
        onConfirm: () => console.log('Continued'),
        onCancel: () => console.log('Went back'),
    },
};

export const Interactive: Story = {
    render: () => {
        const [isOpen, setIsOpen] = useState(false);
        const [variant, setVariant] = useState<'default' | 'danger' | 'warning'>('default');

        return (
            <div className="p-8 space-y-4">
                <div className="flex gap-4">
                    <button
                        onClick={() => {
                            setVariant('default');
                            setIsOpen(true);
                        }}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        Open Default Dialog
                    </button>
                    <button
                        onClick={() => {
                            setVariant('danger');
                            setIsOpen(true);
                        }}
                        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                    >
                        Open Danger Dialog
                    </button>
                    <button
                        onClick={() => {
                            setVariant('warning');
                            setIsOpen(true);
                        }}
                        className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                    >
                        Open Warning Dialog
                    </button>
                </div>

                <ConfirmDialog
                    isOpen={isOpen}
                    title={
                        variant === 'danger'
                            ? 'Delete Item'
                            : variant === 'warning'
                              ? 'Warning'
                              : 'Confirm Action'
                    }
                    message={
                        variant === 'danger'
                            ? 'This action cannot be undone. Are you sure?'
                            : variant === 'warning'
                              ? 'This may have unintended consequences.'
                              : 'Are you sure you want to proceed?'
                    }
                    variant={variant}
                    onConfirm={() => {
                        console.log(`${variant} action confirmed`);
                        setIsOpen(false);
                    }}
                    onCancel={() => {
                        console.log(`${variant} action cancelled`);
                        setIsOpen(false);
                    }}
                />
            </div>
        );
    },
};
