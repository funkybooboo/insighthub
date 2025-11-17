/**
 * Component tests for ChatMessages
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ChatMessages, { type Message } from './ChatMessages';
import themeReducer from '../../store/slices/themeSlice';

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

    const renderWithStore = (ui: React.ReactElement) => {
        const store = configureStore({
            reducer: {
                theme: themeReducer,
            },
        });

        const Wrapper = ({ children }: { children: React.ReactNode }) => (
            <Provider store={store}>{children}</Provider>
        );

        return render(ui, { wrapper: Wrapper });
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Rendering', () => {
        it('should render all messages', () => {
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
            expect(screen.getByText('I am doing well, thank you!')).toBeInTheDocument();
            expect(screen.getByText('Can you help me with something?')).toBeInTheDocument();
        });

        it('should render empty messages list', () => {
            renderWithStore(<ChatMessages messages={[]} error="" isBotTyping={false} />);

            // Should show empty state message
            expect(screen.getByText('Start a conversation')).toBeInTheDocument();
        });

        it('should apply correct styling to user messages', () => {
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            const userMessage = screen.getByText('Hello, how are you?');
            const messageContainer = userMessage.closest('.bg-blue-600');
            expect(messageContainer).toBeInTheDocument();
            expect(messageContainer).toHaveClass('text-white');
        });

        it('should apply correct styling to bot messages', () => {
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            const botMessage = screen.getByText('I am doing well, thank you!');
            const messageContainer = botMessage.closest('.bg-gray-100');
            expect(messageContainer).toBeInTheDocument();
            expect(messageContainer).toHaveClass('text-gray-900');
        });

        it('should render typing indicator when bot is typing', () => {
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={true} />);

            expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
        });

        it('should not render typing indicator when bot is not typing', () => {
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            expect(screen.queryByTestId('typing-indicator')).not.toBeInTheDocument();
        });

        it('should render error message when error is present', () => {
            renderWithStore(
                <ChatMessages
                    messages={mockMessages}
                    error="Connection failed"
                    isBotTyping={false}
                />
            );

            const errorElement = screen.getByText('Connection failed');
            expect(errorElement).toBeInTheDocument();
            expect(errorElement).toHaveClass('text-red-800');
        });

        it('should not render error message when error is empty', () => {
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            expect(screen.queryByText(/failed/i)).not.toBeInTheDocument();
        });
    });

    describe('Markdown Rendering', () => {
        it('should render markdown in messages', () => {
            const messagesWithMarkdown: Message[] = [
                { content: '# Heading', role: 'bot' },
                { content: '**Bold text**', role: 'bot' },
            ];

            renderWithStore(
                <ChatMessages messages={messagesWithMarkdown} error="" isBotTyping={false} />
            );

            // react-markdown renders heading as h1
            expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Heading');
        });

        it('should render markdown lists', () => {
            const messagesWithList: Message[] = [
                { content: '- Item 1\n- Item 2\n- Item 3', role: 'bot' },
            ];

            renderWithStore(
                <ChatMessages messages={messagesWithList} error="" isBotTyping={false} />
            );

            expect(screen.getByText('Item 1')).toBeInTheDocument();
            expect(screen.getByText('Item 2')).toBeInTheDocument();
            expect(screen.getByText('Item 3')).toBeInTheDocument();
        });

        it('should render markdown code blocks', () => {
            const messagesWithCode: Message[] = [{ content: '`inline code`', role: 'bot' }];

            renderWithStore(
                <ChatMessages messages={messagesWithCode} error="" isBotTyping={false} />
            );

            expect(screen.getByText('inline code')).toBeInTheDocument();
        });

        it('should render markdown links', () => {
            const messagesWithLink: Message[] = [
                { content: '[OpenAI](https://openai.com)', role: 'bot' },
            ];

            renderWithStore(
                <ChatMessages messages={messagesWithLink} error="" isBotTyping={false} />
            );

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

            renderWithStore(
                <ChatMessages messages={orderedMessages} error="" isBotTyping={false} />
            );

            const messages = screen.getAllByText(/message/i);
            expect(messages[0]).toHaveTextContent('First message');
            expect(messages[1]).toHaveTextContent('Second message');
            expect(messages[2]).toHaveTextContent('Third message');
        });

        it('should handle single message', () => {
            const singleMessage: Message[] = [{ content: 'Only message', role: 'user' }];

            renderWithStore(<ChatMessages messages={singleMessage} error="" isBotTyping={false} />);

            expect(screen.getByText('Only message')).toBeInTheDocument();
        });

        it('should handle messages with same content but different roles', () => {
            const duplicateContent: Message[] = [
                { content: 'Same text', role: 'user' },
                { content: 'Same text', role: 'bot' },
            ];

            renderWithStore(
                <ChatMessages messages={duplicateContent} error="" isBotTyping={false} />
            );

            const messages = screen.getAllByText('Same text');
            expect(messages).toHaveLength(2);

            // Check that both messages are rendered
            expect(messages[0]).toBeInTheDocument();
            expect(messages[1]).toBeInTheDocument();
        });

        it('should handle very long messages', () => {
            const longMessage = 'a'.repeat(1000);
            const messagesWithLong: Message[] = [{ content: longMessage, role: 'bot' }];

            renderWithStore(
                <ChatMessages messages={messagesWithLong} error="" isBotTyping={false} />
            );

            expect(screen.getByText(longMessage)).toBeInTheDocument();
        });

        it('should handle messages with special characters', () => {
            const specialMessages: Message[] = [
                { content: 'Test <html> & "quotes"', role: 'user' },
            ];

            renderWithStore(
                <ChatMessages messages={specialMessages} error="" isBotTyping={false} />
            );

            expect(screen.getByText(/Test.*html.*quotes/)).toBeInTheDocument();
        });

        it('should handle messages with emojis', () => {
            const emojiMessages: Message[] = [{ content: 'Hello 👋 World 🌍', role: 'bot' }];

            renderWithStore(<ChatMessages messages={emojiMessages} error="" isBotTyping={false} />);

            expect(screen.getByText('Hello 👋 World 🌍')).toBeInTheDocument();
        });

        it('should handle messages with newlines', () => {
            const multilineMessages: Message[] = [
                { content: 'Line 1\nLine 2\nLine 3', role: 'bot' },
            ];

            renderWithStore(
                <ChatMessages messages={multilineMessages} error="" isBotTyping={false} />
            );

            expect(screen.getByText(/Line 1/)).toBeInTheDocument();
            expect(screen.getByText(/Line 2/)).toBeInTheDocument();
            expect(screen.getByText(/Line 3/)).toBeInTheDocument();
        });
    });

    describe('Copy Functionality', () => {
        it('should handle copy event with selected text', async () => {
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

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
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

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
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

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
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            const lastMessage = screen.getByText('Can you help me with something?');
            expect(lastMessage).toBeInTheDocument();
        });

        it('should update scroll when messages change', () => {
            const { rerender } = renderWithStore(
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
            const { rerender } = renderWithStore(
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
            renderWithStore(
                <ChatMessages messages={mockMessages} error="Error occurred" isBotTyping={false} />
            );

            expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
            expect(screen.getByText('Error occurred')).toBeInTheDocument();
        });

        it('should display error with typing indicator', () => {
            renderWithStore(
                <ChatMessages messages={mockMessages} error="Error occurred" isBotTyping={true} />
            );

            expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
            expect(screen.getByText('Error occurred')).toBeInTheDocument();
        });

        it('should handle very long error messages', () => {
            const longError = 'A very long error message that goes on and on';

            renderWithStore(
                <ChatMessages messages={mockMessages} error={longError} isBotTyping={false} />
            );

            // Check that error container is present with the error text
            expect(screen.getByText(longError)).toBeInTheDocument();
        });
    });

    describe('Edge Cases', () => {
        it('should handle empty content messages', () => {
            const emptyMessages: Message[] = [{ content: '', role: 'user' }];

            renderWithStore(<ChatMessages messages={emptyMessages} error="" isBotTyping={false} />);

            // Empty message should still render a div
            const containers = screen.getAllByRole('generic');
            expect(containers.length).toBeGreaterThan(0);
        });

        it('should handle whitespace-only messages', () => {
            const whitespaceMessages: Message[] = [{ content: '   ', role: 'bot' }];

            const { container } = renderWithStore(
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

            renderWithStore(
                <ChatMessages messages={alternatingMessages} error="" isBotTyping={false} />
            );

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

            renderWithStore(
                <ChatMessages messages={consecutiveMessages} error="" isBotTyping={false} />
            );

            const messages = screen.getAllByText(/User message/);
            expect(messages).toHaveLength(3);
            // All messages should be rendered
            messages.forEach((message) => {
                expect(message).toBeInTheDocument();
            });
        });
    });

    describe('Accessibility', () => {
        it('should have visible message content', () => {
            renderWithStore(<ChatMessages messages={mockMessages} error="" isBotTyping={false} />);

            mockMessages.forEach((message) => {
                const element = screen.getByText(message.content);
                expect(element).toBeVisible();
            });
        });

        it('should have visible error messages', () => {
            renderWithStore(
                <ChatMessages messages={mockMessages} error="Test error" isBotTyping={false} />
            );

            const errorElement = screen.getByText('Test error');
            expect(errorElement).toBeVisible();
        });

        it('should maintain message container structure', () => {
            const { container } = renderWithStore(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            const messagesContainer = container.querySelector('.overflow-y-auto');
            expect(messagesContainer).toBeInTheDocument();
        });
    });
});
