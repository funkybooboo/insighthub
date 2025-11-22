import { useState, useRef } from 'react';
import DocumentList, { type DocumentListRef } from './DocumentList';
import FileUpload from './FileUpload';

interface DocumentManagerProps {
    workspaceId: number;
    isExpanded?: boolean;
}

const DocumentManager = ({ workspaceId, isExpanded: initialExpanded = false }: DocumentManagerProps) => {
    const [isExpanded, setIsExpanded] = useState(initialExpanded);
    const [documentCount, setDocumentCount] = useState(0);
    const documentListRef = useRef<DocumentListRef>(null);

    const handleDocumentChange = () => {
        // Trigger refresh of document list when documents change
        documentListRef.current?.refresh();
    };

    const handleDocumentCountChange = (count: number) => {
        setDocumentCount(count);
    };

    const toggleExpanded = () => {
        setIsExpanded((prev) => !prev);
    };

    return (
        <div className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
            <button
                className="w-full px-6 py-3 flex items-center justify-between hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                onClick={toggleExpanded}
            >
                <div className="flex items-center gap-3">
                    <svg
                        className="h-5 w-5 text-gray-600 dark:text-gray-400"
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
                    <span className="font-medium text-gray-900 dark:text-gray-100">Documents</span>
                    {documentCount > 0 && (
                        <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full">
                            {documentCount}
                        </span>
                    )}
                </div>
                <svg
                    className={`h-5 w-5 text-gray-500 dark:text-gray-400 transition-transform ${
                        isExpanded ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 9l-7 7-7-7"
                    />
                </svg>
            </button>

            {isExpanded && (
                <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                    <FileUpload workspaceId={workspaceId} onUploadSuccess={handleDocumentChange} />
                    <DocumentList
                        ref={documentListRef}
                        workspaceId={workspaceId}
                        onDocumentChange={handleDocumentChange}
                        onDocumentCountChange={handleDocumentCountChange}
                    />
                </div>
            )}
        </div>
    );
};

export default DocumentManager;
