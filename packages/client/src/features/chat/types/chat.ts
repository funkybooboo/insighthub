/**
 * Chat types for multi-session management
 */

export interface Message {
    id: string;
    content: string;
    role: 'user' | 'bot';
    timestamp: number;
}

export interface ChatSession {
    id: string;
    title: string;
    messages: Message[];
    createdAt: number;
    updatedAt: number;
    sessionId?: number; // Backend session ID
}

export interface ChatState {
    sessions: ChatSession[];
    activeSessionId: string | null;
    isLoading: boolean;
    isTyping: boolean;
}
