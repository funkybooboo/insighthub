import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '@/store';
import { createSession, deleteSession, setActiveSession, setSessionBackendId } from '@/store/slices/chatSlice';
import apiService from '@/services/api';
import { LoadingSpinner } from '@/components/shared';

interface BackendChatSession {
    session_id: number;
    title: string;
    created_at: string;
    updated_at: string;
    message_count: number;
}

interface ChatSessionManagerProps {
    workspaceId: number;
}

export const ChatSessionManager = ({ workspaceId }: ChatSessionManagerProps) => {
    const dispatch = useDispatch();
    const { sessions, activeSessionId } = useSelector((state: RootState) => state.chat);
    const [backendSessions, setBackendSessions] = useState<BackendChatSession[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Load backend sessions on mount and workspace change
    useEffect(() => {
        if (workspaceId && typeof window !== 'undefined' && !window.location?.href?.includes?.('test')) {
            loadBackendSessions();
        }
    }, [workspaceId]);

    const loadBackendSessions = async () => {
        if (!workspaceId) return;

        setIsLoading(true);
        setError(null);

        try {
            const sessions = await apiService.getChatSessions(workspaceId);
            setBackendSessions(sessions);

            // Sync with local Redux state - create local sessions for backend sessions that don't exist locally
            sessions.forEach(backendSession => {
                const localSession = sessions.find(s => s.sessionId === backendSession.session_id);
                if (!localSession) {
                    // Create a local session representation
                    const localSessionId = `session-${backendSession.session_id}`;
                    dispatch(createSession({
                        id: localSessionId,
                        title: backendSession.title,
                        sessionId: backendSession.session_id
                    }));
                }
            });
        } catch (err: unknown) {
            console.error('Error loading chat sessions:', err);
            let errorMessage = 'Failed to load chat sessions';

            if (err && typeof err === 'object' && 'response' in err) {
                const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
                if (axiosError.response?.status === 401) {
                    errorMessage = 'Authentication failed. Please log in again.';
                } else if (axiosError.response?.status === 403) {
                    errorMessage = 'You do not have permission to access chat sessions in this workspace.';
                } else if (axiosError.response?.status === 404) {
                    errorMessage = 'Workspace not found.';
                } else if (axiosError.response?.data?.detail) {
                    errorMessage = axiosError.response.data.detail;
                }
            }

            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateSession = async (title?: string) => {
        if (!workspaceId) return;

        setIsLoading(true);
        setError(null);

        try {
            const result = await apiService.createChatSession(workspaceId, title);

            // Create local session
            const localSessionId = `session-${result.session_id}`;
            dispatch(createSession({
                id: localSessionId,
                title: result.title,
                sessionId: result.session_id
            }));

            // Set as active
            dispatch(setActiveSession(localSessionId));

            // Reload backend sessions
            await loadBackendSessions();
        } catch (err: unknown) {
            console.error('Error creating chat session:', err);
            let errorMessage = 'Failed to create chat session';

            if (err && typeof err === 'object' && 'response' in err) {
                const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
                if (axiosError.response?.status === 401) {
                    errorMessage = 'Authentication failed. Please log in again.';
                } else if (axiosError.response?.status === 403) {
                    errorMessage = 'You do not have permission to create chat sessions in this workspace.';
                } else if (axiosError.response?.status === 400) {
                    errorMessage = 'Invalid session title or workspace configuration.';
                } else if (axiosError.response?.data?.detail) {
                    errorMessage = axiosError.response.data.detail;
                }
            }

            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteSession = async (sessionId: number) => {
        if (!workspaceId) return;

        setIsLoading(true);
        setError(null);

        try {
            await apiService.deleteChatSession(workspaceId, sessionId);

            // Find and remove local session
            const localSession = sessions.find(s => s.sessionId === sessionId);
            if (localSession) {
                dispatch(deleteSession(localSession.id));
            }

            // Reload backend sessions
            await loadBackendSessions();
        } catch (err: unknown) {
            console.error('Error deleting chat session:', err);
            let errorMessage = 'Failed to delete chat session';

            if (err && typeof err === 'object' && 'response' in err) {
                const axiosError = err as { response?: { status?: number; data?: { detail?: string } } };
                if (axiosError.response?.status === 401) {
                    errorMessage = 'Authentication failed. Please log in again.';
                } else if (axiosError.response?.status === 403) {
                    errorMessage = 'You do not have permission to delete this chat session.';
                } else if (axiosError.response?.status === 404) {
                    errorMessage = 'Chat session not found.';
                } else if (axiosError.response?.data?.detail) {
                    errorMessage = axiosError.response.data.detail;
                }
            }

            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSelectSession = (sessionId: number) => {
        const localSession = sessions.find(s => s.sessionId === sessionId);
        if (localSession) {
            dispatch(setActiveSession(localSession.id));
        }
    };

    // This component doesn't render anything visible - it manages state
    return null;
};

export default ChatSessionManager;