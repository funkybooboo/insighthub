import { useRef, useState } from 'react';

import type { Message } from './ChatMessages';
import ChatMessages from './ChatMessages';
import ChatInput, { type ChatFormData } from './ChatInput';
import DocumentManager from '@/components/upload/DocumentManager';
import apiService from '@/services/api';

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

    const onSubmit = async ({ prompt }: ChatFormData) => {
        try {
            setError('');
            setMessages((prev) => [...prev, { content: prompt, role: 'user' }]);
            setIsBotTyping(true);
            popAudio.play();

            const response = await apiService.sendChatMessage({
                message: prompt,
                session_id: sessionId.current,
            });

            // Store the session_id for subsequent messages
            sessionId.current = response.session_id;

            setMessages((prev) => [...prev, { content: response.answer, role: 'bot' }]);
            notificationAudio.play();
        } catch (error) {
            console.log(error);
            setError('Something went wrong, try again!');
        } finally {
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
