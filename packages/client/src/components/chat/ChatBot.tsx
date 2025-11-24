import { useEffect, useRef, useState, useCallback } from 'react'; // Added useCallback
import { useDispatch, useSelector } from 'react-redux';

import type { RootState } from '@/store';
import {
    createSession,
    addMessageToSession,
    updateMessageInSession,
    setSessionBackendId,
    setActiveSession,
    setTyping,
} from '@/store/slices/chatSlice';
import { selectIsWorkspaceProcessing } from '@/store/slices/statusSlice'; // Import the new selector
import type { Message } from '@/types/chat';
import ChatMessages from './ChatMessages';
import ChatInput, { type ChatFormData } from './ChatInput';
// DocumentManager is now handled in Layout.tsx
import socketService from '@/services/socket';
import apiService from '@/services/api';

import popSound from '@/assets/sounds/pop.mp3';
import notificationSound from '@/assets/sounds/notification.mp3';

const popAudio = new Audio(popSound);
popAudio.volume = 0.2;

const notificationAudio = new Audio(notificationSound);
notificationAudio.volume = 0.2;

const ChatBot = () => {
    const dispatch = useDispatch();
    const { sessions, activeSessionId, isTyping } = useSelector((state: RootState) => state.chat);
    const { activeWorkspaceId } = useSelector((state: RootState) => state.workspace);
    const isWorkspaceProcessing = useSelector(selectIsWorkspaceProcessing(activeWorkspaceId || -1)); // Check processing status
    const [isBotTyping, setIsBotTyping] = useState(false);
    const [error, setError] = useState('');
    const currentBotMessageId = useRef<string | null>(null);
    const currentBotMessage = useRef<string>('');
    const lastUserQuery = useRef<string>(''); // To store the last user query for retries

    // Get active session
    const activeSession = sessions.find((s) => s.id === activeSessionId);

    // Create initial session if none exists
    useEffect(() => {
        if (!activeWorkspaceId) return;
        if (!activeSessionId && sessions.length === 0) {
            const newSessionId = `session-${Date.now()}`;
            dispatch(createSession({ id: newSessionId }));
        } else if (!activeSessionId && sessions.length > 0) {
            // Set the first session as active if there's no active session
            dispatch(setActiveSession(sessions[0].id));
        }
    }, [activeWorkspaceId, sessions, dispatch, activeSessionId]);

    // Load documents on mount (this component no longer directly renders DocumentManager)
    useEffect(() => {
        if (!activeWorkspaceId) return;
        const loadDocuments = async () => {
            try {
                // We don't need to await this to block chat, just ensure it's triggered
                apiService.listDocuments(activeWorkspaceId);
            } catch (error) {
                console.error('Error loading documents on mount:', error);
            }
        };

        loadDocuments();
    }, [activeWorkspaceId]);

    const onSubmit = useCallback(
        async ({ prompt }: ChatFormData) => {
            if (!activeSessionId || !activeWorkspaceId) {
                console.error('No active session or workspace');
                return;
            }

            try {
                setError('');

                // Store last user query for potential RAG enhancement
                lastUserQuery.current = prompt;

                // Add user message to session
                const userMessage: Message = {
                    id: `msg-${Date.now()}`,
                    content: prompt,
                    role: 'user',
                    timestamp: Date.now(),
                };
                dispatch(
                    addMessageToSession({
                        sessionId: activeSessionId,
                        message: userMessage,
                    })
                );

                // Reset current bot message buffer
                currentBotMessage.current = '';
                currentBotMessageId.current = null;

                // Set typing indicator
                setIsBotTyping(true);
                dispatch(setTyping(true));

                // Play pop sound
                popAudio.play();

                // Send message via socket
                socketService.sendMessage({
                    message: prompt,
                    session_id: activeSession?.sessionId,
                    workspace_id: activeWorkspaceId,
                });
            } catch (error) {
                console.error('Error sending message:', error);
                setError('Something went wrong, try again!');
                setIsBotTyping(false);
                dispatch(setTyping(false));
            }
        },
        [activeSessionId, activeWorkspaceId, activeSession?.sessionId, dispatch],
    );

    useEffect(() => {
        if (!activeWorkspaceId) return;

        // Connect to socket on mount
        socketService.connect();

        // Set up event listeners
        socketService.onConnected(() => {
            console.log('Connected to chat server');
        });

        socketService.onChatChunk((data) => {
            if (!activeSessionId) return;

            // Append chunk to current bot message
            currentBotMessage.current += data.chunk;

            // Stop typing indicator on first chunk, but keep isTyping true for cancel button
            setIsBotTyping(false);

            // Create or update bot message in session
            if (currentBotMessageId.current) {
                dispatch(
                    updateMessageInSession({
                        sessionId: activeSessionId,
                        messageId: currentBotMessageId.current,
                        content: currentBotMessage.current,
                    })
                );
            } else {
                // First chunk - add new bot message
                currentBotMessageId.current = `msg-${Date.now()}`;
                const botMessage: Message = {
                    id: currentBotMessageId.current,
                    content: currentBotMessage.current,
                    role: 'bot',
                    timestamp: Date.now(),
                };
                dispatch(
                    addMessageToSession({
                        sessionId: activeSessionId,
                        message: botMessage,
                    })
                );
            }
        });

        socketService.onChatComplete((data) => {
            if (!activeSessionId) return;

            // Store backend session_id in Redux
            dispatch(
                setSessionBackendId({
                    sessionId: activeSessionId,
                    backendSessionId: data.session_id,
                })
            );

            // Update the bot message with the full response and context
            if (currentBotMessageId.current) {
                dispatch(
                    updateMessageInSession({
                        sessionId: activeSessionId,
                        messageId: currentBotMessageId.current,
                        content: data.full_response, // Ensure final content is stored
                        context: data.context, // Store context with the message
                    })
                );
            }

            // Reset current message buffer
            currentBotMessage.current = '';
            currentBotMessageId.current = null;

            // Stop typing indicator
            setIsBotTyping(false);
            dispatch(setTyping(false));

            // Play notification sound
            notificationAudio.play();
        });

        socketService.onChatCancelled(() => {
            if (!activeSessionId) return;

            console.log('Chat stream cancelled by user');

            // Reset current message buffer
            currentBotMessage.current = '';
            currentBotMessageId.current = null;

            // Stop typing indicator
            setIsBotTyping(false);
            dispatch(setTyping(false));
        });

        socketService.onError((data) => {
            console.error('Socket error:', data.error);
            setError(data.error);
            setIsBotTyping(false);
            dispatch(setTyping(false));
            currentBotMessage.current = '';
            currentBotMessageId.current = null;
        });

        socketService.onDisconnected(() => {
            console.log('Disconnected from chat server');
        });

        // Cleanup on unmount
        return () => {
            socketService.removeAllListeners();
            socketService.disconnect();
        };
    }, [activeSessionId, activeWorkspaceId, dispatch]);

    const onCancel = () => {
        try {
            // Cancel the current message
            socketService.cancelMessage();

            // Reset state
            setIsBotTyping(false);
            dispatch(setTyping(false));
            currentBotMessage.current = '';
            currentBotMessageId.current = null;

            console.log('Message cancelled');
        } catch (error) {
            console.error('Error cancelling message:', error);
        }
    };

    const handleFetchWikipedia = async (query: string) => {
        if (!activeWorkspaceId || !activeSessionId) return;

        setError('');
        setIsBotTyping(true);
        dispatch(setTyping(true));
        // Add a message indicating Wikipedia fetch initiated
        dispatch(addMessageToSession({
            sessionId: activeSessionId,
            message: {
                id: `msg-${Date.now()}`,
                content: `Searching Wikipedia for "${query}"...`,
                role: 'bot',
                timestamp: Date.now(),
            },
        }));

        try {
            await apiService.fetchWikipediaArticle(activeWorkspaceId, query);
            // After successful fetch, retry the original query
            // The document processing status will be updated via sockets.
            // When processing completes, isWorkspaceProcessing will become false,
            // and then we can automatically re-submit the query.
            dispatch(addMessageToSession({
                sessionId: activeSessionId,
                message: {
                    id: `msg-${Date.now() + 1}`,
                    content: 'Wikipedia article fetched and processing. Retrying your query shortly...',
                    role: 'bot',
                    timestamp: Date.now(),
                },
            }));
            // Actual re-submission will be handled by a useEffect watching isWorkspaceProcessing
        } catch (err: any) {
            const message = err.response?.data?.detail || 'Failed to fetch Wikipedia article.';
            setError(message);
            dispatch(addMessageToSession({
                sessionId: activeSessionId,
                message: {
                    id: `msg-${Date.now() + 1}`,
                    content: `Error fetching Wikipedia article: ${message}`,
                    role: 'bot',
                    timestamp: Date.now(),
                },
            }));
            setIsBotTyping(false);
            dispatch(setTyping(false));
        }
    };

    const handleUploadDocument = () => {
        if (!activeWorkspaceId || !activeSessionId) return;
        dispatch(addMessageToSession({
            sessionId: activeSessionId,
            message: {
                id: `msg-${Date.now()}`,
                content: `Please use the "Documents" panel on the right to upload your document. Once uploaded, your previous query will be retried automatically after processing completes.`,
                role: 'bot',
                timestamp: Date.now(),
            },
        }));
        // Logic to visually indicate the document panel might be needed here.
        // For now, simple instruction.
    };

    const handleContinueChat = () => {
        if (lastUserQuery.current) {
            onSubmit({ prompt: lastUserQuery.current });
            lastUserQuery.current = ''; // Clear after use
        }
    };

    // Effect to retry query after RAG enhancement completes
    useEffect(() => {
        // Only retry if there's a last query, workspace is no longer processing, and bot isn't typing
        if (activeWorkspaceId && lastUserQuery.current && !isWorkspaceProcessing && !isBotTyping) {
            console.log("RAG enhancement complete, retrying last query:", lastUserQuery.current);
            const queryToRetry = lastUserQuery.current;
            lastUserQuery.current = ''; // Clear immediately to prevent re-triggering
            onSubmit({ prompt: queryToRetry });
        }
    }, [isWorkspaceProcessing, activeWorkspaceId, isBotTyping, dispatch, onSubmit]); // Added onSubmit to dependency array


    // Convert Message[] to the format expected by ChatMessages component
    const messages =
        activeSession?.messages.map((msg) => ({
            id: msg.id,
            content: msg.content,
            role: msg.role,
            timestamp: msg.timestamp,
            context: msg.context, // Ensure context is passed
        })) || [];

    // Show message if no workspace is selected
    if (!activeWorkspaceId) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400">
                <p className="text-lg">Please create or select a workspace to start chatting</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-white dark:bg-gray-900">
            {/* DocumentManager is now rendered in Layout.tsx */}
            <ChatMessages
                messages={messages}
                error={error}
                isBotTyping={isBotTyping}
                onUploadDocument={handleUploadDocument}
                onFetchWikipedia={handleFetchWikipedia}
                onContinueChat={handleContinueChat}
            />
            {isWorkspaceProcessing ? (
                <div className="p-4 bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-200 text-center flex items-center justify-center">
                    <LoadingSpinner size="sm" className="inline-block mr-2" />
                    Processing additional context. Chat will be enabled when complete.
                </div>
            ) : (
                <ChatInput onSubmit={onSubmit} onCancel={onCancel} isTyping={isTyping} />
            )}
        </div>
    );
};

export default ChatBot;
