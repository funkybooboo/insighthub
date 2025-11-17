/**
 * Socket.IO service for real-time chat streaming.
 */

import { io, Socket } from 'socket.io-client';

const SOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface ChatMessageData {
    message: string;
    session_id?: number;
    rag_type?: string;
}

export interface ChatChunkData {
    chunk: string;
}

export interface ChatCompleteData {
    session_id: number;
    full_response: string;
}

export interface ErrorData {
    error: string;
}

export type ChatChunkCallback = (data: ChatChunkData) => void;
export type ChatCompleteCallback = (data: ChatCompleteData) => void;
export type ErrorCallback = (data: ErrorData) => void;
export type ConnectedCallback = () => void;
export type DisconnectedCallback = () => void;

class SocketService {
    private socket: Socket | null = null;

    /**
     * Connect to the Socket.IO server
     */
    connect(): void {
        if (this.socket?.connected) {
            return;
        }

        this.socket = io(SOCKET_URL, {
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5,
        });
    }

    /**
     * Disconnect from the Socket.IO server
     */
    disconnect(): void {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
    }

    /**
     * Check if socket is connected
     */
    isConnected(): boolean {
        return this.socket?.connected ?? false;
    }

    /**
     * Send a chat message
     */
    sendMessage(data: ChatMessageData): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.emit('chat_message', data);
    }

    /**
     * Cancel the current chat message
     */
    cancelMessage(): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.emit('cancel_message');
    }

    /**
     * Listen for chat chunk events
     */
    onChatChunk(callback: ChatChunkCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('chat_chunk', callback);
    }

    /**
     * Listen for chat complete events
     */
    onChatComplete(callback: ChatCompleteCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('chat_complete', callback);
    }

    /**
     * Listen for error events
     */
    onError(callback: ErrorCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('error', callback);
    }

    /**
     * Listen for connection events
     */
    onConnected(callback: ConnectedCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('connected', callback);
    }

    /**
     * Listen for disconnection events
     */
    onDisconnected(callback: DisconnectedCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('disconnect', callback);
    }

    /**
     * Remove all event listeners
     */
    removeAllListeners(): void {
        if (this.socket) {
            this.socket.removeAllListeners();
        }
    }

    /**
     * Remove a specific event listener
     */
    off(event: string, callback?: (...args: unknown[]) => void): void {
        if (this.socket) {
            this.socket.off(event, callback);
        }
    }
}

export const socketService = new SocketService();
export default socketService;
