/**
 * Component tests for ChatSidebar
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ChatSidebar from './ChatSidebar';
import chatReducer, {
    createSession,
    setActiveSession,
    addMessage,
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
            store.dispatch(createSession({ id: session.id }));
            if (session.messages.length > 0) {
                session.messages.forEach((message) => {
                    store.dispatch(
                        addMessage({
                            sessionId: session.id,
                            message,
                        })
                    );
                });
            }
        });

        return { store, ...render(<Provider store={store}><ChatSidebar /></Provider>) };
    };

    beforeEach(() => {
        vi.clearAllMocks();
        mockConfirm.mockReturnValue(true);
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
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

            const { store } = renderChatSidebar(sessions);
            store.dispatch(setActiveSession('session-1'));

            const sessionElement = screen.getByText('Active Chat').closest('div');
            expect(sessionElement).toHaveClass('bg-blue-100');
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
                    title: 'Active Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
                {
                    id: 'session-2',
                    title: 'Inactive Chat',
                    messages: [],
                    createdAt: Date.now(),
                    updatedAt: Date.now(),
                },
            ];

            const { store } = renderChatSidebar(sessions);
            store.dispatch(setActiveSession('session-1'));

            const inactiveElement = screen.getByText('Inactive Chat').closest('div');
            expect(inactiveElement).toHaveClass('bg-white');
            expect(inactiveElement).not.toHaveClass('bg-blue-100');
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

            expect(mockConfirm).toHaveBeenCalledWith(
                'Are you sure you want to delete this chat?'
            );
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

        it('should display minutes ago for timestamps within last hour', () => {
            const now = Date.now();
            const thirtyMinutesAgo = now - 30 * 60 * 1000;
            vi.setSystemTime(now);

            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Recent Chat',
                    messages: [],
                    createdAt: thirtyMinutesAgo,
                    updatedAt: thirtyMinutesAgo,
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText('30m ago')).toBeInTheDocument();
        });

        it('should display hours ago for timestamps within last day', () => {
            const now = Date.now();
            const fiveHoursAgo = now - 5 * 60 * 60 * 1000;
            vi.setSystemTime(now);

            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Recent Chat',
                    messages: [],
                    createdAt: fiveHoursAgo,
                    updatedAt: fiveHoursAgo,
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText('5h ago')).toBeInTheDocument();
        });

        it('should display days ago for timestamps within last week', () => {
            const now = Date.now();
            const threeDaysAgo = now - 3 * 24 * 60 * 60 * 1000;
            vi.setSystemTime(now);

            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Older Chat',
                    messages: [],
                    createdAt: threeDaysAgo,
                    updatedAt: threeDaysAgo,
                },
            ];

            renderChatSidebar(sessions);

            expect(screen.getByText('3d ago')).toBeInTheDocument();
        });

        it('should display full date for timestamps older than 7 days', () => {
            const now = Date.now();
            const tenDaysAgo = new Date(now - 10 * 24 * 60 * 60 * 1000);
            vi.setSystemTime(now);

            const sessions: ChatSession[] = [
                {
                    id: 'session-1',
                    title: 'Old Chat',
                    messages: [],
                    createdAt: tenDaysAgo.getTime(),
                    updatedAt: tenDaysAgo.getTime(),
                },
            ];

            renderChatSidebar(sessions);

            const expectedDate = tenDaysAgo.toLocaleDateString();
            expect(screen.getByText(expectedDate)).toBeInTheDocument();
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

            const messageCounts = screen.getAllByText(/\d+ messages?/);
            expect(messageCounts[0]).toHaveTextContent('1 messages');
            expect(messageCounts[1]).toHaveTextContent('3 messages');
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
