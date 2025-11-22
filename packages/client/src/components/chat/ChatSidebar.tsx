import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '@/store';
import { createSession, setActiveSession, deleteSession } from '@/store/slices/chatSlice';
import { ConfirmDialog } from '@/components/shared';

const ChatSidebar = () => {
    const dispatch = useDispatch();
    const { sessions, activeSessionId } = useSelector((state: RootState) => state.chat);
    const [deleteConfirm, setDeleteConfirm] = useState<{
        isOpen: boolean;
        sessionId: string | null;
    }>({
        isOpen: false,
        sessionId: null,
    });

    const handleNewChat = () => {
        const newSessionId = `session-${Date.now()}`;
        dispatch(createSession({ id: newSessionId }));
    };

    const handleSelectSession = (sessionId: string) => {
        dispatch(setActiveSession(sessionId));
    };

    const handleDeleteClick = (sessionId: string, event: React.MouseEvent) => {
        event.stopPropagation();
        setDeleteConfirm({ isOpen: true, sessionId });
    };

    const handleConfirmDelete = () => {
        if (deleteConfirm.sessionId) {
            dispatch(deleteSession(deleteConfirm.sessionId));
        }
        setDeleteConfirm({ isOpen: false, sessionId: null });
    };

    const handleCancelDelete = () => {
        setDeleteConfirm({ isOpen: false, sessionId: null });
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

    return (
        <div className="w-64 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex flex-col h-full">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <button
                    onClick={handleNewChat}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 4v16m8-8H4"
                        />
                    </svg>
                    New Chat
                </button>
            </div>

            {/* Chat Sessions List */}
            <div className="flex-1 overflow-y-auto">
                {sessions.length === 0 ? (
                    <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                        <svg
                            className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-2"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                            />
                        </svg>
                        <p className="text-sm">No chats yet</p>
                        <p className="text-xs mt-1">Click New Chat to start</p>
                    </div>
                ) : (
                    <div className="p-2">
                        {sessions.map((session) => (
                            <div
                                key={session.id}
                                onClick={() => handleSelectSession(session.id)}
                                className={`group relative p-3 mb-2 rounded-lg cursor-pointer transition-colors ${
                                    activeSessionId === session.id
                                        ? 'bg-blue-100 dark:bg-blue-900/30 border border-blue-300 dark:border-blue-700'
                                        : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700'
                                }`}
                            >
                                <div className="flex items-start justify-between gap-2">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2 mb-1">
                                            <svg
                                                className={`w-4 h-4 flex-shrink-0 ${
                                                    activeSessionId === session.id
                                                        ? 'text-blue-600 dark:text-blue-400'
                                                        : 'text-gray-400 dark:text-gray-500'
                                                }`}
                                                fill="none"
                                                viewBox="0 0 24 24"
                                                stroke="currentColor"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth={2}
                                                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                                                />
                                            </svg>
                                            <h3
                                                className={`text-sm font-medium truncate ${
                                                    activeSessionId === session.id
                                                        ? 'text-blue-900 dark:text-blue-200'
                                                        : 'text-gray-900 dark:text-gray-100'
                                                }`}
                                            >
                                                {session.title}
                                            </h3>
                                        </div>
                                        <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                                            <span>{session.messages.length} messages</span>
                                            <span>•</span>
                                            <span>{formatDate(session.updatedAt)}</span>
                                        </div>
                                    </div>
                                    <button
                                        onClick={(e) => handleDeleteClick(session.id, e)}
                                        className="opacity-0 group-hover:opacity-100 p-1 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-opacity"
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
            </div>

            {/* Footer */}
            <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                    {sessions.length} {sessions.length === 1 ? 'chat' : 'chats'} saved locally
                </div>
            </div>

            {/* Delete Confirmation Dialog */}
            <ConfirmDialog
                isOpen={deleteConfirm.isOpen}
                title="Delete Chat"
                message="Are you sure you want to delete this chat? This action cannot be undone."
                confirmLabel="Delete"
                variant="danger"
                onConfirm={handleConfirmDelete}
                onCancel={handleCancelDelete}
            />
        </div>
    );
};

export default ChatSidebar;
