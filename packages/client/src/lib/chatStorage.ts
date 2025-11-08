/**
 * LocalStorage utilities for chat session persistence
 */

import type { ChatSession } from '@/types/chat';

const STORAGE_KEY = 'insighthub_chat_sessions';

export const chatStorage = {
    /**
     * Load all chat sessions from localStorage
     */
    loadSessions(): ChatSession[] {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (!stored) return [];
            return JSON.parse(stored) as ChatSession[];
        } catch (error) {
            console.error('Error loading chat sessions:', error);
            return [];
        }
    },

    /**
     * Save all chat sessions to localStorage
     */
    saveSessions(sessions: ChatSession[]): void {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
        } catch (error) {
            console.error('Error saving chat sessions:', error);
        }
    },

    /**
     * Clear all chat sessions from localStorage
     */
    clearSessions(): void {
        try {
            localStorage.removeItem(STORAGE_KEY);
        } catch (error) {
            console.error('Error clearing chat sessions:', error);
        }
    },
};
