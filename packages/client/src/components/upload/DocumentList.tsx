import { useState, useEffect, useImperativeHandle, forwardRef, useCallback } from 'react';
import apiService, { type Document } from '@/services/api';
import { ConfirmDialog } from '@/components/shared';

interface DocumentListProps {
    onDocumentChange?: () => void;
    onDocumentCountChange?: (count: number) => void;
}

export interface DocumentListRef {
    refresh: () => Promise<void>;
}

interface DeleteConfirmState {
    isOpen: boolean;
    docId: number | null;
    filename: string;
}

const DocumentList = forwardRef<DocumentListRef, DocumentListProps>(
    ({ onDocumentChange, onDocumentCountChange }, ref) => {
        const [documents, setDocuments] = useState<Document[]>([]);
        const [loading, setLoading] = useState(true);
        const [error, setError] = useState('');
        const [deletingId, setDeletingId] = useState<number | null>(null);
        const [deleteConfirm, setDeleteConfirm] = useState<DeleteConfirmState>({
            isOpen: false,
            docId: null,
            filename: '',
        });

        const loadDocuments = useCallback(async () => {
            try {
                setLoading(true);
                setError('');
                const response = await apiService.listDocuments();
                setDocuments(response.documents);
                onDocumentCountChange?.(response.documents.length);
            } catch (err) {
                console.error('Error loading documents:', err);
                setError('Failed to load documents');
            } finally {
                setLoading(false);
            }
        }, [onDocumentCountChange]);

        useEffect(() => {
            loadDocuments();
        }, [loadDocuments]);

        useImperativeHandle(ref, () => ({
            refresh: loadDocuments,
        }));

        const handleDeleteClick = (docId: number, filename: string) => {
            setDeleteConfirm({ isOpen: true, docId, filename });
        };

        const handleConfirmDelete = async () => {
            if (!deleteConfirm.docId) return;

            const { docId, filename } = deleteConfirm;
            setDeleteConfirm({ isOpen: false, docId: null, filename: '' });

            try {
                setDeletingId(docId);
                setError('');
                await apiService.deleteDocument(docId);
                setDocuments((prev) => prev.filter((doc) => doc.id !== docId));
                onDocumentChange?.();
            } catch (err) {
                console.error('Error deleting document:', err);
                setError(`Failed to delete "${filename}"`);
            } finally {
                setDeletingId(null);
            }
        };

        const handleCancelDelete = () => {
            setDeleteConfirm({ isOpen: false, docId: null, filename: '' });
        };

        const formatFileSize = (bytes: number): string => {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
        };

        const formatDate = (dateString: string): string => {
            const date = new Date(dateString);
            return (
                date.toLocaleDateString() +
                ' ' +
                date.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                })
            );
        };

        if (loading) {
            return (
                <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                    <div className="animate-spin inline-block w-6 h-6 border-2 border-current border-t-transparent rounded-full" />
                    <p className="mt-2">Loading documents...</p>
                </div>
            );
        }

        if (error && documents.length === 0) {
            return (
                <div className="p-4 text-center text-red-600 dark:text-red-400">
                    <p>{error}</p>
                    <button
                        onClick={loadDocuments}
                        className="mt-2 px-4 py-2 text-sm bg-blue-500 dark:bg-blue-600 text-white rounded hover:bg-blue-600 dark:hover:bg-blue-700"
                    >
                        Retry
                    </button>
                </div>
            );
        }

        return (
            <div className="flex flex-col">
                {error && (
                    <div className="p-2 mb-2 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 rounded">
                        {error}
                    </div>
                )}

                {documents.length === 0 ? (
                    <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                        <svg
                            className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                            />
                        </svg>
                        <p className="mt-2 font-medium">No documents uploaded</p>
                        <p className="text-sm">Upload a PDF or TXT file to get started</p>
                    </div>
                ) : (
                    <div className="divide-y divide-gray-200 dark:divide-gray-700">
                        <div className="px-4 py-2 bg-gray-100 dark:bg-gray-800 flex items-center text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                            <div className="flex-1">Document</div>
                            <div className="w-24 text-right">Size</div>
                            <div className="w-32 text-right">Chunks</div>
                            <div className="w-40 text-right">Uploaded</div>
                            <div className="w-20"></div>
                        </div>
                        {documents.map((doc) => (
                            <div
                                key={doc.id}
                                className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center"
                            >
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        {doc.mime_type === 'application/pdf' ? (
                                            <svg
                                                className="h-5 w-5 text-red-500 flex-shrink-0"
                                                fill="currentColor"
                                                viewBox="0 0 20 20"
                                            >
                                                <path
                                                    fillRule="evenodd"
                                                    d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                                                    clipRule="evenodd"
                                                />
                                            </svg>
                                        ) : (
                                            <svg
                                                className="h-5 w-5 text-gray-500 dark:text-gray-400 flex-shrink-0"
                                                fill="currentColor"
                                                viewBox="0 0 20 20"
                                            >
                                                <path
                                                    fillRule="evenodd"
                                                    d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
                                                    clipRule="evenodd"
                                                />
                                            </svg>
                                        )}
                                        <span className="font-medium text-gray-900 dark:text-gray-100 truncate">
                                            {doc.filename}
                                        </span>
                                    </div>
                                </div>
                                <div className="w-24 text-right text-sm text-gray-500 dark:text-gray-400">
                                    {formatFileSize(doc.file_size)}
                                </div>
                                <div className="w-32 text-right text-sm text-gray-500 dark:text-gray-400">
                                    {doc.chunk_count ? `${doc.chunk_count} chunks` : '-'}
                                </div>
                                <div className="w-40 text-right text-sm text-gray-500 dark:text-gray-400">
                                    {formatDate(doc.created_at)}
                                </div>
                                <div className="w-20 text-right">
                                    <button
                                        onClick={() => handleDeleteClick(doc.id, doc.filename)}
                                        disabled={deletingId === doc.id}
                                        className="p-1 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                                        title="Delete document"
                                    >
                                        {deletingId === doc.id ? (
                                            <div className="animate-spin h-5 w-5 border-2 border-current border-t-transparent rounded-full" />
                                        ) : (
                                            <svg
                                                className="h-5 w-5"
                                                fill="none"
                                                viewBox="0 0 24 24"
                                                stroke="currentColor"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth={2}
                                                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                                />
                                            </svg>
                                        )}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Delete Confirmation Dialog */}
                <ConfirmDialog
                    isOpen={deleteConfirm.isOpen}
                    title="Delete Document"
                    message={`Are you sure you want to delete "${deleteConfirm.filename}"? This action cannot be undone.`}
                    confirmLabel="Delete"
                    variant="danger"
                    onConfirm={handleConfirmDelete}
                    onCancel={handleCancelDelete}
                />
            </div>
        );
    }
);

DocumentList.displayName = 'DocumentList';

export default DocumentList;
