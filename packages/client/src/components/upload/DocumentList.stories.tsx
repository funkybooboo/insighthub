import type { Meta, StoryObj } from '@storybook/react-vite';

// Mock DocumentList component for Storybook to avoid complex dependencies
const MockDocumentList = () => {
    const mockDocuments = [
        {
            id: '1',
            filename: 'research-paper.pdf',
            content_type: 'application/pdf',
            file_size: 2048576,
            status: 'ready',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
        },
        {
            id: '2',
            filename: 'notes.txt',
            content_type: 'text/plain',
            file_size: 1024,
            status: 'processing',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
        },
        {
            id: '3',
            filename: 'presentation.pptx',
            content_type:
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            file_size: 5242880,
            status: 'failed',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
        },
    ];

    return (
        <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Documents ({mockDocuments.length})
            </h3>

            <div className="space-y-2">
                {mockDocuments.map((doc) => (
                    <div
                        key={doc.id}
                        className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                        <div className="flex items-center gap-3 min-w-0">
                            <div className="flex-shrink-0">
                                {doc.content_type === 'application/pdf' && (
                                    <div className="w-8 h-8 bg-red-100 dark:bg-red-900/30 rounded flex items-center justify-center">
                                        <svg
                                            className="w-4 h-4 text-red-600 dark:text-red-400"
                                            fill="currentColor"
                                            viewBox="0 0 20 20"
                                        >
                                            <path
                                                fillRule="evenodd"
                                                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                                                clipRule="evenodd"
                                            />
                                        </svg>
                                    </div>
                                )}
                                {doc.content_type === 'text/plain' && (
                                    <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded flex items-center justify-center">
                                        <svg
                                            className="w-4 h-4 text-blue-600 dark:text-blue-400"
                                            fill="currentColor"
                                            viewBox="0 0 20 20"
                                        >
                                            <path
                                                fillRule="evenodd"
                                                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                                                clipRule="evenodd"
                                            />
                                        </svg>
                                    </div>
                                )}
                                {doc.content_type.includes('presentation') && (
                                    <div className="w-8 h-8 bg-orange-100 dark:bg-orange-900/30 rounded flex items-center justify-center">
                                        <svg
                                            className="w-4 h-4 text-orange-600 dark:text-orange-400"
                                            fill="currentColor"
                                            viewBox="0 0 20 20"
                                        >
                                            <path
                                                fillRule="evenodd"
                                                d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"
                                                clipRule="evenodd"
                                            />
                                        </svg>
                                    </div>
                                )}
                            </div>
                            <div className="min-w-0">
                                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                                    {doc.filename}
                                </p>
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                    {(doc.file_size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <span
                                className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                    doc.status === 'ready'
                                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                                        : doc.status === 'processing'
                                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                                          : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                                }`}
                            >
                                {doc.status}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

const meta: Meta<typeof MockDocumentList> = {
    title: 'Upload/DocumentList',
    component: MockDocumentList,
    parameters: {
        layout: 'padded',
        docs: {
            description: {
                component:
                    'Document list display showing uploaded files with status indicators. (Mock implementation for Storybook)',
            },
        },
    },
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    args: {},
};

export const InUploadManager: Story = {
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

            <div className="p-6">
                <MockDocumentList />
            </div>
        </div>
    ),
};
