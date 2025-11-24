import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { ChatSession, ChatState, Message, Context } from '@/types/chat';
import { chatStorage } from '@/lib/chatStorage';

// Generate a meaningful session title from the first message
function generateSessionTitle(message: string): string {
    // Clean up the message
    const cleaned = message.trim();

    // If it's a question, try to extract the key topic
    if (
        cleaned.toLowerCase().startsWith('what') ||
        cleaned.toLowerCase().startsWith('how') ||
        cleaned.toLowerCase().startsWith('why') ||
        cleaned.toLowerCase().startsWith('when') ||
        cleaned.toLowerCase().startsWith('where') ||
        cleaned.toLowerCase().startsWith('can you') ||
        cleaned.toLowerCase().startsWith('tell me')
    ) {
        // Take first 60 characters and ensure it ends at a word boundary
        let title = cleaned.slice(0, 60);
        const lastSpace = title.lastIndexOf(' ');
        if (lastSpace > 20) {
            // Only break at space if we have at least 20 chars
            title = title.slice(0, lastSpace);
        }

        // Capitalize first letter
        title = title.charAt(0).toUpperCase() + title.slice(1);

        return title + (cleaned.length > title.length ? '...' : '');
    }

    // For other types of messages, take the first meaningful part
    const words = cleaned.split(' ').filter((word) => word.length > 2);
    if (words.length >= 2) {
        const title = words.slice(0, 6).join(' '); // Take up to 6 meaningful words
        return title.length > 50 ? title.slice(0, 47) + '...' : title;
    }

    // Fallback to first part of message
    return cleaned.slice(0, 40) + (cleaned.length > 40 ? '...' : '');
}

const initialState: ChatState = {
    sessions: chatStorage.loadSessions(),
    activeSessionId: null,
    isLoading: false,
    isTyping: false,
};

const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        createSession: (state, action: PayloadAction<{ id: string; title?: string }>) => {
            const newSession: ChatSession = {
                id: action.payload.id,
                title: action.payload.title || 'New Chat',
                messages: [],
                createdAt: Date.now(),
                updatedAt: Date.now(),
            };
            state.sessions.unshift(newSession);
            state.activeSessionId = newSession.id;
            chatStorage.saveSessions(state.sessions);
        },
        setActiveSession: (state, action: PayloadAction<string>) => {
            state.activeSessionId = action.payload;
        },
        addMessageToSession: (
            state,
            action: PayloadAction<{ sessionId: string; message: Message }>
        ) => {
            const session = state.sessions.find((s) => s.id === action.payload.sessionId);
            if (session) {
                session.messages.push(action.payload.message);
                session.updatedAt = Date.now();

                // Auto-generate title from first user message
                if (session.title === 'New Chat' && action.payload.message.role === 'user') {
                    session.title = generateSessionTitle(action.payload.message.content);
                }

                chatStorage.saveSessions(state.sessions);
            }
        },
        updateMessageInSession: (
            state,
            action: PayloadAction<{
                sessionId: string;
                messageId: string;
                content?: string;
                context?: Context[]; // Added optional context field
            }>
        ) => {
            const session = state.sessions.find((s) => s.id === action.payload.sessionId);
            if (session) {
                const message = session.messages.find((m) => m.id === action.payload.messageId);
                if (message) {
                    if (action.payload.content !== undefined) {
                        message.content = action.payload.content;
                    }
                    if (action.payload.context !== undefined) {
                        message.context = action.payload.context;
                    }
                    session.updatedAt = Date.now();
                    chatStorage.saveSessions(state.sessions);
                }
            }
        },
        setSessionBackendId: (
            state,
            action: PayloadAction<{ sessionId: string; backendSessionId: number }>
        ) => {
            const session = state.sessions.find((s) => s.id === action.payload.sessionId);
            if (session) {
                session.sessionId = action.payload.backendSessionId;
                chatStorage.saveSessions(state.sessions);
            }
        },
        deleteSession: (state, action: PayloadAction<string>) => {
            state.sessions = state.sessions.filter((s) => s.id !== action.payload);
            if (state.activeSessionId === action.payload) {
                state.activeSessionId = state.sessions.length > 0 ? state.sessions[0].id : null;
            }
            chatStorage.saveSessions(state.sessions);
        },
        setLoading: (state, action: PayloadAction<boolean>) => {
            state.isLoading = action.payload;
        },
        setTyping: (state, action: PayloadAction<boolean>) => {
            state.isTyping = action.payload;
        },
        clearAllSessions: (state) => {
            state.sessions = [];
            state.activeSessionId = null;
            chatStorage.clearSessions();
        },
    },
});

export const {
    createSession,
    setActiveSession,
    addMessageToSession,
    updateMessageInSession,
    setSessionBackendId,
    deleteSession,
    setLoading,
    setTyping,
    clearAllSessions,
} = chatSlice.actions;
export default chatSlice.reducer;
