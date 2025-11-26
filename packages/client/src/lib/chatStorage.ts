/**
 * LocalStorage utilities for chats session persistence
 */

import type { ChatSession } from '@/types/chat';

const STORAGE_KEY = 'insighthub_chat_sessions';

export const chatStorage = {
    /**
     * Load all chats sessions from localStorage
     */
    loadSessions(): ChatSession[] {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (!stored) return [];
            return JSON.parse(stored) as ChatSession[];
        } catch (error) {
            console.error('Error loading chats sessions:', error);
            return [];
        }
    },

    /**
     * Save all chats sessions to localStorage
     */
    saveSessions(sessions: ChatSession[]): void {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
        } catch (error) {
            console.error('Error saving chats sessions:', error);
        }
    },

    /**
     * Clear all chats sessions from localStorage
     */
    clearSessions(): void {
        try {
            localStorage.removeItem(STORAGE_KEY);
        } catch (error) {
            console.error('Error clearing chats sessions:', error);
        }
    },
};
