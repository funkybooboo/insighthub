import React, { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { FaPlus, FaRegComments } from 'react-icons/fa';
import type { RootState } from '@/store';
import { createSession, setActiveSession, deleteSession } from '@/store/slices/chatSlice';
import { ConfirmDialog, LoadingSpinner } from '@/components/shared';
import { AxiosError } from 'axios';
import apiService from '@/services/api';

const ChatSessionList: React.FC = () => {
    const dispatch = useDispatch();
    const { sessions, activeSessionId } = useSelector((state: RootState) => state.chat);
    const { activeWorkspaceId } = useSelector((state: RootState) => state.workspace);
    const [deleteConfirm, setDeleteConfirm] = useState<{
        isOpen: boolean;
        sessionId: string | null;
        sessionTitle: string;
    }>({
        isOpen: false,
        sessionId: null,
        sessionTitle: '',
    });
    const [loadingSessions, setLoadingSessions] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch sessions from backend if they are not already loaded (e.g. initial load)
    useEffect(() => {
        if (activeWorkspaceId && sessions.length === 0) {
            // Placeholder: In a real app, you might fetch sessions associated with the workspace
            // For now, we rely on chatSlice to manage local sessions
            setLoadingSessions(false);
        } else {
            setLoadingSessions(false); // If sessions are loaded or no workspace, stop loading
        }
    }, [activeWorkspaceId, sessions.length]);

    const handleNewChat = () => {
        if (!activeWorkspaceId) return;
        const newSessionId = `session-${Date.now()}`;
        dispatch(createSession({ id: newSessionId }));
    };

    const handleSelectSession = (sessionId: string) => {
        dispatch(setActiveSession(sessionId));
    };

    const handleDeleteClick = (sessionId: string, sessionTitle: string, event: React.MouseEvent) => {
        event.stopPropagation();
        setDeleteConfirm({ isOpen: true, sessionId, sessionTitle });
    };

    const handleConfirmDelete = () => {
        if (deleteConfirm.sessionId) {
            dispatch(deleteSession(deleteConfirm.sessionId));
        }
        setDeleteConfirm({ isOpen: false, sessionId: null, sessionTitle: '' });
    };

    const handleCancelDelete = () => {
        setDeleteConfirm({ isOpen: false, sessionId: null, sessionTitle: '' });
    };

    const formatDate = (timestamp: number): string => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;

        return date.toLocaleDateString();
    };

    if (loadingSessions) {
        return (
            <div className="flex-1 flex items-center justify-center">
                <LoadingSpinner size="md" />
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full">
            {/* Header / New Chat Button */}
            <div className="p-5 border-b border-gray-200/80 dark:border-gray-800">
                <button
                    onClick={handleNewChat}
                    disabled={!activeWorkspaceId}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-sm"
                    title={!activeWorkspaceId ? 'Select a workspace first' : 'Create new chat'}
                >
                    <FaPlus className="w-5 h-5" />
                    New Chat
                </button>
                {!activeWorkspaceId && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 text-center mt-2">
                        Select or create a workspace to start chatting
                    </p>
                )}
            </div>

            {/* Chat Sessions List */}
            <div className="flex-1 overflow-y-auto p-3">
                {sessions.length === 0 && activeWorkspaceId ? (
                    <div className="flex flex-col items-center justify-center h-full text-center px-4 text-gray-500 dark:text-gray-400">
                        <FaRegComments className="w-12 h-12 mb-3 text-gray-400 dark:text-gray-500" />
                        <p className="text-sm font-medium">No chats yet</p>
                        <p className="text-xs mt-1">Start a new conversation</p>
                    </div>
                ) : (
                    <div className="space-y-1">
                        {sessions.map((session) => (
                            <div
                                key={session.id}
                                onClick={() => handleSelectSession(session.id)}
                                className={`group relative px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                                    activeSessionId === session.id
                                        ? 'bg-blue-50 dark:bg-blue-900/20'
                                        : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
                                }`}
                            >
                                <div className="flex items-center justify-between gap-2">
                                    <div className="flex-1 min-w-0">
                                        <h3
                                            className={`text-sm font-medium truncate ${
                                                activeSessionId === session.id
                                                    ? 'text-blue-700 dark:text-blue-300'
                                                    : 'text-gray-700 dark:text-gray-200'
                                            }`}
                                        >
                                            {session.title}
                                        </h3>
                                        <div className="flex items-center gap-1.5 mt-0.5 text-xs text-gray-400 dark:text-gray-500">
                                            <span>{session.messages.length} messages</span>
                                            <span className="text-gray-300 dark:text-gray-600">
                                                |
                                            </span>
                                            <span>{formatDate(session.updatedAt)}</span>
                                        </div>
                                    </div>
                                    <button
                                        onClick={(e) => handleDeleteClick(session.id, session.title, e)}
                                        className="opacity-0 group-hover:opacity-100 p-1.5 text-gray-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
                                        title="Delete chat"
                                    >
                                        <svg
                                            className="w-4 h-4"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                        >
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
                {!activeWorkspaceId && (
                    <div className="flex flex-col items-center justify-center h-full text-center px-4 text-gray-500 dark:text-gray-400">
                        <FaFolderOpen className="w-12 h-12 mb-3 text-gray-400 dark:text-gray-500" />
                        <p className="text-sm font-medium">No active workspace</p>
                        <p className="text-xs mt-1">Select or create a workspace to manage chats.</p>
                    </div>
                )}
            </div>

            {/* Delete Confirmation Dialog */}
            <ConfirmDialog
                isOpen={deleteConfirm.isOpen}
                title="Delete Chat"
                message={`Are you sure you want to delete "${deleteConfirm.sessionTitle}"? This action cannot be undone.`}
                confirmLabel="Delete"
                variant="danger"
                onConfirm={handleConfirmDelete}
                onCancel={handleCancelDelete}
            />
        </div>
    );
};

export default ChatSessionList;
