import { useState, useRef } from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store';
import { StatusBadge, ProgressIndicator } from '../shared';
import type { DocumentStatus } from '../../store/slices/statusSlice';
import api from '../../services/api';

interface UploadedDocument {
    id: number;
    filename: string;
    status: DocumentStatus;
    error?: string;
    chunk_count?: number;
}

interface DocumentUploadProps {
    workspaceId?: number;
    onUploadComplete?: (documentId: number) => void;
}

export default function DocumentUpload({ workspaceId, onUploadComplete: _onUploadComplete }: DocumentUploadProps) {
    void _onUploadComplete; // Reserved for future use
    const { token } = useSelector((state: RootState) => state.auth);
    const documentStatuses = useSelector((state: RootState) => state.status.documents);
    const [uploading, setUploading] = useState(false);
    const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        setUploading(true);

        try {
            for (const file of Array.from(files)) {
                const formData = new FormData();
                formData.append('file', file);
                if (workspaceId) {
                    formData.append('workspace_id', workspaceId.toString());
                }

                const response = await api.post('/documents/upload', formData, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'multipart/form-data',
                    },
                });

                const doc: UploadedDocument = {
                    id: response.data.id,
                    filename: response.data.filename,
                    status: 'pending',
                };

                setUploadedDocs((prev) => [...prev, doc]);
            }
        } catch (error: unknown) {
            const axiosError = error as { response?: { data?: { detail?: string } } };
            alert(axiosError.response?.data?.detail || 'Failed to upload documents');
        } finally {
            setUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    // Update document statuses from Redux
    const getDocumentStatus = (docId: number): UploadedDocument | undefined => {
        const doc = uploadedDocs.find((d) => d.id === docId);
        if (!doc) return undefined;

        const statusUpdate = documentStatuses[docId];
        if (statusUpdate) {
            return {
                ...doc,
                status: statusUpdate.status,
                error: statusUpdate.error || undefined,
                chunk_count: statusUpdate.chunk_count || undefined,
            };
        }

        return doc;
    };

    const allDocs = uploadedDocs.map((doc) => getDocumentStatus(doc.id) || doc);

    return (
        <div className="space-y-4">
            {/* Upload Button */}
            <div>
                <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.txt,.md,.doc,.docx"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="document-upload"
                />
                <label
                    htmlFor="document-upload"
                    className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer ${
                        uploading ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                >
                    {uploading ? 'Uploading...' : 'Upload Documents'}
                </label>
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    Supported formats: PDF, TXT, MD, DOC, DOCX
                </p>
            </div>

            {/* Uploaded Documents List */}
            {allDocs.length > 0 && (
                <div className="space-y-3">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white">
                        Uploaded Documents
                    </h3>
                    <div className="space-y-2">
                        {allDocs.map((doc) => (
                            <div
                                key={doc.id}
                                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                            >
                                <div className="flex-1 min-w-0 mr-4">
                                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                        {doc.filename}
                                    </p>
                                    {doc.chunk_count && (
                                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                            {doc.chunk_count} chunks
                                        </p>
                                    )}
                                    {doc.error && (
                                        <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                                            {doc.error}
                                        </p>
                                    )}
                                </div>
                                <StatusBadge status={doc.status} />
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Processing Indicator */}
            {allDocs.some((doc) => doc.status === 'processing') && (
                <ProgressIndicator
                    title="Processing documents..."
                    description="This may take a few minutes depending on document size"
                    steps={[
                        { label: 'Parsing document', completed: true },
                        { label: 'Chunking text', completed: true },
                        { label: 'Generating embeddings', completed: false },
                        { label: 'Indexing to vector store', completed: false },
                    ]}
                />
            )}
        </div>
    );
}
