import { useCallback, useEffect } from 'react';
import apiService from '@/services/api';
import { logger } from '@/lib/logger';

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
            logger.error('Error loading chat sessions', err as Error, {
                workspaceId,
            });
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
