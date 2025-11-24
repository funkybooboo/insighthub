/**
 * Chat types for multi-session management
 */

export interface Context {
    text: string;
    score: number;
    metadata: Record<string, unknown>;
}

export interface Message {
    id: string;
    content: string;
    role: 'user' | 'bot';
    timestamp: number;
    context?: Context[]; // Added context field
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
