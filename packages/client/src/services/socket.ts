/**
  * Socket.IO service for real-time chats streaming.
  */

import { io, Socket } from 'socket.io-client';
import { logger } from '../lib/logger';
import { type Context } from '../types/chat'; // Import Context type

const SOCKET_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface ChatMessageData {
    message: string;
    session_id?: number;
    workspace_id?: number; // Added workspace_id
    rag_type?: string;
    client_id?: string;
}

export interface ChatChunkData {
    chunk: string;
}

export interface ChatResponseChunkData {
    chunk: string;
    message_id: string;
}

export interface ChatCompleteData {
    session_id: number;
    full_response: string;
    context?: Context[]; // Added context field
}

export interface ErrorData {
    error: string;
}

export interface ChatCancelledData {
    status: string;
}

export interface DocumentStatusData {
    document_id: number;
    workspace_id: number;
    status: 'pending' | 'processing' | 'ready' | 'failed' | 'deleting' | 'deleted';
    message?: string;
    error?: string;
    progress?: number;
    timestamp?: string;
    filename?: string;
    chunk_count?: number;
}

export interface WorkspaceStatusData {
    workspace_id: number;
    user_id: number;
    status: 'provisioning' | 'ready' | 'failed' | 'deleting' | 'deleted';
    message?: string;
    error?: string;
    timestamp?: string;
}

export interface SubscribedData {
    user_id: number;
    room: string;
}

export interface ChatNoContextFoundData {
    session_id: number;
    query: string;
}

export interface WikipediaFetchStatusData {
    workspace_id: number;
    query: string;
    status: 'fetching' | 'processing' | 'completed' | 'failed';
    document_ids?: number[];
    message?: string;
}

export type ChatChunkCallback = (data: ChatChunkData) => void;
export type ChatResponseChunkCallback = (data: ChatResponseChunkData) => void;
export type ChatCompleteCallback = (data: ChatCompleteData) => void;
export type ChatCancelledCallback = (data: ChatCancelledData) => void;
export type ErrorCallback = (data: ErrorData) => void;
export type ConnectedCallback = () => void;
export type DisconnectedCallback = () => void;
export type DocumentStatusCallback = (data: DocumentStatusData) => void;
export type WorkspaceStatusCallback = (data: WorkspaceStatusData) => void;
export type SubscribedCallback = (data: SubscribedData) => void;
export type ChatNoContextFoundCallback = (data: ChatNoContextFoundData) => void;
export type WikipediaFetchStatusCallback = (data: WikipediaFetchStatusData) => void;

class SocketService {
    private socket: Socket | null = null;
    private currentClientId: string | null = null;

    /**
      * Connect to the Socket.IO server
      */
    connect(): void {
        if (this.socket?.connected) {
            logger.debug('Socket already connected, skipping connection attempt');
            return;
        }

        logger.info('Connecting to Socket.IO server', { url: SOCKET_URL });
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
            logger.info('Disconnecting from Socket.IO server');
            this.socket.disconnect();
            this.socket = null;
        } else {
            logger.debug('Socket already disconnected');
        }
        this.currentClientId = null;
    }

    /**
     * Check if socket is connected
     */
    isConnected(): boolean {
        return this.socket?.connected ?? false;
    }

    /**
      * Send a chats message
      */
    sendMessage(data: ChatMessageData): void {
        if (!this.socket) {
            logger.error('Cannot send message: Socket not connected');
            throw new Error('Socket not connected. Call connect() first.');
        }
        // Generate a unique client ID for this message (for cancellation tracking)
        this.currentClientId = `client-${Date.now()}-${Math.random().toString(36).substring(7)}`;
        logger.debug('Sending chat message', {
            session_id: data.session_id,
            workspace_id: data.workspace_id,
            client_id: this.currentClientId,
        });
        this.socket.emit('chat_message', {
            ...data,
            client_id: this.currentClientId,
        });
    }

    /**
     * Cancel the current chats message
     */
    cancelMessage(): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        if (this.currentClientId) {
            this.socket.emit('cancel_message', { client_id: this.currentClientId });
            this.currentClientId = null;
        }
    }

    /**
     * Listen for chats chunk events
     */
    onChatChunk(callback: ChatChunkCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('chat_chunk', callback);
    }

    /**
     * Listen for chats response chunk events
     */
    onChatResponseChunk(callback: ChatResponseChunkCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('chats.response_chunk', callback);
    }

    /**
     * Listen for chats complete events
     */
    onChatComplete(callback: ChatCompleteCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('chat_complete', callback);
    }

    /**
     * Listen for chats cancelled events
     */
    onChatCancelled(callback: ChatCancelledCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('chat_cancelled', callback);
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
     * Subscribe to status updates for a users
     */
    subscribeToStatus(userId: number): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.emit('subscribe_status', { user_id: userId });
    }

    /**
     * Listen for document status updates
     */
    onDocumentStatus(callback: DocumentStatusCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('document_status', callback);
    }

    /**
     * Listen for workspace status updates
     */
    onWorkspaceStatus(callback: WorkspaceStatusCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('workspace_status', callback);
    }

    /**
     * Listen for subscription confirmation
     */
    onSubscribed(callback: SubscribedCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('subscribed', callback);
    }

    /**
     * Listen for chats no context found events
     */
    onChatNoContextFound(callback: ChatNoContextFoundCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('chats.no_context_found', callback);
    }

    /**
     * Listen for Wikipedia fetch status updates
     */
    onWikipediaFetchStatus(callback: WikipediaFetchStatusCallback): void {
        if (!this.socket) {
            throw new Error('Socket not connected. Call connect() first.');
        }
        this.socket.on('wikipedia_fetch_status', callback);
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

    /**
     * Emit an event to the server
     */
    emit(event: string, data?: unknown): void {
        if (this.socket) {
            this.socket.emit(event, data);
        }
    }

    /**
     * Listen for a generic event
     */
    on(event: string, callback: (...args: unknown[]) => void): void {
        if (this.socket) {
            this.socket.on(event, callback);
        }
    }
}

export const socketService = new SocketService();
export default socketService;
