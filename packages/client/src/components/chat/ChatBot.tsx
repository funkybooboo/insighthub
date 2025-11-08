import { useEffect, useRef, useState } from 'react';

import type { Message } from './ChatMessages';
import ChatMessages from './ChatMessages';
import ChatInput, { type ChatFormData } from './ChatInput';
import DocumentManager from '@/components/upload/DocumentManager';
import socketService from '@/services/socket';

import popSound from '@/assets/sounds/pop.mp3';
import notificationSound from '@/assets/sounds/notification.mp3';

const popAudio = new Audio(popSound);
popAudio.volume = 0.2;

const notificationAudio = new Audio(notificationSound);
notificationAudio.volume = 0.2;

const ChatBot = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isBotTyping, setIsBotTyping] = useState(false);
    const [error, setError] = useState('');
    const sessionId = useRef<number | undefined>(undefined);
    const currentBotMessage = useRef<string>('');

    useEffect(() => {
        // Connect to socket on mount
        socketService.connect();

        // Set up event listeners
        socketService.onConnected(() => {
            console.log('Connected to chat server');
        });

        socketService.onChatChunk((data) => {
            // Append chunk to current bot message
            currentBotMessage.current += data.chunk;

            // Stop typing indicator on first chunk
            setIsBotTyping(false);

            // Update the last message (bot message) with accumulated content
            setMessages((prev) => {
                const newMessages = [...prev];
                if (newMessages.length > 0 && newMessages[newMessages.length - 1].role === 'bot') {
                    newMessages[newMessages.length - 1] = {
                        ...newMessages[newMessages.length - 1],
                        content: currentBotMessage.current,
                    };
                } else {
                    // First chunk - add new bot message
                    newMessages.push({ content: currentBotMessage.current, role: 'bot' });
                }
                return newMessages;
            });
        });

        socketService.onChatComplete((data) => {
            // Store session_id for subsequent messages
            sessionId.current = data.session_id;

            // Reset current message buffer
            currentBotMessage.current = '';

            // Stop typing indicator
            setIsBotTyping(false);

            // Play notification sound
            notificationAudio.play();
        });

        socketService.onError((data) => {
            console.error('Socket error:', data.error);
            setError(data.error);
            setIsBotTyping(false);
            currentBotMessage.current = '';
        });

        socketService.onDisconnected(() => {
            console.log('Disconnected from chat server');
        });

        // Cleanup on unmount
        return () => {
            socketService.removeAllListeners();
            socketService.disconnect();
        };
    }, []);

    const onSubmit = async ({ prompt }: ChatFormData) => {
        try {
            setError('');

            // Add user message to UI
            setMessages((prev) => [...prev, { content: prompt, role: 'user' }]);

            // Reset current bot message buffer
            currentBotMessage.current = '';

            // Set typing indicator
            setIsBotTyping(true);

            // Play pop sound
            popAudio.play();

            // Send message via socket
            socketService.sendMessage({
                message: prompt,
                session_id: sessionId.current,
            });
        } catch (error) {
            console.error('Error sending message:', error);
            setError('Something went wrong, try again!');
            setIsBotTyping(false);
        }
    };

    return (
        <div className="flex flex-col h-full">
            <DocumentManager />
            <ChatMessages messages={messages} error={error} isBotTyping={isBotTyping} />
            <ChatInput onSubmit={onSubmit} />
        </div>
    );
};

export default ChatBot;
