import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { socket } from '../services/socket';
import type { RootState } from '../store';
import { updateDocumentStatus, updateWorkspaceStatus } from '../store/slices/statusSlice';

interface DocumentStatusUpdate {
    document_id: number;
    user_id: number;
    workspace_id: number | null;
    status: 'pending' | 'processing' | 'ready' | 'failed';
    error: string | null;
    chunk_count: number | null;
    filename: string;
    metadata: Record<string, any>;
}

interface WorkspaceStatusUpdate {
    workspace_id: number;
    user_id: number;
    status: 'provisioning' | 'ready' | 'error';
    message: string | null;
    name: string;
    metadata: Record<string, any>;
}

/**
 * Hook to subscribe to real-time status updates via WebSocket.
 * 
 * Automatically subscribes when user is authenticated and updates Redux store
 * when status updates are received.
 */
export function useStatusUpdates() {
    const dispatch = useDispatch();
    const { user } = useSelector((state: RootState) => state.auth);

    useEffect(() => {
        if (!user || !socket.connected) {
            return;
        }

        // Subscribe to status updates for this user
        socket.emit('subscribe_status', { user_id: user.id });

        // Listen for document status updates
        const handleDocumentStatus = (data: DocumentStatusUpdate) => {
            console.log('Document status update:', data);
            dispatch(updateDocumentStatus(data));
        };

        // Listen for workspace status updates
        const handleWorkspaceStatus = (data: WorkspaceStatusUpdate) => {
            console.log('Workspace status update:', data);
            dispatch(updateWorkspaceStatus(data));
        };

        // Listen for subscription confirmation
        const handleSubscribed = (data: { user_id: number; room: string }) => {
            console.log('Subscribed to status updates:', data);
        };

        socket.on('document_status', handleDocumentStatus);
        socket.on('workspace_status', handleWorkspaceStatus);
        socket.on('subscribed', handleSubscribed);

        return () => {
            socket.off('document_status', handleDocumentStatus);
            socket.off('workspace_status', handleWorkspaceStatus);
            socket.off('subscribed', handleSubscribed);
        };
    }, [user, dispatch]);
}
