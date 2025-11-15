/**
 * Integration tests for chat flow
 * Tests the complete chat experience including sessions, messages, and state management
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import chatReducer from '@/store/slices/chatSlice';
import authReducer from '@/store/slices/authSlice';
import ChatBot from '@/components/chat/ChatBot';
import apiService from '@/services/api';

// Mock API service
vi.mock('@/services/api', () => ({
    default: {
        sendMessage: vi.fn(),
    },
}));

// Mock socket service
vi.mock('@/services/socket', () => ({
    default: {
        connect: vi.fn(),
        disconnect: vi.fn(),
        sendMessage: vi.fn(),
        on: vi.fn(),
        off: vi.fn(),
    },
}));

const renderChatWithStore = () => {
    const store = configureStore({
        reducer: {
            chat: chatReducer,
            auth: authReducer,
        },
    });

    return {
        store,
        ...render(
            <Provider store={store}>
                <ChatBot />
            </Provider>
        ),
    };
};

describe('Chat Flow Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    describe('Session Management', () => {
        it('should create new session and send first message', async () => {
            const user = userEvent.setup();

            const mockResponse = {
                message: 'Hello! How can I help you today?',
                session_id: 'session-123',
            };

            vi.mocked(apiService.sendMessage).mockResolvedValueOnce(mockResponse);

            const { store } = renderChatWithStore();

            // Create new session
            await user.click(screen.getByRole('button', { name: /new chat/i }));

            // Verify session was created
            await waitFor(() => {
                const state = store.getState();
                expect(state.chat.sessions).toHaveLength(1);
                expect(state.chat.activeSessionId).toBeTruthy();
            });

            // Send first message
            const chatInput = screen.getByPlaceholderText(/ask anything/i);
            await user.type(chatInput, 'Hello');
            await user.click(screen.getByRole('button', { name: /send/i }));

            // Verify message was added to state
            await waitFor(() => {
                const state = store.getState();
                const activeSession = state.chat.sessions.find(
                    (s) => s.id === state.chat.activeSessionId
                );
                expect(activeSession?.messages).toHaveLength(2); // User message + bot response
                expect(activeSession?.messages[0].content).toBe('Hello');
                expect(activeSession?.messages[1].content).toBe(mockResponse.message);
            });
        });

        it('should switch between sessions preserving message history', async () => {
            const user = userEvent.setup();

            const { store } = renderChatWithStore();

            // Create first session and send message
            await user.click(screen.getByRole('button', { name: /new chat/i }));
            const chatInput = screen.getByPlaceholderText(/ask anything/i);
            await user.type(chatInput, 'First session message');
            await user.click(screen.getByRole('button', { name: /send/i }));

            const firstSessionId = store.getState().chat.activeSessionId;

            // Create second session and send message
            await user.click(screen.getByRole('button', { name: /new chat/i }));
            await user.type(chatInput, 'Second session message');
            await user.click(screen.getByRole('button', { name: /send/i }));

            // Switch back to first session
            const firstSessionElement = screen.getAllByTestId('session-item')[0];
            await user.click(firstSessionElement);

            // Verify correct session is active
            await waitFor(() => {
                expect(store.getState().chat.activeSessionId).toBe(firstSessionId);
            });

            // Verify first session messages are visible
            expect(screen.getByText('First session message')).toBeInTheDocument();
            expect(screen.queryByText('Second session message')).not.toBeInTheDocument();
        });

        it('should delete session and update state', async () => {
            const user = userEvent.setup();

            const { store } = renderChatWithStore();

            // Create a session
            await user.click(screen.getByRole('button', { name: /new chat/i }));

            const initialSessionCount = store.getState().chat.sessions.length;

            // Mock window.confirm
            window.confirm = vi.fn(() => true);

            // Delete the session
            await user.click(screen.getByTitle(/delete chat/i));

            // Verify session was deleted
            await waitFor(() => {
                expect(store.getState().chat.sessions).toHaveLength(initialSessionCount - 1);
            });
        });
    });

    describe('Message Handling', () => {
        it('should handle API errors gracefully', async () => {
            const user = userEvent.setup();

            vi.mocked(apiService.sendMessage).mockRejectedValueOnce(
                new Error('API Error: Rate limit exceeded')
            );

            renderChatWithStore();

            await user.click(screen.getByRole('button', { name: /new chat/i }));

            const chatInput = screen.getByPlaceholderText(/ask anything/i);
            await user.type(chatInput, 'This will fail');
            await user.click(screen.getByRole('button', { name: /send/i }));

            // Verify error message is displayed
            await expect(
                screen.findByText(/error|failed|rate limit/i)
            ).resolves.toBeInTheDocument();
        });

        it('should prevent sending empty messages', async () => {
            const user = userEvent.setup();

            renderChatWithStore();

            await user.click(screen.getByRole('button', { name: /new chat/i }));

            // Try to send empty message
            await user.click(screen.getByRole('button', { name: /send/i }));

            // Verify API was not called
            expect(apiService.sendMessage).not.toHaveBeenCalled();
        });

        it('should enforce max message length', async () => {
            const user = userEvent.setup();

            renderChatWithStore();

            await user.click(screen.getByRole('button', { name: /new chat/i }));

            const chatInput = screen.getByPlaceholderText(/ask anything/i) as HTMLTextAreaElement;

            // Try to type a very long message (> 1000 chars)
            const longMessage = 'a'.repeat(1001);
            await user.type(chatInput, longMessage);

            // Verify input is truncated to max length
            expect(chatInput.value.length).toBeLessThanOrEqual(1000);
        });
    });

    describe('Local Storage Integration', () => {
        it('should persist sessions to localStorage', async () => {
            const user = userEvent.setup();

            const { store } = renderChatWithStore();

            // Create a session with a message
            await user.click(screen.getByRole('button', { name: /new chat/i }));
            const chatInput = screen.getByPlaceholderText(/ask anything/i);
            await user.type(chatInput, 'Test message');
            await user.click(screen.getByRole('button', { name: /send/i }));

            await waitFor(() => {
                const sessions = store.getState().chat.sessions;
                expect(sessions.length).toBeGreaterThan(0);
            });

            // Verify localStorage was updated
            const storedSessions = localStorage.getItem('chat_sessions');
            expect(storedSessions).toBeTruthy();

            const parsed = JSON.parse(storedSessions!);
            expect(parsed).toHaveLength(1);
            expect(parsed[0].messages[0].content).toBe('Test message');
        });

        it('should restore sessions from localStorage on mount', () => {
            // Seed localStorage with a session
            const mockSession = {
                id: 'restored-session',
                title: 'Restored Chat',
                messages: [
                    { role: 'user', content: 'Previous message' },
                    { role: 'bot', content: 'Previous response' },
                ],
                createdAt: Date.now(),
                updatedAt: Date.now(),
            };

            localStorage.setItem('chat_sessions', JSON.stringify([mockSession]));

            const { store } = renderChatWithStore();

            // Verify session was restored
            const state = store.getState();
            expect(state.chat.sessions).toHaveLength(1);
            expect(state.chat.sessions[0].id).toBe('restored-session');
            expect(state.chat.sessions[0].messages).toHaveLength(2);
        });
    });
});
