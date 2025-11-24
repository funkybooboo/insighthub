import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import RAGEnhancementPrompt from './RAGEnhancementPrompt';

// Mock the Button component to avoid CSS/styling issues in tests
vi.mock('@/components/ui/button', () => ({
    Button: ({ children, onClick, disabled, ...props }: any) => (
        <button onClick={onClick} disabled={disabled} {...props}>
            {children}
        </button>
    ),
}));

describe('RAGEnhancementPrompt', () => {
    const defaultProps = {
        isVisible: true,
        onUploadDocument: vi.fn(),
        onFetchWikipedia: vi.fn(),
        onContinueWithoutContext: vi.fn(),
        lastQuery: 'What is RAG?',
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders when visible', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        expect(screen.getByText('Enhance Your Query with Context')).toBeInTheDocument();
    });

    it('does not render when not visible', () => {
        render(<RAGEnhancementPrompt {...defaultProps} isVisible={false} />);
        expect(screen.queryByText('Enhance Your Query with Context')).not.toBeInTheDocument();
    });

    it('calls onUploadDocument when upload button is clicked', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        const uploadButton = screen.getByText('Upload Document');
        fireEvent.click(uploadButton);
        expect(defaultProps.onUploadDocument).toHaveBeenCalled();
    });

    it('calls onFetchWikipedia with lastQuery when Wikipedia button is clicked', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        const wikipediaButton = screen.getByText('Fetch from Wikipedia');
        fireEvent.click(wikipediaButton);
        expect(defaultProps.onFetchWikipedia).toHaveBeenCalledWith('What is RAG?');
    });

    it('calls onContinueWithoutContext when continue button is clicked', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        const continueButton = screen.getByText('Continue Anyway');
        fireEvent.click(continueButton);
        expect(defaultProps.onContinueWithoutContext).toHaveBeenCalled();
    });
});

    it('does not render when not visible', () => {
        render(<RAGEnhancementPrompt {...defaultProps} isVisible={false} />);
        expect(screen.queryByText('Enhance Your Query with Context')).not.toBeInTheDocument();
    });

    it('displays the last query when provided', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        expect(screen.getByText('Query: "What is RAG?"')).toBeInTheDocument();
    });

    it('does not display query text when lastQuery is not provided', () => {
        render(<RAGEnhancementPrompt {...defaultProps} lastQuery={undefined} />);
        expect(screen.queryByText(/Query:/)).not.toBeInTheDocument();
    });

    it('disables Wikipedia button when no lastQuery', () => {
        render(<RAGEnhancementPrompt {...defaultProps} lastQuery={undefined} />);
        const wikipediaButton = screen.getByText('Fetch from Wikipedia');
        expect(wikipediaButton).toBeDisabled();
    });

    it('calls onUploadDocument when upload button is clicked', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        const uploadButton = screen.getByText('Upload Document');
        fireEvent.click(uploadButton);
        expect(defaultProps.onUploadDocument).toHaveBeenCalled();
    });

    it('calls onFetchWikipedia with lastQuery when Wikipedia button is clicked', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        const wikipediaButton = screen.getByText('Fetch from Wikipedia');
        fireEvent.click(wikipediaButton);
        expect(defaultProps.onFetchWikipedia).toHaveBeenCalledWith('What is RAG?');
    });

    it('does not call onFetchWikipedia when Wikipedia button is clicked without lastQuery', () => {
        render(<RAGEnhancementPrompt {...defaultProps} lastQuery={undefined} />);
        const wikipediaButton = screen.getByText('Fetch from Wikipedia');
        fireEvent.click(wikipediaButton);
        expect(defaultProps.onFetchWikipedia).not.toHaveBeenCalled();
    });

    it('calls onContinueWithoutContext when continue button is clicked', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        const continueButton = screen.getByText('Continue Anyway');
        fireEvent.click(continueButton);
        expect(defaultProps.onContinueWithoutContext).toHaveBeenCalled();
    });

    it('does not display query text when lastQuery is not provided', () => {
        render(<RAGEnhancementPrompt {...defaultProps} lastQuery={undefined} />);
        expect(screen.queryByText(/Query:/)).not.toBeInTheDocument();
    });

    it('disables Wikipedia button when no lastQuery', () => {
        render(<RAGEnhancementPrompt {...defaultProps} lastQuery={undefined} />);
        const wikipediaButton = screen.getByText('Fetch from Wikipedia');
        expect(wikipediaButton).toBeDisabled();
    });

    it('calls onUploadDocument when upload button is clicked', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        const uploadButton = screen.getByText('Upload Document');
        fireEvent.click(uploadButton);
        expect(defaultProps.onUploadDocument).toHaveBeenCalled();
    });

    it('calls onFetchWikipedia with lastQuery when Wikipedia button is clicked', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        const wikipediaButton = screen.getByText('Fetch from Wikipedia');
        fireEvent.click(wikipediaButton);
        expect(defaultProps.onFetchWikipedia).toHaveBeenCalledWith('What is RAG?');
    });

    it('does not call onFetchWikipedia when Wikipedia button is clicked without lastQuery', () => {
        render(<RAGEnhancementPrompt {...defaultProps} lastQuery={undefined} />);
        const wikipediaButton = screen.getByText('Fetch from Wikipedia');
        fireEvent.click(wikipediaButton);
        expect(defaultProps.onFetchWikipedia).not.toHaveBeenCalled();
    });

    it('calls onContinueWithoutContext when continue button is clicked', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        const continueButton = screen.getByText('➡️ Continue Anyway');
        fireEvent.click(continueButton);
        expect(defaultProps.onContinueWithoutContext).toHaveBeenCalled();
    });

    it('has proper accessibility attributes', () => {
        render(<RAGEnhancementPrompt {...defaultProps} />);
        const heading = screen.getByRole('heading', { name: /enhance your query/i });
        expect(heading).toBeInTheDocument();
    });
});