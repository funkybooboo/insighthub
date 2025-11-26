import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import socketService from '../services/socket';
import type { RootState } from '../store';
import { updateDocumentStatus, updateWorkspaceStatus } from '../store/slices/statusSlice';
import { logger } from '../lib/logger';

interface DocumentStatusUpdate {
    document_id: number;
    user_id: number;
    workspace_id: number | null;
    status: 'pending' | 'parsing' | 'chunking' | 'embedding' | 'indexing' | 'ready' | 'failed' | 'processing' | 'deleting' | 'deleted';
    error: string | null;
    chunk_count: number | null;
    filename: string;
    metadata?: Record<string, unknown>;
    progress?: number;
    message?: string;
}

interface WorkspaceStatusUpdate {
    workspace_id: number;
    user_id: number;
    status: 'provisioning' | 'ready' | 'failed' | 'deleting' | 'deleted';
    message: string | null;
    name?: string;
    metadata?: Record<string, unknown>;
}

/**
 * Hook to subscribe to real-time status updates via WebSocket.
 *
 * Automatically subscribes when users is authenticated and updates Redux store
 * when status updates are received.
 */
export function useStatusUpdates() {
    const dispatch = useDispatch();
    const { user } = useSelector((state: RootState) => state.auth);

    useEffect(() => {
        if (!user) {
            return;
        }

        // Connect socket if not already connected
        if (!socketService.isConnected()) {
            socketService.connect();
        }

        // Wait a bit for connection to establish, then subscribe
        const subscribeTimeout = setTimeout(() => {
            if (socketService.isConnected()) {
                socketService.emit('subscribe_status', { user_id: user.id });
            }
        }, 100);

        // Listen for document status updates
        const handleDocumentStatus = (data: unknown) => {
            const update = data as DocumentStatusUpdate;
            logger.debug('Document status update received', {
                documentId: update.document_id,
                workspaceId: update.workspace_id,
                status: update.status,
                filename: update.filename,
            });
            dispatch(updateDocumentStatus(update));
        };

        // Listen for workspace status updates
        const handleWorkspaceStatus = (data: unknown) => {
            const update = data as WorkspaceStatusUpdate;
            logger.debug('Workspace status update received', {
                workspaceId: update.workspace_id,
                status: update.status,
                message: update.message,
            });
            dispatch(updateWorkspaceStatus(update));
        };

        // Listen for subscription confirmation
        const handleSubscribed = (data: unknown) => {
            const subscribed = data as { user_id: number; room: string };
            logger.info('Subscribed to status updates', {
                userId: subscribed.user_id,
                room: subscribed.room,
            });
        };

        socketService.on('document_status', handleDocumentStatus);
        socketService.on('workspace_status', handleWorkspaceStatus);
        socketService.on('subscribed', handleSubscribed);

        return () => {
            clearTimeout(subscribeTimeout);
            socketService.off('document_status', handleDocumentStatus);
            socketService.off('workspace_status', handleWorkspaceStatus);
            socketService.off('subscribed', handleSubscribed);
        };
    }, [user, dispatch]);
}
