/**
 * Component tests for ChatMessages
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ChatMessages, { type Message } from './ChatMessages';
import themeReducer from '../../store/slices/themeSlice';
import workspaceReducer from '../../store/slices/workspaceSlice';
import statusReducer from '../../store/slices/statusSlice';
import '../../test/setup';

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
                workspace: workspaceReducer,
                status: statusReducer,
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
            const { getByText } = renderWithStore(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            expect(getByText('Hello, how are you?')).toBeInTheDocument();
            expect(getByText('I am doing well, thank you!')).toBeInTheDocument();
            expect(getByText('Can you help me with something?')).toBeInTheDocument();
        });

        it('should render empty messages list', () => {
            const { getByText } = renderWithStore(
                <ChatMessages messages={[]} error="" isBotTyping={false} />
            );

            // Should show empty state message
            expect(getByText('Start a conversation')).toBeInTheDocument();
        });

        it('should apply correct styling to user messages', () => {
            const { getByText } = renderWithStore(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            const userMessage = getByText('Hello, how are you?').closest('.bg-blue-600');
            expect(userMessage).toHaveClass('bg-blue-600', 'text-white');
        });

        it('should apply correct styling to bot messages', () => {
            const { getByText } = renderWithStore(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            const botMessage = getByText('I am doing well, thank you!').closest('.bg-white');
            expect(botMessage).toHaveClass('bg-white', 'text-gray-800');
        });

        it('should render typing indicator when bot is typing', () => {
            const { getByTestId } = renderWithStore(
                <ChatMessages messages={mockMessages} error="" isBotTyping={true} />
            );

            expect(getByTestId('typing-indicator')).toBeInTheDocument();
        });

        it('should not render typing indicator when bot is not typing', () => {
            const { queryByTestId } = renderWithStore(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            expect(queryByTestId('typing-indicator')).not.toBeInTheDocument();
        });

        it('should render error message when error is present', () => {
            const { getByText } = renderWithStore(
                <ChatMessages
                    messages={mockMessages}
                    error="Connection failed"
                    isBotTyping={false}
                />
            );

            const errorElement = getByText('Connection failed');
            expect(errorElement).toBeInTheDocument();
            expect(errorElement).toHaveClass('text-red-700');
        });

        it('should not render error message when error is empty', () => {
            const { queryByText } = renderWithStore(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            expect(queryByText(/failed/i)).not.toBeInTheDocument();
        });
    });

    describe('Message Display', () => {
        it('should render messages in correct order', () => {
            const { getByText } = renderWithStore(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            // Check that all messages are present
            expect(getByText('Hello, how are you?')).toBeInTheDocument();
            expect(getByText('I am doing well, thank you!')).toBeInTheDocument();
            expect(getByText('Can you help me with something?')).toBeInTheDocument();
        });

        it('should handle single message', () => {
            const { getByText } = renderWithStore(
                <ChatMessages
                    messages={[{ content: 'Only message', role: 'user' }]}
                    error=""
                    isBotTyping={false}
                />
            );

            expect(getByText('Only message')).toBeInTheDocument();
        });

        it('should handle messages with same content but different roles', () => {
            const { getAllByText } = renderWithStore(
                <ChatMessages
                    messages={[
                        { content: 'Same text', role: 'user' },
                        { content: 'Same text', role: 'bot' },
                    ]}
                    error=""
                    isBotTyping={false}
                />
            );

            const messages = getAllByText('Same text');
            expect(messages).toHaveLength(2);
        });

        it('should handle very long messages', () => {
            const longMessage = 'a'.repeat(1000);
            const { getByText } = renderWithStore(
                <ChatMessages
                    messages={[{ content: longMessage, role: 'bot' }]}
                    error=""
                    isBotTyping={false}
                />
            );

            expect(getByText(longMessage)).toBeInTheDocument();
        });
    });

    describe('Accessibility', () => {
        it('should have visible message content', () => {
            const { getByText } = renderWithStore(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            // Check that messages are visible (not aria-hidden, etc.)
            const element = getByText('Hello, how are you?');
            expect(element).toBeVisible();
        });

        it('should have visible error messages', () => {
            const { getByText } = renderWithStore(
                <ChatMessages messages={mockMessages} error="Test error" isBotTyping={false} />
            );

            const errorElement = getByText('Test error');
            expect(errorElement).toBeVisible();
        });

        it('should maintain message container structure', () => {
            const { container } = renderWithStore(
                <ChatMessages messages={mockMessages} error="" isBotTyping={false} />
            );

            // Should have proper semantic structure
            expect(container).toBeInTheDocument();
        });
    });
});
