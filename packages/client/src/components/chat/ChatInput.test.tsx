/**
 * Component tests for ChatInput
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import ChatInput from './ChatInput';
import '../../test/setup';

// Import testing library after setup
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('ChatInput', () => {
    const mockOnSubmit = vi.fn();
    const mockOnCancel = vi.fn();
    const user = userEvent.setup();

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Initial State', () => {
        it('should render input field and submit button', () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            expect(getByRole('textbox')).toBeInTheDocument();
            expect(getByRole('button')).toBeInTheDocument();
        });

        it('should disable submit button when input is empty', () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            expect(getByRole('button')).toBeDisabled();
        });

        it('should show cancel button when bot is typing', () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={true} />
            );

            expect(getByRole('button', { name: /cancel/i })).toBeInTheDocument();
        });

        it('should show send button when bot is not typing', () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            expect(getByRole('button', { name: /send/i })).toBeInTheDocument();
        });
    });

    describe('Input Validation', () => {
        it('should enable submit button when user types text', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            const button = getByRole('button');

            await user.type(input, 'Hello world');

            expect(button).toBeEnabled();
        });

        it('should keep submit button disabled for whitespace-only input', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            const button = getByRole('button');

            await user.type(input, '   ');

            expect(button).toBeDisabled();
        });

        it('should keep submit button disabled for whitespace-only input', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            const button = getByRole('button');

            await user.type(input, '   ');

            expect(button).toBeDisabled();
        });
    });

    describe('User Interactions', () => {
        it('should submit message when user clicks send button', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Test message');

            const button = getByRole('button');
            await user.click(button);

            expect(mockOnSubmit).toHaveBeenCalledWith({ prompt: 'Test message' });
        });

        it('should submit message when user presses Enter', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Test message{enter}');

            expect(mockOnSubmit).toHaveBeenCalledWith({ prompt: 'Test message' });
        });

        it('should allow multiline input with Shift+Enter', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Line 1{shift>}{enter}Line 2');

            expect(input).toHaveValue('Line 1\nLine 2');
            expect(mockOnSubmit).not.toHaveBeenCalled();
        });

        it('should submit message when user presses Enter', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Test message{enter}');

            expect(mockOnSubmit).toHaveBeenCalledWith({ prompt: 'Test message' });
        });

        it('should allow multiline input with Shift+Enter', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Line 1{shift>}{enter}Line 2');

            expect(input).toHaveValue('Line 1\nLine 2');
            expect(mockOnSubmit).not.toHaveBeenCalled();
        });

        it('should allow multiline input with Shift+Enter', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Line 1{shift>}{enter}Line 2');

            expect(input).toHaveValue('Line 1\nLine 2');
            expect(mockOnSubmit).not.toHaveBeenCalled();
        });

        it('should clear input after successful submission', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Test message{enter}');

            expect(input).toHaveValue('');
        });

        it('should call cancel function when cancel button is clicked', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={true} />
            );

            const cancelButton = getByRole('button', { name: /cancel/i });
            await user.click(cancelButton);

            expect(mockOnCancel).toHaveBeenCalled();
        });

        it('should handle special characters and emoji', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Hello 🌟 @world! #test');

            expect(input).toHaveValue('Hello 🌟 @world! #test');
        });

        it('should handle long text input', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            const longText = 'A'.repeat(1000);
            await user.type(input, longText);

            expect(input).toHaveValue(longText);
            expect(getByRole('button')).toBeEnabled();
        });

        it('should call cancel function when cancel button is clicked', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={true} />
            );

            const cancelButton = getByRole('button', { name: /cancel/i });
            await user.click(cancelButton);

            expect(mockOnCancel).toHaveBeenCalled();
        });

        it('should handle special characters and emoji', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Hello 🌟 @world! #test');

            expect(input).toHaveValue('Hello 🌟 @world! #test');
        });

        it('should handle long text input', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            const longText = 'A'.repeat(1000);
            await user.type(input, longText);

            expect(input).toHaveValue(longText);
            expect(getByRole('button')).toBeEnabled();
        });

        it('should call cancel function when cancel button is clicked', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={true} />
            );

            const cancelButton = getByRole('button', { name: /cancel/i });
            await user.click(cancelButton);

            expect(mockOnCancel).toHaveBeenCalled();
        });

        it('should handle special characters and emoji', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Hello 🌟 @world! #test');

            expect(input).toHaveValue('Hello 🌟 @world! #test');
        });

        it('should handle long text input', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            const longText = 'A'.repeat(1000);
            await user.type(input, longText);

            expect(input).toHaveValue(longText);
            expect(getByRole('button')).toBeEnabled();
        });
    });

    describe('Input Handling', () => {
        it('should handle special characters and emoji', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            await user.type(input, 'Hello 🌟 @world! #test');

            expect(input).toHaveValue('Hello 🌟 @world! #test');
        });

        it('should handle long text input', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            const longText = 'A'.repeat(1000);
            await user.type(input, longText);

            expect(input).toHaveValue(longText);
            expect(getByRole('button')).toBeEnabled();
        });

        it('should handle long text input', async () => {
            const { getByRole } = render(
                <ChatInput onSubmit={mockOnSubmit} onCancel={mockOnCancel} isTyping={false} />
            );

            const input = getByRole('textbox');
            const longText = 'A'.repeat(1000);
            await user.type(input, longText);

            expect(input).toHaveValue(longText);
            expect(getByRole('button')).toBeEnabled();
        });
    });
});
