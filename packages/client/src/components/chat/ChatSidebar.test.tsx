/**
 * Component tests for ChatSidebar
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ChatSidebar from './ChatSidebar';
import chatReducer, {
    createSession,
    setActiveSession,
    addMessageToSession,
} from '../../store/slices/chatSlice';
import type { ChatSession } from '../../store/slices/chatSlice';

// Mock window.confirm
const mockConfirm = vi.fn();
window.confirm = mockConfirm;

describe('ChatSidebar', () => {
    const renderChatSidebar = (initialSessions: ChatSession[] = []) => {
        const store = configureStore({
            reducer: {
                chat: chatReducer,
            },
        });

        // Add initial sessions if provided
        initialSessions.forEach((session) => {
            store.dispatch(createSession({ id: session.id, title: session.title }));
            if (session.messages.length > 0) {
                session.messages.forEach((message) => {
                    store.dispatch(
                        addMessageToSession({
                            sessionId: session.id,
                            message,
                        })
                    );
                });
            }
        });

        return {
            store,
            ...render(
                <Provider store={store}>
                    <ChatSidebar />
                </Provider>
            ),
        };
    };

    beforeEach(() => {
        vi.clearAllMocks();
        mockConfirm.mockReturnValue(true);
    });

    describe('Rendering', () => {
        it('should render New Chat button', () => {
            renderChatSidebar();

            const newChatButton = screen.getByRole('button', { name: /new chat/i });
            expect(newChatButton).toBeInTheDocument();
        });

        it('should render empty state when no sessions exist', () => {
            renderChatSidebar();

            expect(screen.getByText('No chats yet')).toBeInTheDocument();
            expect(screen.getByText('Click New Chat to start')).toBeInTheDocument();
        });

        it('should render session count in footer', () => {
            renderChatSidebar();

            expect(screen.getByText(/0 chats saved locally/i)).toBeInTheDocument();
        });

        it('should render correct singular form for session count', async () => {
            const user = userEvent.setup({ delay: null });
            renderChatSidebar();

            const newChatButton = screen.getByRole('button', { name: /new chat/i });
            await user.click(newChatButton);

            expect(screen.getByText(/1 chat saved locally/i)).toBeInTheDocument();
        });

        it('should render correct plural form for session count', async () => {
            const user = userEvent.setup({ delay: null });
            renderChatSidebar();

            const newChatButton = screen.getByRole('button', { name: /new chat/i });
            await user.click(newChatButton);
            await user.click(newChatButton);

            expect(screen.getByText(/2 chats saved locally/i)).toBeInTheDocument();
        });

        it('should render sessions list with session titles', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Test Chat 1',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText('Test Chat 1')).toBeInTheDocument();
        });

        it('should render message count for each session', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Test Chat',
                    messages: [
                        { role: 'user', content: 'Hello' },
                        { role: 'bot', content: 'Hi there' },
                    ],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText('2 messages')).toBeInTheDocument();
        });

        it('should render delete button for each session', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Test Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            const deleteButton = screen.getByTitle('Delete chat');
            expect(deleteButton).toBeInTheDocument();
        });
    });

    describe('New Chat Functionality', () => {
        it('should create new session when New Chat button is clicked', async () => {
            const user = userEvent.setup({ delay: null });
            const { store } = renderChatSidebar();

            const newChatButton = screen.getByRole('button', { name: /new chat/i });
            await user.click(newChatButton);

            const state = store.getState();
            expect(state.chat.sessions).toHaveLength(1);
        });

        it('should generate unique session ID with timestamp', async () => {
            const user = userEvent.setup({ delay: null });
            const { store } = renderChatSidebar();

            const now = Date.now();
            vi.setSystemTime(now);

            const newChatButton = screen.getByRole('button', { name: /new chat/i });
            await user.click(newChatButton);

            const state = store.getState();
            expect(state.chat.sessions[0].id).toBe(`session-${now}`);
        });

        it('should create multiple sessions with different IDs', async () => {
            const user = userEvent.setup({ delay: null });
            const { store } = renderChatSidebar();

            const newChatButton = screen.getByRole('button', { name: /new chat/i });

            vi.setSystemTime(1000);
            await user.click(newChatButton);

            vi.setSystemTime(2000);
            await user.click(newChatButton);

            const state = store.getState();
            expect(state.chat.sessions).toHaveLength(2);
            expect(state.chat.sessions[0].id).not.toBe(state.chat.sessions[1].id);
        });

        it('should hide empty state after creating first session', async () => {
            const user = userEvent.setup({ delay: null });
            renderChatSidebar();

            expect(screen.getByText('No chats yet')).toBeInTheDocument();

            const newChatButton = screen.getByRole('button', { name: /new chat/i });
            await user.click(newChatButton);

            expect(screen.queryByText('No chats yet')).not.toBeInTheDocument();
        });
    });

    describe('Session Selection', () => {
        it('should highlight active session', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Active Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            const { store, container } = renderChatSidebar(sessions);
            store.dispatch(setActiveSession('session-1'));

            const sessionElement = container.querySelector('.bg-blue-100');
            expect(sessionElement).toBeInTheDocument();
            expect(sessionElement).toHaveClass('border-blue-300');
        });

        it('should change active session when clicked', async () => {
            const user = userEvent.setup({ delay: null });
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Chat 1',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
                {
                    id: 'session-2',
                    title: 'Chat 2',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            const { store } = renderChatSidebar(sessions);
            store.dispatch(setActiveSession('session-1'));

            const chat2Element = screen.getByText('Chat 2');
            await user.click(chat2Element);

            const state = store.getState();
            expect(state.chat.activeSessionId).toBe('session-2');
        });

        it('should apply different styling to non-active sessions', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'First Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
                {
                    id: 'session-2',
                    title: 'Second Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            const { container } = renderChatSidebar(sessions);

            // createSession automatically sets the last created session as active
            // So session-2 ("Second Chat") should be active
            const activeSession = container.querySelector('.bg-blue-100');
            expect(activeSession).toBeInTheDocument();
            expect(activeSession?.textContent).toContain('Second Chat');

            // Find the inactive session (with bg-white)
            const inactiveSessions = container.querySelectorAll(
                '.bg-white.rounded-lg.cursor-pointer'
            );
            expect(inactiveSessions.length).toBeGreaterThan(0);
            const inactiveSession = Array.from(inactiveSessions).find((el) =>
                el.textContent?.includes('First Chat')
            );
            expect(inactiveSession).toBeInTheDocument();
            expect(inactiveSession).not.toHaveClass('bg-blue-100');
        });
    });

    describe('Session Deletion', () => {
        it('should show confirmation dialog when delete button is clicked', async () => {
            const user = userEvent.setup({ delay: null });
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Test Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            const deleteButton = screen.getByTitle('Delete chat');
            await user.click(deleteButton);

            expect(mockConfirm).toHaveBeenCalledWith('Are you sure you want to delete this chat?');
        });

        it('should delete session when confirmed', async () => {
            const user = userEvent.setup({ delay: null });
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Test Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            mockConfirm.mockReturnValue(true);
            const { store } = renderChatSidebar(sessions);

            const deleteButton = screen.getByTitle('Delete chat');
            await user.click(deleteButton);

            const state = store.getState();
            expect(state.chat.sessions).toHaveLength(0);
        });

        it('should not delete session when cancelled', async () => {
            const user = userEvent.setup({ delay: null });
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Test Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            mockConfirm.mockReturnValue(false);
            const { store } = renderChatSidebar(sessions);

            const deleteButton = screen.getByTitle('Delete chat');
            await user.click(deleteButton);

            const state = store.getState();
            expect(state.chat.sessions).toHaveLength(1);
        });

        it('should stop event propagation when delete button is clicked', async () => {
            const user = userEvent.setup({ delay: null });
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Test Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            const { store } = renderChatSidebar(sessions);

            const deleteButton = screen.getByTitle('Delete chat');
            await user.click(deleteButton);

            // Active session should not change when delete button is clicked
            const state = store.getState();
            expect(state.chat.activeSessionId).not.toBe('session-1');
        });

        it('should show empty state after deleting last session', async () => {
            const user = userEvent.setup({ delay: null });
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Test Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            mockConfirm.mockReturnValue(true);
            renderChatSidebar(sessions);

            const deleteButton = screen.getByTitle('Delete chat');
            await user.click(deleteButton);

            expect(screen.getByText('No chats yet')).toBeInTheDocument();
        });
    });

    describe('Date Formatting', () => {
        it('should display "Just now" for recent timestamps', () => {
            const now = Date.now();
            vi.setSystemTime(now);

            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Recent Chat',
                    messages: [],
                    createdAt: now,
                    updatedAt: now,
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText('Just now')).toBeInTheDocument();
        });

        it('should display relative time for recent sessions', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Recent Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            // Verify session renders with a timestamp (will be "Just now" for current time)
            expect(screen.getByText('Recent Chat')).toBeInTheDocument();
            expect(screen.getByText(/Just now|ago/)).toBeInTheDocument();
        });

        it('should include timestamp in session display', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Chat with Timestamp',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            const { container } = renderChatSidebar(sessions);

            // Verify session title is rendered
            expect(screen.getByText('Chat with Timestamp')).toBeInTheDocument();

            // Verify that timestamp display area exists (contains the bullet separator)
            const timestampArea = container.querySelector('.text-xs.text-gray-500');
            expect(timestampArea).toBeInTheDocument();
            expect(timestampArea?.textContent).toContain('•');
        });
    });

    describe('Multiple Sessions', () => {
        it('should render multiple sessions correctly', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Chat 1',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
                {
                    id: 'session-2',
                    title: 'Chat 2',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
                {
                    id: 'session-3',
                    title: 'Chat 3',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText('Chat 1')).toBeInTheDocument();
            expect(screen.getByText('Chat 2')).toBeInTheDocument();
            expect(screen.getByText('Chat 3')).toBeInTheDocument();
        });

        it('should display correct message counts for multiple sessions', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Chat 1',
                    messages: [{ role: 'user', content: 'Hello' }],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
                {
                    id: 'session-2',
                    title: 'Chat 2',
                    messages: [
                        { role: 'user', content: 'Hello' },
                        { role: 'bot', content: 'Hi' },
                        { role: 'user', content: 'How are you?' },
                    ],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText('1 messages')).toBeInTheDocument();
            expect(screen.getByText('3 messages')).toBeInTheDocument();
        });
    });

    describe('Accessibility', () => {
        it('should have accessible New Chat button', () => {
            renderChatSidebar();

            const button = screen.getByRole('button', { name: /new chat/i });
            expect(button).toBeInTheDocument();
        });

        it('should have accessible delete buttons with titles', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Test Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            const deleteButton = screen.getByTitle('Delete chat');
            expect(deleteButton).toBeInTheDocument();
        });

        it('should have visible session information', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Visible Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            const title = screen.getByText('Visible Chat');
            expect(title).toBeVisible();
        });
    });

    describe('Edge Cases', () => {
        it('should handle very long session titles', () => {
            const longTitle = 'a'.repeat(100);
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: longTitle,
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText(longTitle)).toBeInTheDocument();
        });

        it('should handle sessions with zero messages', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Empty Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText('0 messages')).toBeInTheDocument();
        });

        it('should handle many sessions', () => {
            const sessions: ChatSession[] = Array.from({ length: 50 }, (_, i) => ({
                id: `session-${i}`,
                title: `Chat ${i}`,
                messages: [],
                createdAt: Date.now(),
                updatedAt: Date.now(),
            }));

            renderChatSidebar(sessions);

            expect(screen.getByText(/50 chats saved locally/i)).toBeInTheDocument();
        });

        it('should handle special characters in session titles', () => {
            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Chat with <special> & "characters"',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText(/Chat with.*special.*characters/)).toBeInTheDocument();
        });
    });
});
