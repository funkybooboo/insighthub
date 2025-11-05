import { useEffect, useRef } from 'react';
import ReactMarkDown from 'react-markdown';

import TypingIndicator from './TypingIndicator';

export type Message = {
    content: string;
    role: 'user' | 'bot';
};

type Props = {
    messages: Message[];
    error: string;
    isBotTyping: boolean;
};

const ChatMessages = ({ messages, error, isBotTyping }: Props) => {
    const lastMessageRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        lastMessageRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const onCopyMessage = (event: React.ClipboardEvent) => {
        const selection = window.getSelection()?.toString().trim();
        if (selection) {
            event.preventDefault();
            event.clipboardData.setData('text/plain', selection);
        }
    };

    return (
        <div className="flex flex-col flex-1 gap-3 mb-10 overflow-y-auto">
            <div className="flex flex-col gap-3">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        onCopy={onCopyMessage}
                        ref={index === messages.length - 1 ? lastMessageRef : null}
                        className={`
                        px-3 py-1 rounded-xl
                        ${
                            message.role === 'user'
                                ? 'bg-blue-600 text-white self-end'
                                : 'bg-gray-100 text-black self-start'
                        }
                    `}
                    >
                        <ReactMarkDown>{message.content}</ReactMarkDown>
                    </div>
                ))}
            </div>
            {isBotTyping && <TypingIndicator />}
            {error && <p className="text-red-500">{error}</p>}
        </div>
    );
};

export default ChatMessages;
