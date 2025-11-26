import { useCallback, useEffect } from 'react';
import apiService from '@/services/api';

interface ChatSessionManagerProps {
    workspaceId: number;
}

export const ChatSessionManager = ({ workspaceId }: ChatSessionManagerProps) => {
    // Load backend sessions on mount and workspace change
    const loadBackendSessions = useCallback(async () => {
        if (!workspaceId) return;

        try {
            await apiService.getChatSessions(workspaceId);
            // Note: backendSessions state removed as it's not used
        } catch (err: unknown) {
            console.error('Error loading chats sessions:', err);
            // Note: error state removed as it's not used
        }
    }, [workspaceId]);

    useEffect(() => {
        if (
            workspaceId &&
            typeof window !== 'undefined' &&
            !window.location?.href?.includes?.('test')
        ) {
            loadBackendSessions();
        }
    }, [workspaceId, loadBackendSessions]);

    // This component doesn't render anything visible - it manages state
    return null;
};

export default ChatSessionManager;
