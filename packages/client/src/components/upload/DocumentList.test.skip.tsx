/**
 * Component tests for DocumentList
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { createRef } from 'react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import DocumentList, { type DocumentListRef } from './DocumentList';
import apiService, { type Document } from '../../services/api';
import statusReducer from '../../store/slices/statusSlice';

// Mock useSelector
vi.mock('react-redux', async () => {
    const actual = await vi.importActual('react-redux');
    return {
        ...actual,
        useSelector: vi.fn(() => ({})),
        Provider: actual.Provider,
    };
});

// Mock API service
vi.mock('../../services/api', () => ({
    default: {
        listDocuments: vi.fn().mockResolvedValue({ documents: [], count: 0 }),
        deleteDocument: vi.fn().mockResolvedValue(undefined),
    },
}));

// Mock Redux store
vi.mock('react-redux', () => ({
    useSelector: vi.fn(),
}));

// Mock window.confirm
const mockConfirm = vi.fn();
window.confirm = mockConfirm;



describe('DocumentList', () => {
    const mockDocuments: Document[] = [
        {
            id: 1,
            filename: 'document1.pdf',
            mime_type: 'application/pdf',
            file_size: 1024000,
            chunk_count: 5,
            created_at: '2024-01-01T10:30:00Z',
        },
        {
            id: 2,
            filename: 'document2.txt',
            mime_type: 'text/plain',
            file_size: 2048,
            chunk_count: 1,
            created_at: '2024-01-02T15:45:00Z',
        },
    ];

    beforeEach(() => {
        vi.clearAllMocks();
        mockConfirm.mockReturnValue(true);
    });

    describe('Loading State', () => {
        it('should show loading state initially', () => {
            vi.mocked(apiService.listDocuments).mockImplementationOnce(() => new Promise(() => {}));
            render(<DocumentList workspaceId={1} />);

            expect(screen.getByText('Loading documents...')).toBeInTheDocument();
        });

        it('should show loading spinner while loading', () => {
            vi.mocked(apiService.listDocuments).mockImplementationOnce(() => new Promise(() => {}));
            const { container } = render(<DocumentList workspaceId={1} />);

            const spinner = container.querySelector('.animate-spin');
            expect(spinner).toBeInTheDocument();
        });

        it('should hide loading state after documents load', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.queryByText('Loading documents...')).not.toBeInTheDocument();
            });
        });
    });

    describe('Empty State', () => {
        it('should show empty state when no documents exist', async () => {
            const mockListDocuments = vi.mocked(apiService.listDocuments);
            mockListDocuments.mockResolvedValueOnce({
                documents: [],
                count: 0,
            });
            const { container } = render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(mockListDocuments).toHaveBeenCalledWith(1);
            });

            expect(container.textContent).toContain('No documents uploaded');
            expect(container.textContent).toContain('Upload a PDF or TXT file to get started');
        });

        it('should show empty state icon', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [],
            });
            const { container } = render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                const icon = container.querySelector('svg');
                expect(icon).toBeInTheDocument();
            });
        });
    });

    describe('Document Rendering', () => {
        it('should render all documents', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText('document1.pdf')).toBeInTheDocument();
            expect(screen.getByText('document2.txt')).toBeInTheDocument();
        });

        it('should render table headers', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('Document')).toBeInTheDocument();
                expect(screen.getByText('Status')).toBeInTheDocument();
                expect(screen.getByText('Size')).toBeInTheDocument();
                expect(screen.getByText('Chunks')).toBeInTheDocument();
                expect(screen.getByText('Uploaded')).toBeInTheDocument();
            });
        });

        it('should render PDF icon for PDF files', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [mockDocuments[0]],
            });
            const { container } = render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                const pdfIcon = container.querySelector('.text-red-500');
                expect(pdfIcon).toBeInTheDocument();
            });
        });

        it('should render text icon for TXT files', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [mockDocuments[1]],
            });
            const { container } = render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                const textIcon = container.querySelector('.text-gray-500');
                expect(textIcon).toBeInTheDocument();
            });
        });

        it('should display formatted file sizes', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText('1000 KB')).toBeInTheDocument();
            expect(screen.getByText('2 KB')).toBeInTheDocument();
        });

        it('should display chunk counts', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText('5')).toBeInTheDocument();
            expect(screen.getByText('1')).toBeInTheDocument();
        });

        it('should display formatted dates', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                // Dates should be formatted (exact format depends on locale)
                const dateElements = screen.getAllByText(/\d{1,2}\/\d{1,2}\/\d{4}/);
                expect(dateElements.length).toBeGreaterThan(0);
            });
        });

        it('should render delete button for each document', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                const deleteButtons = screen.getAllByTitle('Delete document');
                expect(deleteButtons).toHaveLength(2);
            });
        });
    });

    describe('File Size Formatting', () => {
        it('should format 0 bytes correctly', async () => {
            const doc: Document = {
                ...mockDocuments[0],
                file_size: 0,
            };
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [doc],
            });
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText('0 Bytes')).toBeInTheDocument();
        });

        it('should format bytes correctly', async () => {
            const doc: Document = {
                ...mockDocuments[0],
                file_size: 500,
            };
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [doc],
            });
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText('500 Bytes')).toBeInTheDocument();
        });

        it('should format kilobbytes correctly', async () => {
            const doc: Document = {
                ...mockDocuments[0],
                file_size: 1536,
            };
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [doc],
            });
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText('1.5 KB')).toBeInTheDocument();
        });

        it('should format megabytes correctly', async () => {
            const doc: Document = {
                ...mockDocuments[0],
                file_size: 5242880,
            };
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [doc],
            });
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText('5 MB')).toBeInTheDocument();
        });
    });

    describe('Delete Functionality', () => {
        it('should show confirmation dialog when delete is clicked', async () => {
            const user = userEvent.setup();
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('document1.pdf')).toBeInTheDocument();
            });

            const deleteButtons = screen.getAllByTitle('Delete document');
            await user.click(deleteButtons[0]);

            expect(mockConfirm).toHaveBeenCalledWith(
                'Are you sure you want to delete "document1.pdf"?'
            );
        });

        it('should delete document when confirmed', async () => {
            const user = userEvent.setup();
            mockConfirm.mockReturnValue(true);
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            vi.mocked(apiService.deleteDocument).mockResolvedValueOnce(undefined);
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('document1.pdf')).toBeInTheDocument();
            });

            const deleteButtons = screen.getAllByTitle('Delete document');
            await user.click(deleteButtons[0]);

            await waitFor(() => {
                expect(apiService.deleteDocument).toHaveBeenCalledWith(1);
            });

            await waitFor(() => {
                expect(screen.queryByText('document1.pdf')).not.toBeInTheDocument();
            });
        });

        it('should not delete document when cancelled', async () => {
            const user = userEvent.setup();
            mockConfirm.mockReturnValue(false);
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('document1.pdf')).toBeInTheDocument();
            });

            const deleteButtons = screen.getAllByTitle('Delete document');
            await user.click(deleteButtons[0]);

            expect(apiService.deleteDocument).not.toHaveBeenCalled();
            expect(screen.getByText('document1.pdf')).toBeInTheDocument();
        });

        it('should show loading spinner while deleting', async () => {
            const user = userEvent.setup();
            let resolveDelete: (value: unknown) => void;
            const deletePromise = new Promise((resolve) => {
                resolveDelete = resolve;
            });

            mockConfirm.mockReturnValue(true);
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            vi.mocked(apiService.deleteDocument).mockReturnValueOnce(deletePromise);
            const { container } = render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('document1.pdf')).toBeInTheDocument();
            });

            const deleteButtons = screen.getAllByTitle('Delete document');
            await user.click(deleteButtons[0]);

            await waitFor(() => {
                const spinner = container.querySelector('.animate-spin');
                expect(spinner).toBeInTheDocument();
            });

            resolveDelete!(undefined);
        });

        it('should disable delete button while deleting', async () => {
            const user = userEvent.setup();
            let resolveDelete: (value: unknown) => void;
            const deletePromise = new Promise((resolve) => {
                resolveDelete = resolve;
            });

            mockConfirm.mockReturnValue(true);
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            vi.mocked(apiService.deleteDocument).mockReturnValueOnce(deletePromise);
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('document1.pdf')).toBeInTheDocument();
            });

            const deleteButtons = screen.getAllByTitle('Delete document');
            await user.click(deleteButtons[0]);

            await waitFor(() => {
                expect(deleteButtons[0]).toBeDisabled();
            });

            resolveDelete!(undefined);
        });

        it('should handle delete error', async () => {
            const user = userEvent.setup();
            const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
            mockConfirm.mockReturnValue(true);
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            vi.mocked(apiService.deleteDocument).mockRejectedValueOnce(new Error('Delete failed'));
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('document1.pdf')).toBeInTheDocument();
            });

            const deleteButtons = screen.getAllByTitle('Delete document');
            await user.click(deleteButtons[0]);

            expect(await screen.findByText('Failed to delete "document1.pdf"')).toBeInTheDocument();
            expect(consoleErrorSpy).toHaveBeenCalledWith(
                'Error deleting document:',
                expect.any(Error)
            );

            consoleErrorSpy.mockRestore();
        });

        it('should call onDocumentChange callback after deletion', async () => {
            const user = userEvent.setup();
            const mockOnDocumentChange = vi.fn();
            mockConfirm.mockReturnValue(true);
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            vi.mocked(apiService.deleteDocument).mockResolvedValueOnce(undefined);
            render(<DocumentList workspaceId={1} onDocumentChange={mockOnDocumentChange} />);

            await waitFor(() => {
                expect(screen.getByText('document1.pdf')).toBeInTheDocument();
            });

            const deleteButtons = screen.getAllByTitle('Delete document');
            await user.click(deleteButtons[0]);

            await waitFor(() => {
                expect(mockOnDocumentChange).toHaveBeenCalledTimes(1);
            });
        });
    });

    describe('Error Handling', () => {
        it('should show error state when loading fails', async () => {
            const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
            vi.mocked(apiService.listDocuments).mockRejectedValueOnce(new Error('Network error'));
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText('Failed to load documents')).toBeInTheDocument();
            expect(consoleErrorSpy).toHaveBeenCalledWith(
                'Error loading documents:',
                expect.any(Error)
            );

            consoleErrorSpy.mockRestore();
        });

        it('should show retry button on error', async () => {
            vi.spyOn(console, 'error').mockImplementation(() => {});
            vi.mocked(apiService.listDocuments).mockRejectedValueOnce(new Error('Network error'));
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByRole('button', { name: /retry/i })).toBeInTheDocument();
        });

        it('should retry loading when retry button is clicked', async () => {
            const user = userEvent.setup();
            vi.spyOn(console, 'error').mockImplementation(() => {});
            vi.mocked(apiService.listDocuments)
                .mockRejectedValueOnce(new Error('Network error'))
                .mockResolvedValueOnce({ documents: mockDocuments });
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('Failed to load documents')).toBeInTheDocument();
            });

            const retryButton = screen.getByRole('button', { name: /retry/i });
            await user.click(retryButton);

            expect(await screen.findByText('document1.pdf')).toBeInTheDocument();
        });

        it('should show error banner when documents exist but operation fails', async () => {
            const user = userEvent.setup();
            const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
            mockConfirm.mockReturnValue(true);
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            vi.mocked(apiService.deleteDocument).mockRejectedValueOnce(new Error('Delete failed'));
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('document1.pdf')).toBeInTheDocument();
            });

            const deleteButtons = screen.getAllByTitle('Delete document');
            await user.click(deleteButtons[0]);

            const errorBanner = await screen.findByText('Failed to delete "document1.pdf"');
            expect(errorBanner).toBeInTheDocument();
            expect(errorBanner.closest('div')).toHaveClass('bg-red-50');

            consoleErrorSpy.mockRestore();
        });
    });

    describe('Ref API', () => {
        it('should expose refresh method via ref', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [],
            });
            const ref = createRef<DocumentListRef>();
            render(<DocumentList ref={ref} workspaceId={1} />);

            await waitFor(() => {
                expect(ref.current).toBeTruthy();
                expect(ref.current?.refresh).toBeInstanceOf(Function);
            });
        });

        it('should reload documents when refresh is called', async () => {
            vi.mocked(apiService.listDocuments)
                .mockResolvedValueOnce({ documents: [] })
                .mockResolvedValueOnce({ documents: mockDocuments });
            const ref = createRef<DocumentListRef>();
            render(<DocumentList ref={ref} workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('No documents uploaded')).toBeInTheDocument();
            });

            await ref.current?.refresh();

            expect(await screen.findByText('document1.pdf')).toBeInTheDocument();
        });

        it('should call API twice when refresh is called', async () => {
            vi.mocked(apiService.listDocuments)
                .mockResolvedValueOnce({ documents: [] })
                .mockResolvedValueOnce({ documents: mockDocuments });
            const ref = createRef<DocumentListRef>();
            render(<DocumentList ref={ref} workspaceId={1} />);

            await waitFor(() => {
                expect(apiService.listDocuments).toHaveBeenCalledTimes(1);
            });

            await ref.current?.refresh();

            expect(apiService.listDocuments).toHaveBeenCalledTimes(2);
        });
    });

    describe('Callbacks', () => {
        it('should call onDocumentCountChange with document count on load', async () => {
            const mockOnDocumentCountChange = vi.fn();
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} onDocumentCountChange={mockOnDocumentCountChange} />);

            await waitFor(() => {
                expect(mockOnDocumentCountChange).toHaveBeenCalledWith(2);
            });
        });

        it('should call onDocumentCountChange with 0 when no documents', async () => {
            const mockOnDocumentCountChange = vi.fn();
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [],
            });
            render(<DocumentList workspaceId={1} onDocumentCountChange={mockOnDocumentCountChange} />);

            await waitFor(() => {
                expect(mockOnDocumentCountChange).toHaveBeenCalledWith(0);
            });
        });
    });

    describe('Edge Cases', () => {
        it('should handle document with null chunk_count', async () => {
            const doc: Document = {
                ...mockDocuments[0],
                chunk_count: null as unknown as number,
            };
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [doc],
            });
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText('-')).toBeInTheDocument();
        });

        it('should handle document with very long filename', async () => {
            const longFilename = 'a'.repeat(100) + '.pdf';
            const doc: Document = {
                ...mockDocuments[0],
                filename: longFilename,
            };
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [doc],
            });
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText(longFilename)).toBeInTheDocument();
        });

        it('should handle document with special characters in filename', async () => {
            const doc: Document = {
                ...mockDocuments[0],
                filename: 'file @#$%&.pdf',
            };
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: [doc],
            });
            render(<DocumentList workspaceId={1} />);

            expect(await screen.findByText('file @#$%&.pdf')).toBeInTheDocument();
        });

        it('should handle many documents', async () => {
            const manyDocuments = Array.from({ length: 100 }, (_, i) => ({
                id: i + 1,
                filename: `document${i + 1}.pdf`,
                mime_type: 'application/pdf',
                file_size: 1024,
                chunk_count: 1,
                created_at: '2024-01-01T00:00:00Z',
            }));

            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: manyDocuments as Document[],
            });
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                expect(screen.getByText('document1.pdf')).toBeInTheDocument();
                expect(screen.getByText('document100.pdf')).toBeInTheDocument();
            });
        });
    });

    describe('Accessibility', () => {
        it('should have visible document information', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                const filename = screen.getByText('document1.pdf');
                expect(filename).toBeVisible();
            });
        });

        it('should have accessible delete buttons with titles', async () => {
            vi.mocked(apiService.listDocuments).mockResolvedValueOnce({
                documents: mockDocuments,
            });
            render(<DocumentList workspaceId={1} />);

            await waitFor(() => {
                const deleteButtons = screen.getAllByTitle('Delete document');
                deleteButtons.forEach((button) => {
                    expect(button).toBeInTheDocument();
                });
            });
        });

        it('should show loading spinner with accessible text', () => {
            apiService.listDocuments.mockImplementationOnce(() => new Promise(() => {}));
            render(<DocumentList workspaceId={1} />);

            const loadingText = screen.getByText('Loading documents...');
            expect(loadingText).toBeVisible();
        });
    });
});
