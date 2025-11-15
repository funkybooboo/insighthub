/**
 * Storybook stories for FileUpload component
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn } from '@storybook/test';
import { within, expect } from '@storybook/test';
import FileUpload from './FileUpload';

const meta: Meta<typeof FileUpload> = {
    title: 'Upload/FileUpload',
    component: FileUpload,
    parameters: {
        layout: 'padded',
        docs: {
            description: {
                component:
                    'File upload component for uploading PDF and TXT files. Supports files up to 16MB with validation.',
            },
        },
    },
    args: {
        onUploadSuccess: fn(),
    },
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof FileUpload>;

export const Default: Story = {
    name: 'Default State',
    parameters: {
        docs: {
            description: {
                story: 'The default state shows the upload button and help text.',
            },
        },
    },
};

export const HoverState: Story = {
    name: 'Hover State',
    parameters: {
        docs: {
            description: {
                story: 'The upload button changes color on hover to indicate interactivity.',
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const label = canvas.getByText('Upload Document').closest('label');

        if (label) {
            // Check that the label exists and has the correct classes
            expect(label).toHaveClass('bg-blue-500');
            expect(label).toHaveClass('hover:bg-blue-600');
        }
    },
};

export const WithHelpText: Story = {
    name: 'With Help Text',
    parameters: {
        docs: {
            description: {
                story:
                    'Help text is displayed when there are no messages or errors, showing accepted file types and size limit.',
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const helpText = canvas.getByText('Upload PDF or TXT files (max 16MB)');

        expect(helpText).toBeInTheDocument();
        expect(helpText).toHaveClass('text-gray-500');
    },
};

export const SuccessMessage: Story = {
    name: 'Success Message (Mocked)',
    parameters: {
        docs: {
            description: {
                story:
                    'After successful upload, a green success message is displayed with the filename.',
            },
        },
    },
    render: () => {
        // Mock component with success state
        return (
            <div className="p-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg cursor-pointer hover:bg-blue-600 transition-colors">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                        Upload Document
                        <input type="file" className="hidden" accept=".pdf,.txt" />
                    </label>

                    <div className="flex-1">
                        <p className="text-sm text-green-600">
                            File "example-document.pdf" uploaded successfully!
                        </p>
                    </div>
                </div>
            </div>
        );
    },
};

export const ErrorMessage: Story = {
    name: 'Error Message (Mocked)',
    parameters: {
        docs: {
            description: {
                story:
                    'Error messages are displayed in red when validation fails or upload errors occur.',
            },
        },
    },
    render: () => {
        return (
            <div className="p-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg cursor-pointer hover:bg-blue-600 transition-colors">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                        Upload Document
                        <input type="file" className="hidden" accept=".pdf,.txt" />
                    </label>

                    <div className="flex-1">
                        <p className="text-sm text-red-600">
                            Only PDF and TXT files are allowed
                        </p>
                    </div>
                </div>
            </div>
        );
    },
};

export const UploadingState: Story = {
    name: 'Uploading State (Mocked)',
    parameters: {
        docs: {
            description: {
                story:
                    'During upload, the button shows "Uploading..." text and the file input is disabled.',
            },
        },
    },
    render: () => {
        return (
            <div className="p-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg cursor-pointer hover:bg-blue-600 transition-colors opacity-75">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                        Uploading...
                        <input type="file" className="hidden" accept=".pdf,.txt" disabled />
                    </label>

                    <div className="flex-1">
                        <p className="text-sm text-gray-500">
                            Upload PDF or TXT files (max 16MB)
                        </p>
                    </div>
                </div>
            </div>
        );
    },
};

export const FileSizeError: Story = {
    name: 'File Size Error (Mocked)',
    parameters: {
        docs: {
            description: {
                story: 'Shows error message when file exceeds 16MB size limit.',
            },
        },
    },
    render: () => {
        return (
            <div className="p-4 border-b border-gray-200 bg-gray-50">
                <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg cursor-pointer hover:bg-blue-600 transition-colors">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                        Upload Document
                        <input type="file" className="hidden" accept=".pdf,.txt" />
                    </label>

                    <div className="flex-1">
                        <p className="text-sm text-red-600">File size must be less than 16MB</p>
                    </div>
                </div>
            </div>
        );
    },
};

export const AcceptedFileTypes: Story = {
    name: 'Accepted File Types',
    parameters: {
        docs: {
            description: {
                story:
                    'The file input only accepts .pdf and .txt files as specified in the accept attribute.',
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const input = canvas.getByText('Upload Document').querySelector('input');

        if (input) {
            expect(input).toHaveAttribute('accept', '.pdf,.txt');
        }
    },
};
