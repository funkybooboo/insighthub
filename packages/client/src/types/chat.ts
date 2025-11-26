/**
 * Chat types for multi-session management
 * Local implementation replacing shared package
 */

// Context chunk from RAG system
export interface Context {
    text: string;
    score: number;
    metadata: Record<string, unknown>;
}

// Chat message model
export interface ChatMessage {
    id: number;
    session_id: number;
    role: string;
    content: string;
    extra_metadata?: string | null;
    created_at: string;
    updated_at: string;
}

// Chat session model
export interface ChatSession {
    id: number;
    user_id: number;
    workspace_id: number | null;
    title: string | null;
    rag_type: string;
    created_at: string;
    updated_at: string;
}

// Client-specific extensions
export interface ChatState {
    sessions: ChatSession[];
    activeSessionId: string | null;
    isLoading: boolean;
    isTyping: boolean;
}
