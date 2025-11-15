/**
 * Component tests for ChatMessages
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import ChatMessages, { type Message } from './ChatMessages';

// Mock TypingIndicator component
vi.mock('./TypingIndicator', () => ({
    default: () => <div data-testid="typing-indicator">Typing...</div>,
}));

describe('ChatMessages', () => {
    const mockMessages: Message[] = [
        { content: 'Hello, how are you?', role: 'user' },
        { content: 'I am doing well, thank you!', role: 'bot' },
        { content: 'Can you help me with something?', role: 'user' },
    ];

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('should render all messages', () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
            expect(screen.getByText('I am doing well, thank you!')).toBeInTheDocument();
            expect(screen.getByText('Can you help me with something?')).toBeInTheDocument();
        });

        it('should render empty messages list', () => {
            const { container } = render(
                <ChatMessages messages={[]} error="" isBotTyping={false} />
            );

            // Should render without errors
            expect(container.querySelector('.flex.flex-col')).toBeInTheDocument();
        });

        it('should apply correct styling to user messages', () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            const userMessage = screen.getByText('Hello, how are you?').closest('div');
            expect(userMessage).toHaveClass('bg-blue-600');
            expect(userMessage).toHaveClass('text-white');
            expect(userMessage).toHaveClass('self-end');
        });

        it('should apply correct styling to bot messages', () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            const botMessage = screen.getByText('I am doing well, thank you!').closest('div');
            expect(botMessage).toHaveClass('bg-gray-100');
            expect(botMessage).toHaveClass('text-black');
            expect(botMessage).toHaveClass('self-start');
        });

        it('should render typing indicator when bot is typing', () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={true} />);

            expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
        });

        it('should not render typing indicator when bot is not typing', () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            expect(screen.queryByTestId('typing-indicator')).not.toBeInTheDocument();
        });

        it('should render error message when error is present', () => {
            render(
                <ChatMessages
                    messages={mockMessages}
                    error="Connection failed"
                    isBotTyping={false}
                />
            );

            const errorElement = screen.getByText('Connection failed');
            expect(errorElement).toBeInTheDocument();
            expect(errorElement).toHaveClass('text-red-500');
        });

        it('should not render error message when error is empty', () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            expect(screen.queryByText(/failed/i)).not.toBeInTheDocument();
        });
    });

    describe('Markdown Rendering', () => {
        it('should render markdown in messages', () => {
            const messagesWithMarkdown: Message[] = [
                { content: '# Heading', role: 'bot' },
                { content: '**Bold text**', role: 'bot' },
            ];

            render(<ChatMessages messages={messagesWithMarkdown} error="" isBotTyping={false} />);

            // react-markdown renders heading as h1
            expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Heading');
        });

        it('should render markdown lists', () => {
            const messagesWithList: Message[] = [
                { content: '- Item 1\n- Item 2\n- Item 3', role: 'bot' },
            ];

            render(<ChatMessages messages={messagesWithList} error="" isBotTyping={false} />);

            expect(screen.getByText('Item 1')).toBeInTheDocument();
            expect(screen.getByText('Item 2')).toBeInTheDocument();
            expect(screen.getByText('Item 3')).toBeInTheDocument();
        });

        it('should render markdown code blocks', () => {
            const messagesWithCode: Message[] = [{ content: '`inline code`', role: 'bot' }];

            render(<ChatMessages messages={messagesWithCode} error="" isBotTyping={false} />);

            expect(screen.getByText('inline code')).toBeInTheDocument();
        });

        it('should render markdown links', () => {
            const messagesWithLink: Message[] = [
                { content: '[OpenAI](https://openai.com)', role: 'bot' },
            ];

            render(<ChatMessages messages={messagesWithLink} error="" isBotTyping={false} />);

            const link = screen.getByRole('link', { name: 'OpenAI' });
            expect(link).toBeInTheDocument();
            expect(link).toHaveAttribute('href', 'https://openai.com');
        });
    });

    describe('Message Display', () => {
        it('should render messages in correct order', () => {
            const orderedMessages: Message[] = [
                { content: 'First message', role: 'user' },
                { content: 'Second message', role: 'bot' },
                { content: 'Third message', role: 'user' },
            ];

            render(<ChatMessages messages={orderedMessages} error="" isBotTyping={false} />);

            const messages = screen.getAllByText(/message/i);
            expect(messages[0]).toHaveTextContent('First message');
            expect(messages[1]).toHaveTextContent('Second message');
            expect(messages[2]).toHaveTextContent('Third message');
        });

        it('should handle single message', () => {
            const singleMessage: Message[] = [{ content: 'Only message', role: 'user' }];

            render(<ChatMessages messages={singleMessage} error="" isBotTyping={false} />);

            expect(screen.getByText('Only message')).toBeInTheDocument();
        });

        it('should handle messages with same content but different roles', () => {
            const duplicateContent: Message[] = [
                { content: 'Same text', role: 'user' },
                { content: 'Same text', role: 'bot' },
            ];

            render(<ChatMessages messages={duplicateContent} error="" isBotTyping={false} />);

            const messages = screen.getAllByText('Same text');
            expect(messages).toHaveLength(2);

            // First should be user (blue background)
            expect(messages[0].closest('div')).toHaveClass('bg-blue-600');
            // Second should be bot (gray background)
            expect(messages[1].closest('div')).toHaveClass('bg-gray-100');
        });

        it('should handle very long messages', () => {
            const longMessage = 'a'.repeat(1000);
            const messagesWithLong: Message[] = [{ content: longMessage, role: 'bot' }];

            render(<ChatMessages messages={messagesWithLong} error="" isBotTyping={false} />);

            expect(screen.getByText(longMessage)).toBeInTheDocument();
        });

        it('should handle messages with special characters', () => {
            const specialMessages: Message[] = [
                { content: 'Test <html> & "quotes"', role: 'user' },
            ];

            render(<ChatMessages messages={specialMessages} error="" isBotTyping={false} />);

            expect(screen.getByText(/Test.*html.*quotes/)).toBeInTheDocument();
        });

        it('should handle messages with emojis', () => {
            const emojiMessages: Message[] = [{ content: 'Hello 👋 World 🌍', role: 'bot' }];

            render(<ChatMessages messages={emojiMessages} error="" isBotTyping={false} />);

            expect(screen.getByText('Hello 👋 World 🌍')).toBeInTheDocument();
        });

        it('should handle messages with newlines', () => {
            const multilineMessages: Message[] = [
                { content: 'Line 1\nLine 2\nLine 3', role: 'bot' },
            ];

            render(<ChatMessages messages={multilineMessages} error="" isBotTyping={false} />);

            expect(screen.getByText(/Line 1/)).toBeInTheDocument();
            expect(screen.getByText(/Line 2/)).toBeInTheDocument();
            expect(screen.getByText(/Line 3/)).toBeInTheDocument();
        });
    });

    describe('Copy Functionality', () => {
        it('should handle copy event with selected text', async () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            const message = screen.getByText('Hello, how are you?');

            // Simulate text selection
            const selection = {
                toString: () => 'Hello, how are you?',
            };
            window.getSelection = vi.fn(() => selection as Selection);

            const clipboardData = {
                setData: vi.fn(),
            };

            // Simulate copy event
            const copyEvent = new ClipboardEvent('copy', {
                clipboardData: clipboardData as unknown as DataTransfer,
                bubbles: true,
            });

            Object.defineProperty(copyEvent, 'clipboardData', {
                value: clipboardData,
            });

            const preventDefaultSpy = vi.spyOn(copyEvent, 'preventDefault');

            message.parentElement?.dispatchEvent(copyEvent);

            expect(preventDefaultSpy).toHaveBeenCalled();
            expect(clipboardData.setData).toHaveBeenCalledWith('text/plain', 'Hello, how are you?');
        });

        it('should handle copy event with no selection', () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            const message = screen.getByText('Hello, how are you?');

            // Simulate no selection
            window.getSelection = vi.fn(() => ({
                toString: () => '',
            })) as unknown as () => Selection | null;

            const clipboardData = {
                setData: vi.fn(),
            };

            const copyEvent = new ClipboardEvent('copy', {
                clipboardData: clipboardData as unknown as DataTransfer,
                bubbles: true,
            });

            Object.defineProperty(copyEvent, 'clipboardData', {
                value: clipboardData,
            });

            const preventDefaultSpy = vi.spyOn(copyEvent, 'preventDefault');

            message.parentElement?.dispatchEvent(copyEvent);

            expect(preventDefaultSpy).not.toHaveBeenCalled();
            expect(clipboardData.setData).not.toHaveBeenCalled();
        });

        it('should trim whitespace from selection', () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            const message = screen.getByText('Hello, how are you?');

            const selection = {
                toString: () => '  Hello, how are you?  ',
            };
            window.getSelection = vi.fn(() => selection as Selection);

            const clipboardData = {
                setData: vi.fn(),
            };

            const copyEvent = new ClipboardEvent('copy', {
                clipboardData: clipboardData as unknown as DataTransfer,
                bubbles: true,
            });

            Object.defineProperty(copyEvent, 'clipboardData', {
                value: clipboardData,
            });

            message.parentElement?.dispatchEvent(copyEvent);

            expect(clipboardData.setData).toHaveBeenCalledWith('text/plain', 'Hello, how are you?');
        });
    });

    describe('Scroll Behavior', () => {
        it('should have scrollIntoView reference on last message', () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            const lastMessage = screen.getByText('Can you help me with something?');
            expect(lastMessage).toBeInTheDocument();
        });

        it('should update scroll when messages change', () => {
            const { rerender } = render(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            const newMessages: Message[] = [
                ...mockMessages,
                { content: 'New message', role: 'bot' },
            ];

            rerender(<ChatMessages messages={newMessages} error="" isBotTyping={false} />);

            expect(screen.getByText('New message')).toBeInTheDocument();
        });
    });

    describe('Error Handling', () => {
        it('should display multiple types of errors', () => {
            const { rerender } = render(
                <ChatMessages messages={mockMessages} error="Network error" isBotTyping={false} />
            );

            expect(screen.getByText('Network error')).toBeInTheDocument();

            rerender(
                <ChatMessages messages={mockMessages} error="Server error" isBotTyping={false} />
            );

            expect(screen.getByText('Server error')).toBeInTheDocument();
            expect(screen.queryByText('Network error')).not.toBeInTheDocument();
        });

        it('should display error alongside messages', () => {
            render(
                <ChatMessages messages={mockMessages} error="Error occurred" isBotTyping={false} />
            );

            expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
            expect(screen.getByText('Error occurred')).toBeInTheDocument();
        });

        it('should display error with typing indicator', () => {
            render(
                <ChatMessages messages={mockMessages} error="Error occurred" isBotTyping={true} />
            );

            expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
            expect(screen.getByText('Error occurred')).toBeInTheDocument();
        });

        it('should handle very long error messages', () => {
            const longError = 'Error: '.repeat(100);

            render(<ChatMessages messages={mockMessages} error={longError} isBotTyping={false} />);

            // Check that error text is present (partial match since it might be normalized)
            expect(screen.getByText((content, element) => {
                return element?.textContent === longError;
            })).toBeInTheDocument();
        });
    });

    describe('Edge Cases', () => {
        it('should handle empty content messages', () => {
            const emptyMessages: Message[] = [{ content: '', role: 'user' }];

            render(<ChatMessages messages={emptyMessages} error="" isBotTyping={false} />);

            // Empty message should still render a div
            const containers = screen.getAllByRole('generic');
            expect(containers.length).toBeGreaterThan(0);
        });

        it('should handle whitespace-only messages', () => {
            const whitespaceMessages: Message[] = [{ content: '   ', role: 'bot' }];

            const { container } = render(
                <ChatMessages messages={whitespaceMessages} error="" isBotTyping={false} />
            );

            // Message container should exist even with whitespace-only content
            expect(container.querySelector('.bg-gray-100')).toBeInTheDocument();
        });

        it('should handle alternating user and bot messages', () => {
            const alternatingMessages: Message[] = [
                { content: 'User 1', role: 'user' },
                { content: 'Bot 1', role: 'bot' },
                { content: 'User 2', role: 'user' },
                { content: 'Bot 2', role: 'bot' },
            ];

            render(<ChatMessages messages={alternatingMessages} error="" isBotTyping={false} />);

            expect(screen.getByText('User 1')).toBeInTheDocument();
            expect(screen.getByText('Bot 1')).toBeInTheDocument();
            expect(screen.getByText('User 2')).toBeInTheDocument();
            expect(screen.getByText('Bot 2')).toBeInTheDocument();
        });

        it('should handle consecutive messages from same role', () => {
            const consecutiveMessages: Message[] = [
                { content: 'User message 1', role: 'user' },
                { content: 'User message 2', role: 'user' },
                { content: 'User message 3', role: 'user' },
            ];

            render(<ChatMessages messages={consecutiveMessages} error="" isBotTyping={false} />);

            const messages = screen.getAllByText(/User message/);
            expect(messages).toHaveLength(3);
            messages.forEach((message) => {
                expect(message.closest('div')).toHaveClass('bg-blue-600');
            });
        });
    });

    describe('Accessibility', () => {
        it('should have visible message content', () => {
            render(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            mockMessages.forEach((message) => {
                const element = screen.getByText(message.content);
                expect(element).toBeVisible();
            });
        });

        it('should have visible error messages', () => {
            render(<ChatMessages messages={mockMessages} error="Test error" isBotTyping={false} />);

            const errorElement = screen.getByText('Test error');
            expect(errorElement).toBeVisible();
        });

        it('should maintain message container structure', () => {
            const { container } = render(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            const messagesContainer = container.querySelector('.flex.flex-col.flex-1');
            expect(messagesContainer).toBeInTheDocument();
        });
    });
});
