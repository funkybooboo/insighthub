/**
 * Component tests for FileUpload
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FileUpload from './FileUpload';
import apiService from '../../services/api';

// Mock API service
vi.mock('../../services/api', () => ({
    default: {
        uploadDocument: vi.fn(),
    },
}));

describe('FileUpload', () => {
    const mockOnUploadSuccess = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('should render upload button', () => {
            render(<FileUpload />);

            const button = screen.getByText('Upload Document');
            expect(button).toBeInTheDocument();
        });

        it('should render file input with correct accept types', () => {
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input');
            expect(input).toHaveAttribute('accept', '.pdf,.txt');
        });

        it('should render default help text', () => {
            render(<FileUpload />);

            expect(screen.getByText('Upload PDF or TXT files (max 16MB)')).toBeInTheDocument();
        });

        it('should render upload icon', () => {
            render(<FileUpload />);

            const button = screen.getByText('Upload Document').closest('label');
            const svg = button?.querySelector('svg');
            expect(svg).toBeInTheDocument();
        });

        it('should hide file input element', () => {
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input');
            expect(input).toHaveClass('hidden');
        });
    });

    describe('File Validation', () => {
        it('should reject non-PDF/TXT files', async () => {
            const user = userEvent.setup();
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });

            await user.upload(input, file);

            expect(
                await screen.findByText('Only PDF and TXT files are allowed')
            ).toBeInTheDocument();
            expect(apiService.uploadDocument).not.toHaveBeenCalled();
        });

        it('should accept PDF files', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'test.pdf',
                    mime_type: 'application/pdf',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

            await user.upload(input, file);

            await waitFor(() => {
                expect(apiService.uploadDocument).toHaveBeenCalledWith(file);
            });
        });

        it('should accept TXT files', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'test.txt',
                    mime_type: 'text/plain',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.txt', { type: 'text/plain' });

            await user.upload(input, file);

            await waitFor(() => {
                expect(apiService.uploadDocument).toHaveBeenCalledWith(file);
            });
        });

        it('should reject files larger than 16MB', async () => {
            const user = userEvent.setup();
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const largeContent = new Uint8Array(17 * 1024 * 1024); // 17MB
            const file = new File([largeContent], 'large.pdf', {
                type: 'application/pdf',
            });

            await user.upload(input, file);

            expect(await screen.findByText('File size must be less than 16MB')).toBeInTheDocument();
            expect(apiService.uploadDocument).not.toHaveBeenCalled();
        });

        it('should accept files exactly at 16MB limit', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'max-size.pdf',
                    mime_type: 'application/pdf',
                    file_size: 16 * 1024 * 1024,
                    chunk_count: 10,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const maxContent = new Uint8Array(16 * 1024 * 1024); // Exactly 16MB
            const file = new File([maxContent], 'max-size.pdf', {
                type: 'application/pdf',
            });

            await user.upload(input, file);

            await waitFor(() => {
                expect(apiService.uploadDocument).toHaveBeenCalledWith(file);
            });
        });

        it('should clear previous errors when uploading new valid file', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'valid.pdf',
                    mime_type: 'application/pdf',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;

            // Upload invalid file
            const invalidFile = new File(['content'], 'test.jpg', { type: 'image/jpeg' });
            await user.upload(input, invalidFile);

            expect(
                await screen.findByText('Only PDF and TXT files are allowed')
            ).toBeInTheDocument();

            // Upload valid file
            const validFile = new File(['content'], 'valid.pdf', {
                type: 'application/pdf',
            });
            await user.upload(input, validFile);

            await waitFor(() => {
                expect(
                    screen.queryByText('Only PDF and TXT files are allowed')
                ).not.toBeInTheDocument();
            });
        });
    });

    describe('Upload Process', () => {
        it('should show uploading state during upload', async () => {
            const user = userEvent.setup();
            let resolveUpload: (value: unknown) => void;
            const uploadPromise = new Promise((resolve) => {
                resolveUpload = resolve;
            });

            vi.mocked(apiService.uploadDocument).mockReturnValueOnce(uploadPromise);
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

            await user.upload(input, file);

            expect(screen.getByText('Uploading...')).toBeInTheDocument();

            resolveUpload!({
                document: {
                    id: 1,
                    filename: 'test.pdf',
                    mime_type: 'application/pdf',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });

            await waitFor(() => {
                expect(screen.queryByText('Uploading...')).not.toBeInTheDocument();
            });
        });

        it('should disable input during upload', async () => {
            const user = userEvent.setup();
            let resolveUpload: (value: unknown) => void;
            const uploadPromise = new Promise((resolve) => {
                resolveUpload = resolve;
            });

            vi.mocked(apiService.uploadDocument).mockReturnValueOnce(uploadPromise);
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

            await user.upload(input, file);

            expect(input).toBeDisabled();

            resolveUpload!({
                document: {
                    id: 1,
                    filename: 'test.pdf',
                    mime_type: 'application/pdf',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });

            await waitFor(() => {
                expect(input).not.toBeDisabled();
            });
        });

        it('should show success message after successful upload', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'success.pdf',
                    mime_type: 'application/pdf',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'success.pdf', { type: 'application/pdf' });

            await user.upload(input, file);

            expect(
                await screen.findByText('File "success.pdf" uploaded successfully!')
            ).toBeInTheDocument();
        });

        it('should clear input value after successful upload', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'test.pdf',
                    mime_type: 'application/pdf',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload />);

            const input = screen
                .getByText('Upload Document')
                .querySelector('input')! as HTMLInputElement;
            const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

            await user.upload(input, file);

            await waitFor(() => {
                expect(input.value).toBe('');
            });
        });

        it('should call onUploadSuccess callback after successful upload', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'test.pdf',
                    mime_type: 'application/pdf',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload onUploadSuccess={mockOnUploadSuccess} />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

            await user.upload(input, file);

            await waitFor(() => {
                expect(mockOnUploadSuccess).toHaveBeenCalledTimes(1);
            });
        });

        it('should not call onUploadSuccess if callback not provided', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'test.pdf',
                    mime_type: 'application/pdf',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

            await user.upload(input, file);

            await waitFor(() => {
                expect(
                    screen.getByText('File "test.pdf" uploaded successfully!')
                ).toBeInTheDocument();
            });
        });

        it('should handle upload error', async () => {
            const user = userEvent.setup();
            const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
            vi.mocked(apiService.uploadDocument).mockRejectedValueOnce(new Error('Network error'));
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

            await user.upload(input, file);

            expect(
                await screen.findByText('Failed to upload file. Please try again.')
            ).toBeInTheDocument();
            expect(consoleErrorSpy).toHaveBeenCalledWith('Upload error:', expect.any(Error));

            consoleErrorSpy.mockRestore();
        });

        it('should re-enable input after upload error', async () => {
            const user = userEvent.setup();
            vi.spyOn(console, 'error').mockImplementation(() => {});
            vi.mocked(apiService.uploadDocument).mockRejectedValueOnce(new Error('Upload failed'));
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

            await user.upload(input, file);

            await waitFor(() => {
                expect(input).not.toBeDisabled();
            });
        });

        it('should handle multiple consecutive uploads', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument)
                .mockResolvedValueOnce({
                    document: {
                        id: 1,
                        filename: 'file1.pdf',
                        mime_type: 'application/pdf',
                        file_size: 1024,
                        chunk_count: 1,
                        created_at: '2024-01-01T00:00:00Z',
                    },
                })
                .mockResolvedValueOnce({
                    document: {
                        id: 2,
                        filename: 'file2.pdf',
                        mime_type: 'application/pdf',
                        file_size: 2048,
                        chunk_count: 2,
                        created_at: '2024-01-01T00:00:00Z',
                    },
                });
            render(<FileUpload onUploadSuccess={mockOnUploadSuccess} />);

            const input = screen.getByText('Upload Document').querySelector('input')!;

            // First upload
            const file1 = new File(['content1'], 'file1.pdf', {
                type: 'application/pdf',
            });
            await user.upload(input, file1);

            await waitFor(() => {
                expect(mockOnUploadSuccess).toHaveBeenCalledTimes(1);
            });

            // Second upload
            const file2 = new File(['content2'], 'file2.pdf', {
                type: 'application/pdf',
            });
            await user.upload(input, file2);

            await waitFor(() => {
                expect(mockOnUploadSuccess).toHaveBeenCalledTimes(2);
            });
        });
    });

    describe('Edge Cases', () => {
        it('should handle empty file selection', async () => {
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;

            // Simulate selecting no file
            const changeEvent = new Event('change', { bubbles: true });
            Object.defineProperty(input, 'files', {
                value: null,
                configurable: true,
            });
            input.dispatchEvent(changeEvent);

            expect(apiService.uploadDocument).not.toHaveBeenCalled();
        });

        it('should handle very small files', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'tiny.txt',
                    mime_type: 'text/plain',
                    file_size: 1,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['a'], 'tiny.txt', { type: 'text/plain' });

            await user.upload(input, file);

            await waitFor(() => {
                expect(apiService.uploadDocument).toHaveBeenCalledWith(file);
            });
        });

        it('should handle files with special characters in filename', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'file @#$%.pdf',
                    mime_type: 'application/pdf',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'file @#$%.pdf', {
                type: 'application/pdf',
            });

            await user.upload(input, file);

            expect(
                await screen.findByText('File "file @#$%.pdf" uploaded successfully!')
            ).toBeInTheDocument();
        });

        it('should clear success message when uploading new file', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument)
                .mockResolvedValueOnce({
                    document: {
                        id: 1,
                        filename: 'first.pdf',
                        mime_type: 'application/pdf',
                        file_size: 1024,
                        chunk_count: 1,
                        created_at: '2024-01-01T00:00:00Z',
                    },
                })
                .mockResolvedValueOnce({
                    document: {
                        id: 2,
                        filename: 'second.pdf',
                        mime_type: 'application/pdf',
                        file_size: 2048,
                        chunk_count: 2,
                        created_at: '2024-01-01T00:00:00Z',
                    },
                });
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;

            // First upload
            const file1 = new File(['content1'], 'first.pdf', {
                type: 'application/pdf',
            });
            await user.upload(input, file1);

            expect(
                await screen.findByText('File "first.pdf" uploaded successfully!')
            ).toBeInTheDocument();

            // Second upload
            const file2 = new File(['content2'], 'second.pdf', {
                type: 'application/pdf',
            });
            await user.upload(input, file2);

            await waitFor(() => {
                expect(
                    screen.queryByText('File "first.pdf" uploaded successfully!')
                ).not.toBeInTheDocument();
            });

            expect(
                screen.getByText('File "second.pdf" uploaded successfully!')
            ).toBeInTheDocument();
        });
    });

    describe('Accessibility', () => {
        it('should have accessible label for file input', () => {
            render(<FileUpload />);

            const label = screen.getByText('Upload Document').closest('label');
            expect(label).toBeInTheDocument();
        });

        it('should have visible error messages', async () => {
            const user = userEvent.setup();
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.jpg', { type: 'image/jpeg' });

            await user.upload(input, file);

            const errorMessage = await screen.findByText('Only PDF and TXT files are allowed');
            expect(errorMessage).toBeVisible();
        });

        it('should have visible success messages', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.uploadDocument).mockResolvedValueOnce({
                document: {
                    id: 1,
                    filename: 'test.pdf',
                    mime_type: 'application/pdf',
                    file_size: 1024,
                    chunk_count: 1,
                    created_at: '2024-01-01T00:00:00Z',
                },
            });
            render(<FileUpload />);

            const input = screen.getByText('Upload Document').querySelector('input')!;
            const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });

            await user.upload(input, file);

            const successMessage = await screen.findByText(
                'File "test.pdf" uploaded successfully!'
            );
            expect(successMessage).toBeVisible();
        });
    });
});
