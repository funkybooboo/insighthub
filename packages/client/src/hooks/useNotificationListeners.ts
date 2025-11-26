import { useEffect } from 'react';
import { useNotifications } from '../contexts/NotificationContext';
import socketService from '../services/socket';
import type {
    DocumentStatusData,
    WorkspaceStatusData,
    WikipediaFetchStatusData,
    ChatCompleteData,
    ErrorData,
    ChatNoContextFoundData,
} from '../services/socket';

export const useNotificationListeners = () => {
    const { addNotification } = useNotifications();

    useEffect(() => {
        // Document status updates
        const handleDocumentStatus = (data: DocumentStatusData) => {
            const { status, message, error } = data;

            switch (status) {
                case 'processing':
                    addNotification({
                        type: 'info',
                        title: 'Document Processing',
                        message: message || 'Your document is being processed...',
                        duration: 3000,
                    });
                    break;
                case 'ready':
                    addNotification({
                        type: 'success',
                        title: 'Document Ready',
                        message: message || 'Your document has been processed successfully!',
                        duration: 5000,
                    });
                    break;
                case 'deleting':
                    addNotification({
                        type: 'info',
                        title: 'Document Deleting',
                        message: message || 'Your document is being deleted...',
                        duration: 3000,
                    });
                    break;
                case 'deleted':
                    addNotification({
                        type: 'success',
                        title: 'Document Deleted',
                        message: message || 'Your document has been deleted successfully!',
                        duration: 3000,
                    });
                    break;
                case 'failed':
                    addNotification({
                        type: 'error',
                        title: 'Document Operation Failed',
                        message:
                            error || message || 'Failed to process document. Please try again.',
                        persistent: true,
                    });
                    break;
            }
        };

        // Workspace status updates
        const handleWorkspaceStatus = (data: WorkspaceStatusData) => {
            const { status, message, error } = data;

            switch (status) {
                case 'provisioning':
                    addNotification({
                        type: 'info',
                        title: 'Workspace Setup',
                        message: message || 'Setting up your workspace...',
                        duration: 3000,
                    });
                    break;
                case 'ready':
                    addNotification({
                        type: 'success',
                        title: 'Workspace Ready',
                        message: message || 'Your workspace is ready to use!',
                        duration: 5000,
                    });
                    break;
                case 'deleting':
                    addNotification({
                        type: 'info',
                        title: 'Workspace Deleting',
                        message: message || 'Deleting your workspace...',
                        duration: 3000,
                    });
                    break;
                case 'deleted':
                    addNotification({
                        type: 'success',
                        title: 'Workspace Deleted',
                        message: message || 'Your workspace has been deleted successfully!',
                        duration: 3000,
                    });
                    break;
                case 'failed':
                    addNotification({
                        type: 'error',
                        title: 'Workspace Operation Failed',
                        message:
                            error || message || 'Failed to process workspace. Please try again.',
                        persistent: true,
                    });
                    break;
            }
        };

        // Wikipedia fetch status updates
        const handleWikipediaFetchStatus = (data: WikipediaFetchStatusData) => {
            const { status, message, query } = data;

            switch (status) {
                case 'fetching':
                    addNotification({
                        type: 'info',
                        title: 'Fetching Wikipedia Data',
                        message: `Searching Wikipedia for: "${query}"`,
                        duration: 3000,
                    });
                    break;
                case 'processing':
                    addNotification({
                        type: 'info',
                        title: 'Processing Wikipedia Data',
                        message: 'Analyzing and processing fetched content...',
                        duration: 3000,
                    });
                    break;
                case 'completed':
                    addNotification({
                        type: 'success',
                        title: 'Wikipedia Data Added',
                        message: message || 'Wikipedia content has been added to your workspace!',
                        duration: 5000,
                    });
                    break;
                case 'failed':
                    addNotification({
                        type: 'warning',
                        title: 'Wikipedia Fetch Failed',
                        message:
                            message ||
                            'Could not fetch Wikipedia data. Continuing with available context.',
                        duration: 5000,
                    });
                    break;
            }
        };

        // Chat completion notifications
        const handleChatComplete = (data: ChatCompleteData) => {
            if (data.context && data.context.length > 0) {
                addNotification({
                    type: 'success',
                    title: 'Response Generated',
                    message: `Found ${data.context.length} relevant context snippets for your query.`,
                    duration: 3000,
                });
            }
        };

        // Error notifications
        const handleError = (data: ErrorData) => {
            addNotification({
                type: 'error',
                title: 'Error',
                message: data.error,
                persistent: true,
            });
        };

        // No context found notifications
        const handleNoContextFound = (_data: ChatNoContextFoundData) => {
            addNotification({
                type: 'info',
                title: 'No Context Found',
                message: 'No relevant documents found. You can fetch from Wikipedia if needed.',
                duration: 4000,
            });
        };

        // Connection status monitoring
        const handleConnected = () => {
            addNotification({
                type: 'success',
                title: 'Connected',
                message: 'Successfully connected to the server.',
                duration: 3000,
            });
        };

        const handleDisconnected = () => {
            addNotification({
                type: 'error',
                title: 'Connection Lost',
                message: 'Lost connection to the server. Attempting to reconnect...',
                persistent: true,
            });
        };

        // Register all event listeners
        socketService.onDocumentStatus(handleDocumentStatus);
        socketService.onWorkspaceStatus(handleWorkspaceStatus);
        socketService.onWikipediaFetchStatus(handleWikipediaFetchStatus);
        socketService.onChatComplete(handleChatComplete);
        socketService.onError(handleError);
        socketService.onChatNoContextFound(handleNoContextFound);
        socketService.onConnected(handleConnected);
        socketService.onDisconnected(handleDisconnected);

        // Cleanup function
        return () => {
            socketService.off('document_status', handleDocumentStatus as (...args: unknown[]) => void);
            socketService.off('workspace_status', handleWorkspaceStatus as (...args: unknown[]) => void);
            socketService.off('wikipedia_fetch_status', handleWikipediaFetchStatus as (...args: unknown[]) => void);
            socketService.off('chat_complete', handleChatComplete as (...args: unknown[]) => void);
            socketService.off('error', handleError as (...args: unknown[]) => void);
            socketService.off('chats.no_context_found', handleNoContextFound as (...args: unknown[]) => void);
            socketService.off('connected', handleConnected as (...args: unknown[]) => void);
            socketService.off('disconnect', handleDisconnected as (...args: unknown[]) => void);
        };
    }, [addNotification]);
};
