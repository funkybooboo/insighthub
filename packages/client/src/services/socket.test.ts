/**
 * Unit tests for Socket service
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { io, type Socket } from 'socket.io-client';
import type { MockedFunction } from 'vitest';
import socketService, {
    type ChatMessageData,
    type ChatChunkData,
    type ChatCompleteData,
    type ErrorData,
} from './socket';

// Mock socket.io-client
vi.mock('socket.io-client', () => ({
    io: vi.fn(),
}));

const mockedIo = io as MockedFunction<typeof io>;

describe('SocketService', () => {
    let mockSocket: {
        connected: boolean;
        emit: MockedFunction<(event: string, data: unknown) => void>;
        on: MockedFunction<(event: string, callback: (data: unknown) => void) => void>;
        off: MockedFunction<(event: string, callback?: (data: unknown) => void) => void>;
        disconnect: MockedFunction<() => void>;
        removeAllListeners: MockedFunction<() => void>;
    };

    beforeEach(() => {
        socketService.disconnect();

        mockSocket = {
            connected: false,
            emit: vi.fn(),
            on: vi.fn(),
            off: vi.fn(),
            disconnect: vi.fn(),
            removeAllListeners: vi.fn(),
        };

        mockedIo.mockReturnValue(mockSocket as unknown as Socket);
        vi.clearAllMocks();
    });

    afterEach(() => {
        socketService.disconnect();
        vi.restoreAllMocks();
    });

    describe('Connection Management', () => {
        it('should establish a socket connection when connect is called', () => {
            socketService.connect();

            expect(mockedIo).toHaveBeenCalled();
        });

        it('should close the socket connection when disconnect is called', () => {
            socketService.connect();
            socketService.disconnect();

            expect(mockSocket.disconnect).toHaveBeenCalled();
        });

        it('should report connection status accurately', () => {
            expect(socketService.isConnected()).toBe(false);

            mockSocket.connected = true;
            socketService.connect();

            expect(socketService.isConnected()).toBe(true);
        });
    });

    describe('Message Sending', () => {
        it('should send a chat message with all provided data', () => {
            const messageData: ChatMessageData = {
                message: 'Hello, world!',
                session_id: 1,
                workspace_id: 2,
                rag_type: 'vector',
            };

            socketService.connect();
            socketService.sendMessage(messageData);

            expect(mockSocket.emit).toHaveBeenCalledWith(
                'chat_message',
                expect.objectContaining({
                    message: 'Hello, world!',
                    session_id: 1,
                    workspace_id: 2,
                    rag_type: 'vector',
                    client_id: expect.any(String),
                })
            );
        });

        it('should send message with minimal required data', () => {
            const messageData: ChatMessageData = {
                message: 'Hello',
            };

            socketService.connect();
            socketService.sendMessage(messageData);

            expect(mockSocket.emit).toHaveBeenCalledWith(
                'chat_message',
                expect.objectContaining({
                    message: 'Hello',
                    client_id: expect.any(String),
                })
            );
        });

        it('should reject message sending when not connected', () => {
            const messageData: ChatMessageData = {
                message: 'Hello',
            };

            expect(() => socketService.sendMessage(messageData)).toThrow();
        });
    });

    describe('Event Handling', () => {
        it('should deliver chat chunks to registered listeners', () => {
            const callback = vi.fn();
            const chunkData: ChatChunkData = { chunk: 'Hello ' };

            socketService.connect();
            socketService.onChatChunk(callback);

            // Simulate receiving a chunk
            const onCall = mockSocket.on.mock.calls.find((call) => call[0] === 'chat_chunk');
            if (onCall) {
                const [, handler] = onCall;
                (handler as (data: ChatChunkData) => void)(chunkData);
            }

            expect(callback).toHaveBeenCalledWith(chunkData);
        });

        it('should deliver chat completion events to registered listeners', () => {
            const callback = vi.fn();
            const completeData: ChatCompleteData = {
                session_id: 1,
                full_response: 'Hello, world!',
                context: [],
            };

            socketService.connect();
            socketService.onChatComplete(callback);

            // Simulate receiving completion
            const onCall = mockSocket.on.mock.calls.find((call) => call[0] === 'chat_complete');
            if (onCall) {
                const [, handler] = onCall;
                (handler as (data: ChatCompleteData) => void)(completeData);
            }

            expect(callback).toHaveBeenCalledWith(completeData);
        });

        it('should reject event listener registration when not connected', () => {
            const callback = vi.fn();

            expect(() => socketService.onChatChunk(callback)).toThrow();
            expect(() => socketService.onChatComplete(callback)).toThrow();
        });

        it('should deliver error events to registered listeners', () => {
            const callback = vi.fn();
            const errorData: ErrorData = { error: 'Connection failed' };

            socketService.connect();
            socketService.onError(callback);

            const onCall = mockSocket.on.mock.calls.find((call) => call[0] === 'error');
            if (onCall) {
                const [, handler] = onCall;
                (handler as (data: ErrorData) => void)(errorData);
            }

            expect(callback).toHaveBeenCalledWith(errorData);
        });
    });

    describe('Message Cancellation', () => {
        it('should cancel an active message request', () => {
            const messageData: ChatMessageData = {
                message: 'Hello, world!',
            };

            socketService.connect();
            socketService.sendMessage(messageData);
            mockSocket.emit.mockClear(); // Clear the send message call

            socketService.cancelMessage();

            expect(mockSocket.emit).toHaveBeenCalledWith(
                'cancel_message',
                expect.objectContaining({
                    client_id: expect.any(String),
                })
            );
        });

        it('should handle cancel requests gracefully when no active message', () => {
            socketService.connect();

            socketService.cancelMessage();

            expect(mockSocket.emit).not.toHaveBeenCalled();
        });

        it('should reject cancellation when not connected', () => {
            expect(() => socketService.cancelMessage()).toThrow();
        });
    });

    describe('Event Cleanup', () => {
        it('should remove all event listeners', () => {
            socketService.connect();
            socketService.removeAllListeners();

            expect(mockSocket.removeAllListeners).toHaveBeenCalled();
        });

        it('should handle cleanup operations safely when not connected', () => {
            expect(() => socketService.removeAllListeners()).not.toThrow();
            expect(() => socketService.off('chat_chunk')).not.toThrow();
        });
    });
});
