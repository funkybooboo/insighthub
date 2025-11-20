import { useEffect, useRef, useState } from 'react';
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
import type { Message } from '@/types/chat';
import ChatMessages from './ChatMessages';
import ChatInput, { type ChatFormData } from './ChatInput';
import DocumentManager from '@/components/upload/DocumentManager';
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
    const [isBotTyping, setIsBotTyping] = useState(false);
    const [error, setError] = useState('');
    const currentBotMessageId = useRef<string | null>(null);
    const currentBotMessage = useRef<string>('');

    // Get active session
    const activeSession = sessions.find((s) => s.id === activeSessionId);

    // Show message if no workspace is selected
    if (!activeWorkspaceId) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400">
                <p className="text-lg">Please create or select a workspace to start chatting</p>
            </div>
        );
    }

    // Create initial session if none exists
    useEffect(() => {
        if (!activeSessionId && sessions.length === 0) {
            const newSessionId = `session-${Date.now()}`;
            dispatch(createSession({ id: newSessionId }));
        } else if (!activeSessionId && sessions.length > 0) {
            // Set the first session as active if there's no active session
            dispatch(setActiveSession(sessions[0].id));
        }
    }, [activeSessionId, sessions, dispatch]);

    // Load documents on mount
    useEffect(() => {
        const loadDocuments = async () => {
            try {
                await apiService.listDocuments();
            } catch (error) {
                console.error('Error loading documents on mount:', error);
            }
        };

        loadDocuments();
    }, []);

    useEffect(() => {
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
    }, [activeSessionId, dispatch]);

    const onSubmit = async ({ prompt }: ChatFormData) => {
        if (!activeSessionId) {
            console.error('No active session');
            return;
        }

        try {
            setError('');

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
            });
        } catch (error) {
            console.error('Error sending message:', error);
            setError('Something went wrong, try again!');
            setIsBotTyping(false);
            dispatch(setTyping(false));
        }
    };

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

    // Convert Message[] to the format expected by ChatMessages component
    const messages =
        activeSession?.messages.map((msg) => ({
            content: msg.content,
            role: msg.role,
        })) || [];

    return (
        <div className="flex flex-col h-full bg-white dark:bg-gray-900">
            <DocumentManager />
            <ChatMessages messages={messages} error={error} isBotTyping={isBotTyping} />
            <ChatInput onSubmit={onSubmit} onCancel={onCancel} isTyping={isTyping} />
        </div>
    );
};

export default ChatBot;
