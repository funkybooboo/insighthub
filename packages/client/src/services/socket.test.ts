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
vi.mock('socket.io-client');

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
        // Create a fresh socket service instance for each test
        // Reset the socket to null
        socketService.disconnect();

        // Create mock socket
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

    describe('connect', () => {
        it('should connect to the socket server', () => {
            socketService.connect();

            expect(mockedIo).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    transports: ['websocket', 'polling'],
                    reconnection: true,
                    reconnectionDelay: 1000,
                    reconnectionAttempts: 5,
                })
            );
        });

        it('should not reconnect if already connected', () => {
            mockSocket.connected = true;
            socketService.connect();
            socketService.connect();

            expect(mockedIo).toHaveBeenCalledTimes(1);
        });

        it('should use correct socket URL from environment', () => {
            socketService.connect();

            expect(mockedIo).toHaveBeenCalledWith(
                expect.stringContaining('http://localhost:5000'),
                expect.any(Object)
            );
        });
    });

    describe('disconnect', () => {
        it('should disconnect from the socket server', () => {
            socketService.connect();
            socketService.disconnect();

            expect(mockSocket.disconnect).toHaveBeenCalled();
        });

        it('should handle disconnect when not connected', () => {
            socketService.disconnect();

            expect(mockSocket.disconnect).not.toHaveBeenCalled();
        });
    });

    describe('isConnected', () => {
        it('should return true when connected', () => {
            mockSocket.connected = true;
            socketService.connect();

            expect(socketService.isConnected()).toBe(true);
        });

        it('should return false when not connected', () => {
            mockSocket.connected = false;

            expect(socketService.isConnected()).toBe(false);
        });

        it('should return false when socket is null', () => {
            expect(socketService.isConnected()).toBe(false);
        });
    });

    describe('sendMessage', () => {
        it('should send a chat message', () => {
            const messageData: ChatMessageData = {
                message: 'Hello, world!',
                session_id: 1,
                rag_type: 'vector',
            };

            socketService.connect();
            socketService.sendMessage(messageData);

            // Verify emit was called with correct event name and message data (plus client_id)
            expect(mockSocket.emit).toHaveBeenCalledWith(
                'chat_message',
                expect.objectContaining({
                    message: 'Hello, world!',
                    session_id: 1,
                    rag_type: 'vector',
                    client_id: expect.stringMatching(/^client-\d+-[a-z0-9]+$/),
                })
            );
        });

        it('should send message without optional parameters', () => {
            const messageData: ChatMessageData = {
                message: 'Hello',
            };

            socketService.connect();
            socketService.sendMessage(messageData);

            // Verify emit was called with correct event name and message data (plus client_id)
            expect(mockSocket.emit).toHaveBeenCalledWith(
                'chat_message',
                expect.objectContaining({
                    message: 'Hello',
                    client_id: expect.stringMatching(/^client-\d+-[a-z0-9]+$/),
                })
            );
        });

        it('should throw error if socket not connected', () => {
            const messageData: ChatMessageData = {
                message: 'Hello',
            };

            expect(() => socketService.sendMessage(messageData)).toThrow(
                'Socket not connected. Call connect() first.'
            );
        });
    });

    describe('onChatChunk', () => {
        it('should register chat chunk listener', () => {
            const callback = vi.fn();

            socketService.connect();
            socketService.onChatChunk(callback);

            expect(mockSocket.on).toHaveBeenCalledWith('chat_chunk', callback);
        });

        it('should throw error if socket not connected', () => {
            const callback = vi.fn();

            expect(() => socketService.onChatChunk(callback)).toThrow(
                'Socket not connected. Call connect() first.'
            );
        });

        it('should receive chat chunks correctly', () => {
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
    });

    describe('onChatComplete', () => {
        it('should register chat complete listener', () => {
            const callback = vi.fn();

            socketService.connect();
            socketService.onChatComplete(callback);

            expect(mockSocket.on).toHaveBeenCalledWith('chat_complete', callback);
        });

        it('should throw error if socket not connected', () => {
            const callback = vi.fn();

            expect(() => socketService.onChatComplete(callback)).toThrow(
                'Socket not connected. Call connect() first.'
            );
        });

        it('should receive complete event with data', () => {
            const callback = vi.fn();
            const completeData: ChatCompleteData = {
                session_id: 1,
                full_response: 'Hello, how can I help you?',
            };

            socketService.connect();
            socketService.onChatComplete(callback);

            const onCall = mockSocket.on.mock.calls.find((call) => call[0] === 'chat_complete');
            if (onCall) {
                const [, handler] = onCall;
                (handler as (data: ChatCompleteData) => void)(completeData);
            }

            expect(callback).toHaveBeenCalledWith(completeData);
        });
    });

    describe('onError', () => {
        it('should register error listener', () => {
            const callback = vi.fn();

            socketService.connect();
            socketService.onError(callback);

            expect(mockSocket.on).toHaveBeenCalledWith('error', callback);
        });

        it('should throw error if socket not connected', () => {
            const callback = vi.fn();

            expect(() => socketService.onError(callback)).toThrow(
                'Socket not connected. Call connect() first.'
            );
        });

        it('should handle error events', () => {
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

    describe('onConnected', () => {
        it('should register connected listener', () => {
            const callback = vi.fn();

            socketService.connect();
            socketService.onConnected(callback);

            expect(mockSocket.on).toHaveBeenCalledWith('connected', callback);
        });

        it('should throw error if socket not connected', () => {
            const callback = vi.fn();

            expect(() => socketService.onConnected(callback)).toThrow(
                'Socket not connected. Call connect() first.'
            );
        });
    });

    describe('onDisconnected', () => {
        it('should register disconnected listener', () => {
            const callback = vi.fn();

            socketService.connect();
            socketService.onDisconnected(callback);

            expect(mockSocket.on).toHaveBeenCalledWith('disconnect', callback);
        });

        it('should throw error if socket not connected', () => {
            const callback = vi.fn();

            expect(() => socketService.onDisconnected(callback)).toThrow(
                'Socket not connected. Call connect() first.'
            );
        });
    });

    describe('cancelMessage', () => {
        it('should emit cancel_message with client_id when there is an active request', () => {
            const messageData: ChatMessageData = {
                message: 'Hello, world!',
            };

            socketService.connect();
            socketService.sendMessage(messageData);

            // Clear previous emit calls
            vi.mocked(mockSocket.emit).mockClear();

            socketService.cancelMessage();

            expect(mockSocket.emit).toHaveBeenCalledWith(
                'cancel_message',
                expect.objectContaining({
                    client_id: expect.stringMatching(/^client-\d+-[a-z0-9]+$/),
                })
            );
        });

        it('should not emit cancel_message when there is no active request', () => {
            socketService.connect();

            socketService.cancelMessage();

            expect(mockSocket.emit).not.toHaveBeenCalled();
        });

        it('should throw error if socket not connected', () => {
            expect(() => socketService.cancelMessage()).toThrow(
                'Socket not connected. Call connect() first.'
            );
        });
    });

    describe('onChatCancelled', () => {
        it('should register chat cancelled listener', () => {
            const callback = vi.fn();

            socketService.connect();
            socketService.onChatCancelled(callback);

            expect(mockSocket.on).toHaveBeenCalledWith('chat_cancelled', callback);
        });

        it('should throw error if socket not connected', () => {
            const callback = vi.fn();

            expect(() => socketService.onChatCancelled(callback)).toThrow(
                'Socket not connected. Call connect() first.'
            );
        });
    });

    describe('removeAllListeners', () => {
        it('should remove all event listeners', () => {
            socketService.connect();
            socketService.removeAllListeners();

            expect(mockSocket.removeAllListeners).toHaveBeenCalled();
        });

        it('should handle removeAllListeners when socket is null', () => {
            expect(() => socketService.removeAllListeners()).not.toThrow();
        });
    });

    describe('off', () => {
        it('should remove specific event listener', () => {
            const callback = vi.fn();

            socketService.connect();
            socketService.off('chat_chunk', callback);

            expect(mockSocket.off).toHaveBeenCalledWith('chat_chunk', callback);
        });

        it('should remove listener without callback', () => {
            socketService.connect();
            socketService.off('chat_chunk');

            expect(mockSocket.off).toHaveBeenCalledWith('chat_chunk', undefined);
        });

        it('should handle off when socket is null', () => {
            expect(() => socketService.off('chat_chunk')).not.toThrow();
        });
    });
});
