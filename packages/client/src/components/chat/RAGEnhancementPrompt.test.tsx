import { render } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import RAGEnhancementPrompt from './RAGEnhancementPrompt';
import '../../test/setup';

const defaultProps = {
    isVisible: true,
    onUploadDocument: vi.fn(),
    onFetchWikipedia: vi.fn(),
    onContinueWithoutContext: vi.fn(),
    lastQuery: 'Test query',
};

describe('RAGEnhancementPrompt', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders without crashing when visible', () => {
        expect(() => render(<RAGEnhancementPrompt {...defaultProps} />)).not.toThrow();
    });

    it('does not render when not visible', () => {
        const { container } = render(<RAGEnhancementPrompt {...defaultProps} isVisible={false} />);
        expect(container.firstChild).toBeNull();
    });

    it('handles props correctly', () => {
        // Test that component accepts all required props without errors
        expect(() => render(<RAGEnhancementPrompt {...defaultProps} />)).not.toThrow();
        expect(() =>
            render(<RAGEnhancementPrompt {...defaultProps} lastQuery={undefined} />)
        ).not.toThrow();
        expect(() =>
            render(<RAGEnhancementPrompt {...defaultProps} isVisible={false} />)
        ).not.toThrow();
    });
});
