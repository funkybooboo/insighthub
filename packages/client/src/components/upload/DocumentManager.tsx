import { useState, useRef } from 'react';
import DocumentList, { type DocumentListRef } from './DocumentList';
import FileUpload from './FileUpload';

interface DocumentManagerProps {
    isExpanded?: boolean;
}

const DocumentManager = ({ isExpanded: initialExpanded = false }: DocumentManagerProps) => {
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
        <div className="border-b border-gray-200 bg-white">
            {/* Header with toggle */}
            <div
                className="px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-gray-50"
                onClick={toggleExpanded}
            >
                <div className="flex items-center gap-3">
                    <svg
                        className="h-5 w-5 text-gray-500"
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
                    <h2 className="font-semibold text-gray-900">Document Management</h2>
                    {documentCount > 0 && (
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                            {documentCount} {documentCount === 1 ? 'document' : 'documents'}
                        </span>
                    )}
                </div>
                <svg
                    className={`h-5 w-5 text-gray-500 transition-transform ${
                        isExpanded ? 'transform rotate-180' : ''
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
            </div>

            {/* Expandable content */}
            {isExpanded && (
                <div className="border-t border-gray-200">
                    <FileUpload onUploadSuccess={handleDocumentChange} />
                    <DocumentList
                        ref={documentListRef}
                        onDocumentChange={handleDocumentChange}
                        onDocumentCountChange={handleDocumentCountChange}
                    />
                </div>
            )}
        </div>
    );
};

export default DocumentManager;
