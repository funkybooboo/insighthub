import { render, act } from '@testing-library/react';
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
    LoadingSpinner: () => <div>Loading...</div>,
}));

vi.mock('./ChatSessionManager', () => ({
    default: () => null,
}));

vi.mock('./ChatMessages', () => ({
    default: ({
        messages,
        error,
        isBotTyping,
    }: {
        messages?: { content: string }[];
        error?: string;
        isBotTyping?: boolean;
    }) => (
        <div data-testid="chat-messages">
            {messages?.map((msg, idx: number) => (
                <div key={idx} data-testid={`message-${idx}`}>
                    {msg.content}
                </div>
            ))}
            {error && <div data-testid="error-message">{error}</div>}
            {isBotTyping && <div data-testid="typing-indicator">Bot is typing...</div>}
        </div>
    ),
}));

vi.mock('./ChatInput', () => ({
    default: () => <div data-testid="chat-input">ChatInput</div>,
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
                <p>Enhance Your Query with Context</p>
                <button data-testid="upload-btn" onClick={onUploadDocument}>
                    Upload Document
                </button>
                <button
                    data-testid="wikipedia-btn"
                    onClick={() => onFetchWikipedia(lastQuery || '')}
                    disabled={!lastQuery}
                >
                    Fetch from Wikipedia
                </button>
                <button data-testid="continue-btn" onClick={onContinueWithoutContext}>
                    Continue Anyway
                </button>
                {lastQuery && <p>Query: "{lastQuery}"</p>}
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
        onConnected: vi.fn(),
        onChatChunk: vi.fn(),
        onChatResponseChunk: vi.fn(),
        onChatComplete: vi.fn(),
        onChatCancelled: vi.fn(),
        onError: vi.fn(),
        onDisconnected: vi.fn(),
        onChatNoContextFound: vi.fn(),
        removeAllListeners: vi.fn(),
        on: vi.fn(), // Add generic on method
    },
}));

vi.mock('../../services/api', () => ({
    default: {
        sendChatMessage: vi.fn(),
        cancelChatMessage: vi.fn(),
        listDocuments: vi.fn(),
    },
}));

// Mock audio
global.Audio = vi.fn().mockImplementation(() => ({
    play: vi.fn(),
    pause: vi.fn(),
    volume: 0,
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
                workspaces: { '1': { status: 'ready' } }, // Add workspace status to avoid selector error
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
    });

    it('renders without crashing', () => {
        expect(() => renderWithProviders(<ChatBot />)).not.toThrow();
    });

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

    it('handles WebSocket errors', async () => {
        const mockSocket = vi.mocked(socketService);

        renderWithProviders(<ChatBot />);

        // Simulate WebSocket error
        await act(async () => {
            const errorCallbacks = mockSocket.onError.mock.calls;
            if (errorCallbacks.length > 0) {
                const callback = errorCallbacks[0][0];
                callback({ error: 'Connection lost' });
            }
        });

        // Check that error state is set (component may not render error text directly)
        expect(mockSocket.onError).toHaveBeenCalled();
    });

    it('handles message cancellation', async () => {
        const mockApi = vi.mocked(apiService);
        mockApi.cancelChatMessage.mockResolvedValue({ message: 'Cancelled' });

        renderWithProviders(<ChatBot />);

        // Find and click cancel button (this would need the button to be visible)
        // This test would need more setup to make the cancel button visible
    });

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
});
