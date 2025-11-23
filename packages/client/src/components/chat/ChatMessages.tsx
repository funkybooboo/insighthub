import { useEffect, useRef, useState } from 'react';
import { FaArrowDown } from 'react-icons/fa';

import TypingIndicator from './TypingIndicator';
import MarkdownRenderer from './MarkdownRenderer';

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
    const scrollContainerRef = useRef<HTMLDivElement | null>(null);
    const [showScrollButton, setShowScrollButton] = useState(false);
    const shouldAutoScrollRef = useRef(true);

    const onCopyMessage = (event: React.ClipboardEvent) => {
        const selection = window.getSelection()?.toString().trim();
        if (selection) {
            event.preventDefault();
            event.clipboardData.setData('text/plain', selection);
        }
    };

    // Check if user is at the bottom
    const isAtBottom = () => {
        if (!scrollContainerRef.current) return true;
        const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
        return scrollHeight - scrollTop - clientHeight < 100;
    };

    // Scroll to bottom function
    const scrollToBottom = () => {
        if (lastMessageRef.current) {
            lastMessageRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
            shouldAutoScrollRef.current = true;
        }
    };

    // Detect if user scrolls away from bottom
    const handleScroll = () => {
        if (!scrollContainerRef.current) return;

        const atBottom = isAtBottom();
        shouldAutoScrollRef.current = atBottom;
        setShowScrollButton(!atBottom && messages.length > 0);
    };

    // Auto-scroll when messages change - only if user is at bottom
    useEffect(() => {
        if (shouldAutoScrollRef.current && lastMessageRef.current) {
            lastMessageRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }, [messages, isBotTyping]);

    return (
        <div className="flex-1 relative overflow-hidden">
            <div
                ref={scrollContainerRef}
                onScroll={handleScroll}
                className="h-full overflow-y-auto px-4 sm:px-6 lg:px-8 py-8"
            >
                <div className="max-w-3xl mx-auto space-y-5">
                    {messages.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-center">
                            <div className="w-14 h-14 mb-5 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                                <svg
                                    className="w-7 h-7 text-white"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={1.5}
                                        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                                    />
                                </svg>
                            </div>
                            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-2">
                                Start a conversation
                            </h2>
                            <p className="text-gray-500 dark:text-gray-400 max-w-sm text-sm leading-relaxed">
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
                                        className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 ${
                                            message.role === 'user'
                                                ? 'bg-blue-600 text-white rounded-br-md'
                                                : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 rounded-bl-md shadow-sm border border-gray-100 dark:border-gray-700/50'
                                        }`}
                                    >
                                        <MarkdownRenderer
                                            content={message.content}
                                            isUser={message.role === 'user'}
                                        />
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
                            <div className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800/50 text-red-700 dark:text-red-300 px-4 py-3 rounded-xl max-w-md text-sm">
                                {error}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {showScrollButton && (
                <button
                    onClick={scrollToBottom}
                    className="absolute bottom-6 right-6 bg-gray-900 dark:bg-gray-100 hover:bg-gray-800 dark:hover:bg-white text-white dark:text-gray-900 rounded-full p-2.5 shadow-lg transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 z-10"
                    title="Scroll to bottom"
                    aria-label="Scroll to bottom"
                >
                    <FaArrowDown className="w-4 h-4" />
                </button>
            )}
        </div>
    );
};

export default ChatMessages;
