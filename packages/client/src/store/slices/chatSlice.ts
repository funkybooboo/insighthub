import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { ChatSession, ChatState, Message, Context } from '@/types/chat';
import { chatStorage } from '@/lib/chatStorage';

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
                    session.title =
                        action.payload.message.content.slice(0, 50) +
                        (action.payload.message.content.length > 50 ? '...' : '');
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
