import { useState, useRef } from 'react';
import apiService from '@/services/api';
import { LoadingSpinner } from '@/components/shared';

interface FileUploadProps {
    workspaceId: number;
    onUploadSuccess?: () => void;
}

const FileUpload = ({ workspaceId, onUploadSuccess }: FileUploadProps) => {
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState<string | null>(null);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const processFile = async (file: File) => {
        // Validate file type
        const allowedTypes = ['application/pdf', 'text/plain', 'text/markdown'];
        const allowedExtensions = ['.pdf', '.txt', '.md'];
        const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));

        if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
            setError('Only PDF, TXT, and MD files are allowed');
            return;
        }

        // Validate file size (16MB max)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            setError('File size must be less than 16MB');
            return;
        }

        try {
            setUploading(true);
            setError('');
            setMessage('');
            setUploadProgress('Uploading file...');

            const response = await apiService.uploadDocument(workspaceId, file);
            setUploadProgress(null);
            setMessage(`"${response.document.filename}" uploaded. Processing...`);

            // Notify parent component
            onUploadSuccess?.();

            // Clear success message after 5 seconds
            setTimeout(() => setMessage(''), 5000);
        } catch (err) {
            console.error('Upload error:', err);
            setError('Failed to upload file. Please try again.');
            setUploadProgress(null);
        } finally {
            setUploading(false);
        }
    };

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;
        await processFile(file);
        // Clear the input
        event.target.value = '';
    };

    const handleDrop = async (event: React.DragEvent<HTMLDivElement>) => {
        event.preventDefault();
        setIsDragging(false);

        const file = event.dataTransfer.files[0];
        if (file) {
            await processFile(file);
        }
    };

    const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
        event.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
        event.preventDefault();
        setIsDragging(false);
    };

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    return (
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
            <div
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer
                    ${isDragging
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500'
                    }
                    ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={handleClick}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    className="hidden"
                    accept=".pdf,.txt,.md"
                    onChange={handleFileChange}
                    disabled={uploading}
                />

                {uploading ? (
                    <div className="flex flex-col items-center gap-2">
                        <LoadingSpinner size="md" />
                        <p className="text-sm text-blue-600 dark:text-blue-400">
                            {uploadProgress || 'Processing...'}
                        </p>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-2">
                        <svg
                            className="h-10 w-10 text-gray-400 dark:text-gray-500"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={1.5}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                        <div>
                            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                Drop files here or click to upload
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                PDF, TXT, or MD files (max 16MB)
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* Status messages */}
            {(message || error) && (
                <div className="mt-3">
                    {message && (
                        <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                                <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clipRule="evenodd"
                                />
                            </svg>
                            {message}
                        </div>
                    )}
                    {error && (
                        <div className="flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
                            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                                <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                    clipRule="evenodd"
                                />
                            </svg>
                            {error}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default FileUpload;
