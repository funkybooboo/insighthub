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
        <div className="flex-1 overflow-y-auto px-4 py-6">
            <div className="max-w-3xl mx-auto space-y-6">
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-center">
                        <div className="w-16 h-16 mb-4 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                            <svg
                                className="w-8 h-8 text-blue-600 dark:text-blue-400"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                                />
                            </svg>
                        </div>
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
                            Start a conversation
                        </h2>
                        <p className="text-gray-500 dark:text-gray-400 max-w-sm">
                            Ask questions about your documents and get insights powered by AI
                        </p>
                    </div>
                ) : (
                    <>
                        {messages.map((message, index) => (
                            <div
                                key={index}
                                onCopy={onCopyMessage}
                                ref={index === messages.length - 1 ? lastMessageRef : null}
                                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                                        message.role === 'user'
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                                    }`}
                                >
                                    <div
                                        className={`prose prose-sm max-w-none ${
                                            message.role === 'user' ? 'prose-invert' : 'prose-gray'
                                        }`}
                                    >
                                        <ReactMarkDown>{message.content}</ReactMarkDown>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </>
                )}
                {isBotTyping && (
                    <div className="flex justify-start">
                        <TypingIndicator />
                    </div>
                )}
                {error && (
                    <div className="flex justify-center">
                        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300 px-4 py-3 rounded-lg max-w-md">
                            {error}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatMessages;
