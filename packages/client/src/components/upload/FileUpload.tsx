import { useState } from 'react';
import apiService from '@/services/api';

const FileUpload = () => {
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // Validate file type
        const allowedTypes = ['application/pdf', 'text/plain'];
        if (!allowedTypes.includes(file.type)) {
            setError('Only PDF and TXT files are allowed');
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

            const response = await apiService.uploadDocument(file);
            setMessage(`File "${response.document.filename}" uploaded successfully!`);

            // Clear the input
            event.target.value = '';
        } catch (err) {
            console.error('Upload error:', err);
            setError('Failed to upload file. Please try again.');
        } finally {
            setUploading(false);
        }
    };

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
                    {uploading ? 'Uploading...' : 'Upload Document'}
                    <input
                        type="file"
                        className="hidden"
                        accept=".pdf,.txt"
                        onChange={handleFileChange}
                        disabled={uploading}
                    />
                </label>

                <div className="flex-1">
                    {message && <p className="text-sm text-green-600">{message}</p>}
                    {error && <p className="text-sm text-red-600">{error}</p>}
                    {!message && !error && (
                        <p className="text-sm text-gray-500">Upload PDF or TXT files (max 16MB)</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default FileUpload;
