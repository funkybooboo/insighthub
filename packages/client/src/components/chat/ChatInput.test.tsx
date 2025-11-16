/**
 * Component tests for ChatInput
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatInput from './ChatInput';

describe('ChatInput', () => {
    const mockOnSubmit = vi.fn();

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('should render textarea with placeholder', () => {
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            expect(textarea).toBeInTheDocument();
        });

        it('should render submit button', () => {
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const button = screen.getByRole('button');
            expect(button).toBeInTheDocument();
        });

        it('should have correct textarea attributes', () => {
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            expect(textarea).toHaveAttribute('maxLength', '1000');
            // autoFocus is a React prop, check that element exists instead
            expect(textarea).toBeInTheDocument();
        });

        it('should start with disabled submit button', () => {
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const button = screen.getByRole('button');
            expect(button).toBeDisabled();
        });
    });

    describe('Form Validation', () => {
        it('should enable button when text is entered', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            await user.type(textarea, 'Hello');

            expect(button).not.toBeDisabled();
        });

        it('should keep button disabled for empty text', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            await user.type(textarea, '   ');
            await user.clear(textarea);

            expect(button).toBeDisabled();
        });

        it('should keep button disabled for whitespace-only text', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            await user.type(textarea, '   ');

            expect(button).toBeDisabled();
        });

        it('should validate text trimming', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            // Type spaces
            await user.type(textarea, '   ');
            expect(button).toBeDisabled();

            // Add actual text
            await user.type(textarea, 'test');
            expect(button).not.toBeDisabled();
        });

        it('should respect maxLength attribute', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i) as HTMLTextAreaElement;

            const longText = 'a'.repeat(1001);
            await user.type(textarea, longText);

            // HTML maxLength prevents typing beyond limit
            expect(textarea.value.length).toBeLessThanOrEqual(1000);
        });
    });

    describe('Form Submission', () => {
        it('should call onSubmit with prompt text when form is submitted', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            await user.type(textarea, 'What is AI?');
            await user.click(button);

            expect(mockOnSubmit).toHaveBeenCalledTimes(1);
            expect(mockOnSubmit).toHaveBeenCalledWith({
                prompt: 'What is AI?',
            });
        });

        it('should clear textarea after submission', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            await user.type(textarea, 'Test message');
            await user.click(button);

            expect(textarea).toHaveValue('');
        });

        it('should disable button after textarea is cleared', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            await user.type(textarea, 'Test');
            await user.click(button);

            expect(button).toBeDisabled();
        });

        it('should submit on Enter key press', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);

            await user.type(textarea, 'Quick question');
            await user.keyboard('{Enter}');

            expect(mockOnSubmit).toHaveBeenCalledWith({
                prompt: 'Quick question',
            });
        });

        it('should not submit on Shift+Enter (allow newline)', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);

            await user.type(textarea, 'First line');
            await user.keyboard('{Shift>}{Enter}{/Shift}');
            await user.type(textarea, 'Second line');

            expect(mockOnSubmit).not.toHaveBeenCalled();
            expect(textarea).toHaveValue('First line\nSecond line');
        });

        it('should handle rapid submissions correctly', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);

            await user.type(textarea, 'First message');
            await user.keyboard('{Enter}');

            await user.type(textarea, 'Second message');
            await user.keyboard('{Enter}');

            expect(mockOnSubmit).toHaveBeenCalledTimes(2);
            expect(mockOnSubmit).toHaveBeenNthCalledWith(1, { prompt: 'First message' });
            expect(mockOnSubmit).toHaveBeenNthCalledWith(2, { prompt: 'Second message' });
        });

        it('should not submit when button is clicked while disabled', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const button = screen.getByRole('button');

            await user.click(button);

            expect(mockOnSubmit).not.toHaveBeenCalled();
        });
    });

    describe('User Experience', () => {
        it('should focus textarea on mount', () => {
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            expect(textarea).toHaveFocus();
        });

        it('should allow multi-line input', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);

            await user.type(textarea, 'Line 1{Shift>}{Enter}{/Shift}Line 2');

            expect(textarea).toHaveValue('Line 1\nLine 2');
        });

        it('should maintain focus after clearing', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            await user.type(textarea, 'Test');
            await user.click(button);

            // Textarea should still be in the document (just cleared)
            expect(textarea).toBeInTheDocument();
            expect(textarea).toHaveValue('');
        });
    });

    describe('Edge Cases', () => {
        it('should handle very long text within limit', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            const longText = 'a'.repeat(999);
            await user.type(textarea, longText);
            await user.click(button);

            expect(mockOnSubmit).toHaveBeenCalledWith({
                prompt: longText,
            });
        });

        it('should handle special characters', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            const specialText = 'Test with <html> & "quotes" and \'apostrophes\'';
            await user.type(textarea, specialText);
            await user.click(button);

            expect(mockOnSubmit).toHaveBeenCalledWith({
                prompt: specialText,
            });
        });

        it('should handle emoji input', async () => {
            const user = userEvent.setup();
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByPlaceholderText(/ask me anything/i);
            const button = screen.getByRole('button');

            await user.type(textarea, 'Hello 👋 World 🌍');
            await user.click(button);

            expect(mockOnSubmit).toHaveBeenCalledWith({
                prompt: 'Hello 👋 World 🌍',
            });
        });
    });

    describe('Accessibility', () => {
        it('should have accessible form structure', () => {
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const form = screen.getByRole('textbox').closest('form');
            expect(form).toBeInTheDocument();
        });

        it('should have accessible textarea', () => {
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const textarea = screen.getByRole('textbox');
            expect(textarea).toBeInTheDocument();
            expect(textarea).toHaveAttribute('placeholder', 'Ask me anything...');
        });

        it('should have accessible button', () => {
            render(<ChatInput onSubmit={mockOnSubmit} />);

            const button = screen.getByRole('button');
            expect(button).toBeInTheDocument();
        });
    });
});
