import { useRef, useState } from 'react';
import axios from 'axios';

import type { Message } from './ChatMessages';
import ChatMessages from './ChatMessages';
import ChatInput, { type ChatFormData } from './ChatInput';

import popSound from '@/assets/sounds/pop.mp3';
import notificationSound from '@/assets/sounds/notification.mp3';

const popAudio = new Audio(popSound);
popAudio.volume = 0.2;

const notificationAudio = new Audio(notificationSound);
notificationAudio.volume = 0.2;

type ChatReponse = {
    message: string;
};

const ChatBot = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isBotTyping, setIsBotTyping] = useState(false);
    const [error, setError] = useState('');
    const conversationId = useRef(crypto.randomUUID());

    const onSubmit = async ({ prompt }: ChatFormData) => {
        try {
            setError('');
            setMessages((prev) => [...prev, { content: prompt, role: 'user' }]);
            setIsBotTyping(true);
            popAudio.play();

            const { data } = await axios.post<ChatReponse>(
                '/api/chat',
                {
                    prompt,
                    conversationId: conversationId.current,
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );

            setMessages((prev) => [
                ...prev,
                { content: data.message, role: 'bot' },
            ]);
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
            <ChatMessages
                messages={messages}
                error={error}
                isBotTyping={isBotTyping}
            />
            <ChatInput onSubmit={onSubmit} />
        </div>
    );
};

export default ChatBot;
