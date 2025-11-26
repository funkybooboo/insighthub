import { useEffect, useRef, useState, useCallback } from 'react'; // Added useCallback
import { useDispatch, useSelector } from 'react-redux';

import { logger } from '@/lib/logger';
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
import RAGEnhancementPrompt from './RAGEnhancementPrompt';
import ChatSessionManager from './ChatSessionManager';
import { LoadingSpinner } from '@/components/shared';
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
    const [showRAGPrompt, setShowRAGPrompt] = useState(false);
    const currentBotMessageId = useRef<string | null>(null);
    const currentBotMessage = useRef<string>('');
    const lastUserQuery = useRef<string>(''); // To store the last users query for retries

    // Get active session
    const activeSession = sessions.find((s) => s.id === activeSessionId);

    // Create initial session if none exists
    useEffect(() => {
        if (!activeWorkspaceId) return;

        const createInitialSession = async () => {
            if (!activeSessionId && sessions.length === 0) {
                try {
                    // Generate a title based on current time or use default
                    // Create backend session with generic title (will be updated with first message)
                    const result = await apiService.createChatSession(
                        activeWorkspaceId,
                        'New Chat'
                    );

                    // Create local session representation
                    const newSessionId = `session-${result.session_id}`;
                    dispatch(
                        createSession({
                            id: newSessionId,
                            title: result.title,
                            sessionId: result.session_id,
                        })
                    );

                    // Set as active
                    dispatch(setActiveSession(newSessionId));
                 } catch (error) {
                     logger.error('Error creating initial chat session', error as Error, {
                         workspaceId: activeWorkspaceId,
                     });
                     // Fallback to local session if backend fails
                    const newSessionId = `session-${Date.now()}`;
                    dispatch(createSession({ id: newSessionId }));
                }
            } else if (!activeSessionId && sessions.length > 0) {
                // Set the first session as active if there's no active session
                dispatch(setActiveSession(sessions[0].id));
            }
        };

        createInitialSession();
    }, [activeWorkspaceId, sessions, dispatch, activeSessionId]);

    // Load documents on mount (this component no longer directly renders DocumentManager)
    useEffect(() => {
        if (!activeWorkspaceId) return;
        const loadDocuments = async () => {
            try {
                // We don't need to await this to block chats, just ensure it's triggered
                apiService.listDocuments(activeWorkspaceId);
             } catch (error) {
                 logger.error('Error loading documents on mount', error as Error, {
                     workspaceId: activeWorkspaceId,
                 });
             }
        };

        loadDocuments();
    }, [activeWorkspaceId]);

    const onSubmit = useCallback(
        async ({ prompt }: ChatFormData, ignoreRag?: boolean) => {
             if (!activeSessionId || !activeWorkspaceId) {
                 logger.error('Cannot send message: No active session or workspace', undefined, {
                     activeSessionId,
                     activeWorkspaceId,
                 });
                 return;
             }

            try {
                setError('');

                // Store last users query for potential RAG enhancement
                lastUserQuery.current = prompt;

                // Add users message to session
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

                // Send message via REST API (server will stream response via WebSocket)
                const backendSessionId = activeSession?.sessionId;
                if (!backendSessionId) {
                    throw new Error('No backend session ID available');
                }
                await apiService.sendChatMessage(
                    activeWorkspaceId,
                    backendSessionId,
                    prompt,
                    undefined,
                    ignoreRag
                );
             } catch (error: unknown) {
                 logger.error('Error sending message', error as Error, {
                     sessionId: activeSessionId,
                     workspaceId: activeWorkspaceId,
                 });

                // Handle different error types
                let errorMessage = 'Something went wrong, try again!';
                if (error && typeof error === 'object' && 'response' in error) {
                    const axiosError = error as {
                        response?: { status?: number; data?: { detail?: string } };
                    };
                    if (axiosError.response?.status === 401) {
                        errorMessage = 'Authentication failed. Please log in again.';
                    } else if (axiosError.response?.status === 403) {
                        errorMessage =
                            'You do not have permission to send messages in this workspace.';
                    } else if (axiosError.response?.status === 404) {
                        errorMessage = 'Workspace or session not found.';
                    } else if (axiosError.response?.data?.detail) {
                        errorMessage = axiosError.response.data.detail;
                    }
                }

                setError(errorMessage);

                // Add error message to chats
                dispatch(
                    addMessageToSession({
                        sessionId: activeSessionId,
                        message: {
                            id: `msg-${Date.now()}`,
                            content: `Error: ${errorMessage}`,
                            role: 'bot',
                            timestamp: Date.now(),
                        },
                    })
                );

                setIsBotTyping(false);
                dispatch(setTyping(false));
            }
        },
        [activeSessionId, activeWorkspaceId, activeSession?.sessionId, dispatch]
    );

    useEffect(() => {
        if (!activeWorkspaceId) return;

        // Connect to socket on mount
        socketService.connect();

        // Set up event listeners
         socketService.onConnected(() => {
             logger.info('Connected to chat server');
         });

        socketService.onChatResponseChunk((data) => {
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
                currentBotMessageId.current = data.message_id;
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

             logger.info('Chat stream cancelled by user', {
                 sessionId: activeSessionId,
             });

            // Reset current message buffer
            currentBotMessage.current = '';
            currentBotMessageId.current = null;

            // Stop typing indicator
            setIsBotTyping(false);
            dispatch(setTyping(false));
        });

         socketService.onError((data) => {
             logger.error('Socket error occurred', new Error(data.error), {
                 sessionId: activeSessionId,
             });
            const errorMessage = data.error || 'Connection error occurred';

            setError(errorMessage);

            // Add error message to chats if we were in the middle of a response
            if (currentBotMessageId.current) {
                dispatch(
                    addMessageToSession({
                        sessionId: activeSessionId,
                        message: {
                            id: `msg-${Date.now()}`,
                            content: `Connection error: ${errorMessage}. Please try again.`,
                            role: 'bot',
                            timestamp: Date.now(),
                        },
                    })
                );
            }

            setIsBotTyping(false);
            dispatch(setTyping(false));
            currentBotMessage.current = '';
            currentBotMessageId.current = null;
        });

         socketService.onDisconnected(() => {
             logger.info('Disconnected from chat server');
         });

         // Listen for no context found event to show RAG enhancement prompt
         socketService.on('chats.no_context_found', (data: { session_id: number; query: string }) => {
             if (!activeSessionId) return;
             logger.info('No context found for query', {
                 sessionId: activeSessionId,
                 query: data.query,
             });
            setShowRAGPrompt(true);
        });

        // Cleanup on unmount
        return () => {
            socketService.removeAllListeners();
            socketService.disconnect();
        };
    }, [activeSessionId, activeWorkspaceId, dispatch]);

    const onCancel = async () => {
        try {
            if (activeWorkspaceId && activeSession?.sessionId) {
                // Cancel via API
                await apiService.cancelChatMessage(
                    activeWorkspaceId,
                    activeSession.sessionId,
                    currentBotMessageId.current || undefined
                );
             } else {
                 logger.warn('Cannot cancel message: missing workspace or session ID', {
                     workspaceId: activeWorkspaceId,
                     sessionId: activeSession?.sessionId,
                 });
             }

            // Also cancel via WebSocket for immediate response
            socketService.cancelMessage();

            // Reset state
            setIsBotTyping(false);
            dispatch(setTyping(false));
            currentBotMessage.current = '';
             currentBotMessageId.current = null;

             logger.info('Message cancelled successfully');
         } catch (error: unknown) {
             logger.error('Error cancelling message', error as Error, {
                 sessionId: activeSessionId,
                 workspaceId: activeWorkspaceId,
             });
            const errorMessage = 'Failed to cancel message. It may still be processing.';
            setError(errorMessage);

            // Add error message to chats
            if (activeSessionId) {
                dispatch(
                    addMessageToSession({
                        sessionId: activeSessionId,
                        message: {
                            id: `msg-${Date.now()}`,
                            content: errorMessage,
                            role: 'bot',
                            timestamp: Date.now(),
                        },
                    })
                );
            }
        }
    };

    const handleFetchWikipedia = async (query: string) => {
        if (!activeWorkspaceId || !activeSessionId) return;

        setShowRAGPrompt(false); // Hide the prompt
        setError('');
        setIsBotTyping(true);
        dispatch(setTyping(true));
        // Add a message indicating Wikipedia fetch initiated
        dispatch(
            addMessageToSession({
                sessionId: activeSessionId,
                message: {
                    id: `msg-${Date.now()}`,
                    content: `Searching Wikipedia for "${query}"...`,
                    role: 'bot',
                    timestamp: Date.now(),
                },
            })
        );

        try {
            await apiService.fetchWikipediaArticle(activeWorkspaceId, query);
            // After successful fetch, retry the original query
            // The document processing status will be updated via sockets.
            // When processing completes, isWorkspaceProcessing will become false,
            // and then we can automatically re-submit the query.
            dispatch(
                addMessageToSession({
                    sessionId: activeSessionId,
                    message: {
                        id: `msg-${Date.now() + 1}`,
                        content:
                            'Wikipedia article fetched and processing. Retrying your query shortly...',
                        role: 'bot',
                        timestamp: Date.now(),
                    },
                })
            );
            // Actual re-submission will be handled by a useEffect watching isWorkspaceProcessing
         } catch (err: unknown) {
             logger.error('Error fetching Wikipedia article', err as Error, {
                 sessionId: activeSessionId,
                 workspaceId: activeWorkspaceId,
                 query,
             });
            const error = err as { response?: { data?: { detail?: string }; status?: number } };
            let message = 'Failed to fetch Wikipedia article.';

            if (error.response?.status === 429) {
                message = 'Too many requests. Please wait before trying again.';
            } else if (error.response?.status === 404) {
                message = 'Wikipedia article not found. Try a different search term.';
            } else if (error.response?.data?.detail) {
                message = error.response.data.detail;
            }

            setError(message);
            dispatch(
                addMessageToSession({
                    sessionId: activeSessionId,
                    message: {
                        id: `msg-${Date.now() + 1}`,
                        content: `Error fetching Wikipedia article: ${message}`,
                        role: 'bot',
                        timestamp: Date.now(),
                    },
                })
            );
            setIsBotTyping(false);
            dispatch(setTyping(false));
        }
    };

    const handleUploadDocument = () => {
        if (!activeWorkspaceId || !activeSessionId) return;
        setShowRAGPrompt(false); // Hide the prompt
        dispatch(
            addMessageToSession({
                sessionId: activeSessionId,
                message: {
                    id: `msg-${Date.now()}`,
                    content: `Please use the "Documents" panel on the right to upload your document. Once uploaded, your previous query will be retried automatically after processing completes.`,
                    role: 'bot',
                    timestamp: Date.now(),
                },
            })
        );
        // Logic to visually indicate the document panel might be needed here.
        // For now, simple instruction.
    };

    const handleContinueChat = () => {
        setShowRAGPrompt(false); // Hide the prompt
        if (lastUserQuery.current) {
            onSubmit({ prompt: lastUserQuery.current }, true); // Pass ignoreRag=true
            lastUserQuery.current = ''; // Clear after use
        }
    };

    // Effect to retry query after RAG enhancement completes
    useEffect(() => {
         // Only retry if there's a last query, workspace is no longer processing, and bot isn't typing
         if (activeWorkspaceId && lastUserQuery.current && !isWorkspaceProcessing && !isBotTyping) {
             logger.info('RAG enhancement complete, retrying last query', {
                 workspaceId: activeWorkspaceId,
                 query: lastUserQuery.current,
             });
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
            {/* ChatSessionManager handles backend session synchronization */}
            {activeWorkspaceId && <ChatSessionManager workspaceId={activeWorkspaceId} />}
            {/* DocumentManager is now rendered in Layout.tsx */}
            <ChatMessages
                messages={messages}
                error={error}
                isBotTyping={isBotTyping}
                onUploadDocument={handleUploadDocument}
                onFetchWikipedia={handleFetchWikipedia}
                onContinueChat={handleContinueChat}
            />
            <RAGEnhancementPrompt
                isVisible={showRAGPrompt}
                onUploadDocument={handleUploadDocument}
                onFetchWikipedia={handleFetchWikipedia}
                onContinueWithoutContext={handleContinueChat}
                lastQuery={lastUserQuery.current}
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
