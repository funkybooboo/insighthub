import React from 'react';
import { FaArrowDown } from 'react-icons/fa';

interface ScrollToBottomButtonProps {
    onClick: () => void;
    visible: boolean;
}

export const ScrollToBottomButton: React.FC<ScrollToBottomButtonProps> = ({ onClick, visible }) => {
    if (!visible) return null;

    return (
        <button
            onClick={onClick}
            className="absolute bottom-6 right-6 bg-gray-900 dark:bg-gray-100 hover:bg-gray-800 dark:hover:bg-white text-white dark:text-gray-900 rounded-full p-2.5 shadow-lg transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 z-10"
            title="Scroll to bottom"
            aria-label="Scroll to bottom"
        >
            <FaArrowDown className="w-4 h-4" />
        </button>
    );
};

interface ChatScrollContainerProps {
    children: React.ReactNode;
    onScroll: () => void;
    className?: string;
}

export const ChatScrollContainer = React.forwardRef<HTMLDivElement, ChatScrollContainerProps>(
    ({ children, onScroll, className = '' }, ref) => (
        <div
            ref={ref}
            onScroll={onScroll}
            className={`h-full overflow-y-auto px-4 sm:px-6 lg:px-8 py-8 ${className}`}
        >
            {children}
        </div>
    )
);

interface EmptyChatStateProps {
    onExampleClick?: (query: string) => void;
}

export const EmptyChatState: React.FC<EmptyChatStateProps> = ({ onExampleClick }) => (
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
        {onExampleClick && (
            <div className="mt-6 space-y-2">
                <p className="text-sm text-gray-600 dark:text-gray-400">Try asking:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                    <button
                        onClick={() => onExampleClick('What is RAG?')}
                        className="px-3 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                    >
                        What is RAG?
                    </button>
                    <button
                        onClick={() => onExampleClick('How does vector search work?')}
                        className="px-3 py-1 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors"
                    >
                        How does vector search work?
                    </button>
                </div>
            </div>
        )}
    </div>
);

interface ChatErrorProps {
    error: string;
}

export const ChatError: React.FC<ChatErrorProps> = ({ error }) => (
    <div className="flex justify-center">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800/50 text-red-700 dark:text-red-300 px-4 py-3 rounded-xl max-w-md text-sm">
            {error}
        </div>
    </div>
);
