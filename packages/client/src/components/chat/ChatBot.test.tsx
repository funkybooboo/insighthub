import { render, act, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ChatBot from './ChatBot';
import chatSlice from '../../store/slices/chatSlice';
import workspaceSlice from '../../store/slices/workspaceSlice';
import statusSlice from '../../store/slices/statusSlice';
import socketService from '../../services/socket';
import apiService from '../../services/api';

// Mock the UI components to avoid styling issues
vi.mock('@/components/shared', () => ({
    LoadingSpinner: ({ className }: { className?: string }) => (
        <div className={className} data-testid="loading-spinner">
            Loading...
        </div>
    ),
}));

vi.mock('./ChatSessionManager', () => ({
    default: () => null,
}));

vi.mock('./ChatMessages', () => ({
    default: ({
        messages,
        error,
        isBotTyping,
        onFetchWikipedia,
        onUploadDocument: _onUploadDocument,
        onContinueChat: _onContinueChat,
    }: {
        messages?: { content: string; id: string }[];
        error?: string;
        isBotTyping?: boolean;
        onFetchWikipedia?: (query: string) => void;
        onUploadDocument?: () => void;
        onContinueChat?: () => void;
    }) => (
        <div data-testid="chat-messages">
            {messages?.map((msg) => (
                <div key={msg.id} data-testid={`message-${msg.id}`}>
                    {msg.content}
                </div>
            ))}
            {error && <div data-testid="error-message">{error}</div>}
            {isBotTyping && <div data-testid="typing-indicator">Bot is typing...</div>}
            {onFetchWikipedia && (
                <button
                    data-testid="test-fetch-wikipedia"
                    onClick={() => onFetchWikipedia('test query')}
                >
                    Fetch Wikipedia
                </button>
            )}
        </div>
    ),
}));

vi.mock('./ChatInput', () => ({
    default: ({
        onSubmit,
        onCancel,
        isTyping,
    }: {
        onSubmit: (data: { prompt: string }) => void;
        onCancel: () => void;
        isTyping: boolean;
    }) => (
        <div data-testid="chat-input">
            <button
                data-testid="submit-message"
                onClick={() => onSubmit({ prompt: 'test message' })}
            >
                Send
            </button>
            <button data-testid="cancel-message" onClick={onCancel}>
                Cancel
            </button>
            {isTyping && <div data-testid="typing-status">Typing...</div>}
        </div>
    ),
}));

vi.mock('./RAGEnhancementPrompt', () => ({
    default: ({
        isVisible,
        onUploadDocument,
        onFetchWikipedia,
        onContinueWithoutContext,
        lastQuery,
    }: {
        isVisible: boolean;
        onUploadDocument: () => void;
        onFetchWikipedia: (query: string) => void;
        onContinueWithoutContext: () => void;
        lastQuery?: string;
    }) =>
        isVisible ? (
            <div data-testid="rag-prompt">
                <button data-testid="upload-btn" onClick={onUploadDocument}>
                    Upload Document
                </button>
                <button
                    data-testid="wikipedia-btn"
                    onClick={() => onFetchWikipedia(lastQuery || '')}
                >
                    Fetch from Wikipedia
                </button>
                <button data-testid="continue-btn" onClick={onContinueWithoutContext}>
                    Continue Anyway
                </button>
            </div>
        ) : null,
}));

// Mock services
vi.mock('../../services/socket', () => ({
    default: {
        connect: vi.fn(),
        disconnect: vi.fn(),
        sendMessage: vi.fn(),
        cancelMessage: vi.fn(),
        onConnected: vi.fn(() => vi.fn()), // Return cleanup function
        onChatChunk: vi.fn(() => vi.fn()),
        onChatResponseChunk: vi.fn(() => vi.fn()),
        onChatComplete: vi.fn(() => vi.fn()),
        onChatCancelled: vi.fn(() => vi.fn()),
        onError: vi.fn(() => vi.fn()),
        onDisconnected: vi.fn(() => vi.fn()),
        onChatNoContextFound: vi.fn(() => vi.fn()),
        removeAllListeners: vi.fn(),
        on: vi.fn(() => vi.fn()), // Return cleanup function
    },
}));

vi.mock('../../services/api', () => ({
    default: {
        sendChatMessage: vi.fn().mockResolvedValue({}),
        cancelChatMessage: vi.fn().mockResolvedValue({}),
        listDocuments: vi.fn().mockResolvedValue([]),
        createChatSession: vi.fn().mockResolvedValue({
            session_id: 1,
            title: 'New Chat',
        }),
        fetchWikipediaArticle: vi.fn().mockResolvedValue({}),
    },
}));

const createMockStore = (initialState = {}) => {
    return configureStore({
        reducer: {
            chat: chatSlice,
            workspace: workspaceSlice,
            status: statusSlice,
        },
        preloadedState: {
            chat: {
                sessions: [
                    {
                        id: 'session-1',
                        title: 'Test Session',
                        messages: [],
                        createdAt: Date.now(),
                        updatedAt: Date.now(),
                        sessionId: 1,
                    },
                ],
                activeSessionId: 'session-1',
                isTyping: false,
            },
            workspace: {
                workspaces: [
                    {
                        id: 1,
                        name: 'Test Workspace',
                        description: 'Test workspace',
                        status: 'ready',
                        created_at: '2025-01-01T00:00:00Z',
                        updated_at: '2025-01-01T00:00:00Z',
                    },
                ],
                activeWorkspaceId: 1,
                isLoading: false,
                error: null,
            },
            status: {
                documents: {},
                workspaces: { '1': { status: 'ready' } },
                wikipediaFetches: {},
            },
            ...initialState,
        },
    });
};

const renderWithProviders = (component: React.ReactElement, store = createMockStore()) => {
    return render(<Provider store={store}>{component}</Provider>);
};

describe('ChatBot', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Reset API service mocks to default resolved values
        vi.mocked(apiService.sendChatMessage).mockResolvedValue({});
        vi.mocked(apiService.cancelChatMessage).mockResolvedValue({});
        vi.mocked(apiService.listDocuments).mockResolvedValue([]);
        vi.mocked(apiService.createChatSession).mockResolvedValue({
            session_id: 1,
            title: 'New Chat',
        });
        vi.mocked(apiService.fetchWikipediaArticle).mockResolvedValue({});
    });

    describe('Basic Rendering', () => {
        it('renders without crashing', () => {
            expect(() => renderWithProviders(<ChatBot />)).not.toThrow();
        });
    });

    describe('Socket Connection', () => {
        it('connects to socket on mount', () => {
            const mockSocket = vi.mocked(socketService);
            renderWithProviders(<ChatBot />);
            expect(mockSocket.connect).toHaveBeenCalled();
        });

        it('disconnects from socket on unmount', () => {
            const mockSocket = vi.mocked(socketService);
            const { unmount } = renderWithProviders(<ChatBot />);
            unmount();
            expect(mockSocket.disconnect).toHaveBeenCalled();
        });

        it('removes all listeners on unmount', () => {
            const mockSocket = vi.mocked(socketService);
            const { unmount } = renderWithProviders(<ChatBot />);
            unmount();
            expect(mockSocket.removeAllListeners).toHaveBeenCalled();
        });

        it('sets up socket event listeners', () => {
            const mockSocket = vi.mocked(socketService);
            renderWithProviders(<ChatBot />);
            expect(mockSocket.onConnected).toHaveBeenCalled();
            expect(mockSocket.onChatResponseChunk).toHaveBeenCalled();
            expect(mockSocket.onChatComplete).toHaveBeenCalled();
            expect(mockSocket.onChatCancelled).toHaveBeenCalled();
            expect(mockSocket.onError).toHaveBeenCalled();
            expect(mockSocket.onDisconnected).toHaveBeenCalled();
        });
    });

    describe('Socket Event Handling', () => {
        it('handles chats completion', async () => {
            const mockSocket = vi.mocked(socketService);
            renderWithProviders(<ChatBot />);

            await waitFor(() => {
                expect(mockSocket.onChatResponseChunk).toHaveBeenCalled();
                expect(mockSocket.onChatComplete).toHaveBeenCalled();
            });

            await act(async () => {
                const chunkCallback = mockSocket.onChatResponseChunk.mock.calls[0][0];
                chunkCallback({ chunk: 'Hello', message_id: 'msg-123' });

                const completeCallback = mockSocket.onChatComplete.mock.calls[0][0];
                completeCallback({
                    session_id: 1,
                    full_response: 'Hello world',
                    context: [],
                });
            });

            expect(screen.queryByTestId('typing-indicator')).not.toBeInTheDocument();
        });

        it('handles chats cancellation', async () => {
            const mockSocket = vi.mocked(socketService);
            renderWithProviders(<ChatBot />);

            await waitFor(() => {
                expect(mockSocket.onChatCancelled).toHaveBeenCalled();
            });

            await act(async () => {
                const cancelCallback = mockSocket.onChatCancelled.mock.calls[0][0];
                cancelCallback();
            });

            expect(screen.queryByTestId('typing-indicator')).not.toBeInTheDocument();
        });
    });

    describe('Document Loading', () => {
        it('loads documents on mount', () => {
            const mockApi = vi.mocked(apiService);
            mockApi.listDocuments.mockResolvedValue({ documents: [] });

            renderWithProviders(<ChatBot />);

            expect(mockApi.listDocuments).toHaveBeenCalledWith(1);
        });

        it('handles document loading errors gracefully', () => {
            const mockApi = vi.mocked(apiService);
            mockApi.listDocuments.mockRejectedValue(new Error('Load failed'));

            expect(() => renderWithProviders(<ChatBot />)).not.toThrow();
        });
    });

    describe('Session Management', () => {
        it('creates initial session when none exists', async () => {
            const mockApi = vi.mocked(apiService);
            mockApi.createChatSession.mockResolvedValue({
                session_id: 1,
                title: 'New Chat',
            });

            const store = createMockStore({
                chat: {
                    sessions: [],
                    activeSessionId: null,
                    isTyping: false,
                },
            });

            await act(async () => {
                renderWithProviders(<ChatBot />, store);
            });

            expect(mockApi.createChatSession).toHaveBeenCalledWith(1, 'New Chat');
        });

        it('handles session creation errors with fallback', async () => {
            const mockApi = vi.mocked(apiService);
            mockApi.createChatSession.mockRejectedValue(new Error('Create failed'));

            const store = createMockStore({
                chat: {
                    sessions: [],
                    activeSessionId: null,
                    isTyping: false,
                },
            });

            await act(async () => {
                renderWithProviders(<ChatBot />, store);
            });

            expect(mockApi.createChatSession).toHaveBeenCalled();
        });

        it('sets first session as active when no active session', async () => {
            const store = createMockStore({
                chat: {
                    sessions: [
                        {
                            id: 'session-1',
                            title: 'Test Session',
                            messages: [],
                            createdAt: Date.now(),
                            updatedAt: Date.now(),
                            sessionId: 1,
                        },
                    ],
                    activeSessionId: null,
                    isTyping: false,
                },
            });

            await act(async () => {
                renderWithProviders(<ChatBot />, store);
            });

            // The component should set the first session as active
            expect(store.getState().chat.activeSessionId).toBe('session-1');
        });
    });
});
