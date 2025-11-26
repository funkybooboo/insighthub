import { useState, useRef } from 'react';
import apiService from '@/services/api';
import { LoadingSpinner } from '@/components/shared';
import { AxiosError } from 'axios';
import { logger } from '@/lib/logger';

interface FileUploadProps {
    workspaceId: number;
    onUploadSuccess?: () => void;
    disabled?: boolean;
}

const FileUpload = ({ workspaceId, onUploadSuccess, disabled = false }: FileUploadProps) => {
    const [isUploading, setIsUploading] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const [currentFileError, setCurrentFileError] = useState(''); // Local error for file validation
    const fileInputRef = useRef<HTMLInputElement>(null);

    const processFile = async (file: File) => {
        // Validate file type
        const allowedTypes = ['application/pdf', 'text/plain', 'text/markdown'];
        const allowedExtensions = ['.pdf', '.txt', '.md'];
        const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));

        if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
            setCurrentFileError('Only PDF, TXT, and MD files are allowed');
            return;
        }

        // Validate file size (16MB max)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            setCurrentFileError('File size must be less than 16MB');
            return;
        }

        try {
            setIsUploading(true);
            setCurrentFileError('');

            await apiService.uploadDocument(workspaceId, file);

            // Notify parent component that an upload was initiated (status will come via websockets)
            onUploadSuccess?.();
        } catch (err: unknown) {
             logger.error('Upload initiation error', err as Error, {
                 workspaceId,
                 fileName: file.name,
                 fileSize: file.size,
             });
            const errorMessage =
                err instanceof AxiosError && err.response?.data?.detail
                    ? err.response.data.detail
                    : 'Failed to upload file. Please try again.';
            setCurrentFileError(errorMessage);
        } finally {
            setIsUploading(false);
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
                    ${
                        isDragging
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500'
                    }
                    ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
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
                    disabled={isUploading || disabled}
                />

                {isUploading ? (
                    <div className="flex flex-col items-center gap-2">
                        <LoadingSpinner size="md" />
                        <p className="text-sm text-blue-600 dark:text-blue-400">
                            Upload initiated. Waiting for processing status...
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

            {/* Local error messages */}
            {currentFileError && (
                <div className="mt-3 flex items-center gap-2 text-sm text-red-600 dark:text-red-400">
                    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                        <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                            clipRule="evenodd"
                        />
                    </svg>
                    {currentFileError}
                </div>
            )}
        </div>
    );
};

export default FileUpload;
