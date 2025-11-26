/**
 * Unit tests for Chat Redux slice
 */

import { describe, it, expect, vi } from 'vitest';
import chatReducer, {
    createSession,
    setActiveSession,
    addMessageToSession,
    updateMessageInSession,
    setSessionBackendId,
    deleteSession,
    setLoading,
    clearAllSessions,
} from './chatSlice';
import type { ChatSession, Message, ChatState } from '@/types/chat';
import { chatStorage } from '@/lib/chatStorage';

// Mock chatStorage
vi.mock('@/lib/chatStorage', () => ({
    chatStorage: {
        loadSessions: vi.fn(() => []),
        saveSessions: vi.fn(),
        clearSessions: vi.fn(),
    },
}));

describe('chatSlice', () => {
    describe('initial state', () => {
        it('should have correct initial state', () => {
            const state = chatReducer(undefined, { type: '@@INIT' });

            expect(state).toEqual({
                sessions: [],
                activeSessionId: null,
                isLoading: false,
                isTyping: false,
            });
        });

        it('should initialize with empty sessions when no data in storage', () => {
            // Note: Since the initial state is evaluated when the module loads,
            // chatStorage.loadSessions is called at import time
            // We verify the initial state reflects what loadSessions returns (mocked to return [])
            const state = chatReducer(undefined, { type: '@@INIT' });

            expect(state.sessions).toEqual([]);
            expect(state.activeSessionId).toBeNull();
        });
    });

    describe('createSession', () => {
        it('should create a new session with title', () => {
            const state = chatReducer(
                undefined,
                createSession({ id: 'session-1', title: 'My Chat' })
            );

            expect(state.sessions).toHaveLength(1);
            expect(state.sessions[0]).toMatchObject({
                id: 'session-1',
                title: 'My Chat',
                messages: [],
            });
            expect(state.activeSessionId).toBe('session-1');
            expect(chatStorage.saveSessions).toHaveBeenCalled();
        });

        it('should create a new session with default title', () => {
            const state = chatReducer(undefined, createSession({ id: 'session-1' }));

            expect(state.sessions[0].title).toBe('New Chat');
        });

        it('should add new session to the beginning of the list', () => {
            const initialState: ChatState = {
                sessions: [
                    {
                        id: 'session-1',
                        title: 'First',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                ],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(initialState, createSession({ id: 'session-2' }));

            expect(state.sessions).toHaveLength(2);
            expect(state.sessions[0].id).toBe('session-2');
            expect(state.sessions[1].id).toBe('session-1');
        });

        it('should set new session as active', () => {
            const initialState: ChatState = {
                sessions: [
                    {
                        id: 'session-1',
                        title: 'First',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                ],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(initialState, createSession({ id: 'session-2' }));

            expect(state.activeSessionId).toBe('session-2');
        });
    });

    describe('setActiveSession', () => {
        it('should set active session ID', () => {
            const state = chatReducer(undefined, setActiveSession('session-1'));

            expect(state.activeSessionId).toBe('session-1');
        });

        it('should update active session ID', () => {
            const initialState: ChatState = {
                sessions: [],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(initialState, setActiveSession('session-2'));

            expect(state.activeSessionId).toBe('session-2');
        });
    });

    describe('addMessageToSession', () => {
        const mockSession: ChatSession = {
            id: 'session-1',
            title: 'New Chat',
            messages: [],
            createdAt: Date.now(),
            updatedAt: Date.now(),
        };

        it('should add message to session', () => {
            const initialState: ChatState = {
                sessions: [mockSession],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const message: Message = {
                id: 'msg-1',
                content: 'Hello, world!',
                role: 'user',
                timestamp: Date.now(),
            };

            const state = chatReducer(
                initialState,
                addMessageToSession({ sessionId: 'session-1', message })
            );

            expect(state.sessions[0].messages).toHaveLength(1);
            expect(state.sessions[0].messages[0]).toEqual(message);
            expect(chatStorage.saveSessions).toHaveBeenCalled();
        });

        it('should auto-generate title from first users message', () => {
            const initialState: ChatState = {
                sessions: [mockSession],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const message: Message = {
                id: 'msg-1',
                content: 'What is the weather today?',
                role: 'user',
                timestamp: Date.now(),
            };

            const state = chatReducer(
                initialState,
                addMessageToSession({ sessionId: 'session-1', message })
            );

            expect(state.sessions[0].title).toBe('What is the weather today?');
        });

        it('should truncate long title to 50 characters', () => {
            const initialState: ChatState = {
                sessions: [mockSession],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const longMessage = 'a'.repeat(100);
            const message: Message = {
                id: 'msg-1',
                content: longMessage,
                role: 'user',
                timestamp: Date.now(),
            };

            const state = chatReducer(
                initialState,
                addMessageToSession({ sessionId: 'session-1', message })
            );

            expect(state.sessions[0].title).toBe('a'.repeat(40) + '...');
        });

        it('should not auto-generate title from bot message', () => {
            const initialState: ChatState = {
                sessions: [mockSession],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const message: Message = {
                id: 'msg-1',
                content: 'Hello! How can I help you?',
                role: 'bot',
                timestamp: Date.now(),
            };

            const state = chatReducer(
                initialState,
                addMessageToSession({ sessionId: 'session-1', message })
            );

            expect(state.sessions[0].title).toBe('New Chat');
        });

        it('should not change title if already set', () => {
            const sessionWithTitle: ChatSession = {
                ...mockSession,
                title: 'Existing Title',
            };

            const initialState: ChatState = {
                sessions: [sessionWithTitle],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const message: Message = {
                id: 'msg-1',
                content: 'New message',
                role: 'user',
                timestamp: Date.now(),
            };

            const state = chatReducer(
                initialState,
                addMessageToSession({ sessionId: 'session-1', message })
            );

            expect(state.sessions[0].title).toBe('Existing Title');
        });

        it('should not add message to non-existent session', () => {
            const initialState: ChatState = {
                sessions: [mockSession],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const message: Message = {
                id: 'msg-1',
                content: 'Hello',
                role: 'user',
                timestamp: Date.now(),
            };

            const state = chatReducer(
                initialState,
                addMessageToSession({ sessionId: 'non-existent', message })
            );

            expect(state.sessions[0].messages).toHaveLength(0);
        });

        it('should update session updatedAt timestamp', () => {
            const oldTimestamp = Date.now() - 10000;
            const sessionWithOldTimestamp: ChatSession = {
                ...mockSession,
                updatedAt: oldTimestamp,
            };

            const initialState: ChatState = {
                sessions: [sessionWithOldTimestamp],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const message: Message = {
                id: 'msg-1',
                content: 'Hello',
                role: 'user',
                timestamp: Date.now(),
            };

            const state = chatReducer(
                initialState,
                addMessageToSession({ sessionId: 'session-1', message })
            );

            expect(state.sessions[0].updatedAt).toBeGreaterThan(oldTimestamp);
        });
    });

    describe('updateMessageInSession', () => {
        it('should update message content', () => {
            const message: Message = {
                id: 'msg-1',
                content: 'Original content',
                role: 'bot',
                timestamp: Date.now(),
            };

            const sessionWithMessage: ChatSession = {
                id: 'session-1',
                title: 'Chat',
                messages: [message],
                createdAt: Date.now(),
                updatedAt: Date.now(),
            };

            const initialState: ChatState = {
                sessions: [sessionWithMessage],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(
                initialState,
                updateMessageInSession({
                    sessionId: 'session-1',
                    messageId: 'msg-1',
                    content: 'Updated content',
                })
            );

            expect(state.sessions[0].messages[0].content).toBe('Updated content');
            expect(chatStorage.saveSessions).toHaveBeenCalled();
        });

        it('should not update non-existent message', () => {
            const sessionWithMessage: ChatSession = {
                id: 'session-1',
                title: 'Chat',
                messages: [
                    {
                        id: 'msg-1',
                        content: 'Original',
                        role: 'bot',
                        timestamp: Date.now(),
                    },
                ],
                createdAt: Date.now(),
                updatedAt: Date.now(),
            };

            const initialState: ChatState = {
                sessions: [sessionWithMessage],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(
                initialState,
                updateMessageInSession({
                    sessionId: 'session-1',
                    messageId: 'non-existent',
                    content: 'Updated',
                })
            );

            expect(state.sessions[0].messages[0].content).toBe('Original');
        });

        it('should not update message in non-existent session', () => {
            const initialState: ChatState = {
                sessions: [],
                activeSessionId: null,
                isLoading: false,
            };

            const state = chatReducer(
                initialState,
                updateMessageInSession({
                    sessionId: 'non-existent',
                    messageId: 'msg-1',
                    content: 'Updated',
                })
            );

            expect(state.sessions).toHaveLength(0);
        });
    });

    describe('setSessionBackendId', () => {
        it('should set backend session ID', () => {
            const mockSession: ChatSession = {
                id: 'session-1',
                title: 'Chat',
                messages: [],
                createdAt: Date.now(),
                updatedAt: Date.now(),
            };

            const initialState: ChatState = {
                sessions: [mockSession],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(
                initialState,
                setSessionBackendId({ sessionId: 'session-1', backendSessionId: 42 })
            );

            expect(state.sessions[0].sessionId).toBe(42);
            expect(chatStorage.saveSessions).toHaveBeenCalled();
        });

        it('should not set backend ID for non-existent session', () => {
            const initialState: ChatState = {
                sessions: [],
                activeSessionId: null,
                isLoading: false,
            };

            const state = chatReducer(
                initialState,
                setSessionBackendId({ sessionId: 'non-existent', backendSessionId: 42 })
            );

            expect(state.sessions).toHaveLength(0);
        });
    });

    describe('deleteSession', () => {
        it('should delete session by ID', () => {
            const initialState: ChatState = {
                sessions: [
                    {
                        id: 'session-1',
                        title: 'First',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                    {
                        id: 'session-2',
                        title: 'Second',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                ],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(initialState, deleteSession('session-1'));

            expect(state.sessions).toHaveLength(1);
            expect(state.sessions[0].id).toBe('session-2');
            expect(chatStorage.saveSessions).toHaveBeenCalled();
        });

        it('should set active session to first remaining session when deleting active session', () => {
            const initialState: ChatState = {
                sessions: [
                    {
                        id: 'session-1',
                        title: 'First',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                    {
                        id: 'session-2',
                        title: 'Second',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                ],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(initialState, deleteSession('session-1'));

            expect(state.activeSessionId).toBe('session-2');
        });

        it('should set active session to null when deleting last session', () => {
            const initialState: ChatState = {
                sessions: [
                    {
                        id: 'session-1',
                        title: 'Only',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                ],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(initialState, deleteSession('session-1'));

            expect(state.sessions).toHaveLength(0);
            expect(state.activeSessionId).toBeNull();
        });

        it('should not change active session when deleting non-active session', () => {
            const initialState: ChatState = {
                sessions: [
                    {
                        id: 'session-1',
                        title: 'First',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                    {
                        id: 'session-2',
                        title: 'Second',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                ],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(initialState, deleteSession('session-2'));

            expect(state.activeSessionId).toBe('session-1');
        });
    });

    describe('setLoading', () => {
        it('should set loading to true', () => {
            const state = chatReducer(undefined, setLoading(true));

            expect(state.isLoading).toBe(true);
        });

        it('should set loading to false', () => {
            const initialState: ChatState = {
                sessions: [],
                activeSessionId: null,
                isLoading: true,
            };

            const state = chatReducer(initialState, setLoading(false));

            expect(state.isLoading).toBe(false);
        });
    });

    describe('clearAllSessions', () => {
        it('should clear all sessions', () => {
            const initialState: ChatState = {
                sessions: [
                    {
                        id: 'session-1',
                        title: 'First',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                    {
                        id: 'session-2',
                        title: 'Second',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                    },
                ],
                activeSessionId: 'session-1',
                isLoading: false,
            };

            const state = chatReducer(initialState, clearAllSessions());

            expect(state.sessions).toHaveLength(0);
            expect(state.activeSessionId).toBeNull();
            expect(chatStorage.clearSessions).toHaveBeenCalled();
        });

        it('should handle clearing when already empty', () => {
            const initialState: ChatState = {
                sessions: [],
                activeSessionId: null,
                isLoading: false,
            };

            const state = chatReducer(initialState, clearAllSessions());

            expect(state.sessions).toHaveLength(0);
            expect(state.activeSessionId).toBeNull();
        });
    });
});
