/**
 * Chat types for multi-session management
 * Re-exports shared types with client-specific extensions
 */

export { Context, ChatMessage as Message, ChatSession } from '@insighthub/shared-typescript';

// Client-specific extensions
export interface ChatState {
    sessions: ChatSession[];
    activeSessionId: string | null;
    isLoading: boolean;
    isTyping: boolean;
}
