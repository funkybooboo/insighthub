import React from 'react';
import MarkdownRenderer from './MarkdownRenderer';
import ContextDisplay from './ContextDisplay';

// Mock message type for Storybook
interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
  context?: Array<{ text: string; score: number; metadata: Record<string, unknown> }>;
}

interface MessageItemProps {
  message: Message;
  onFetchWikipedia?: (query: string) => void;
  isWorkspaceProcessing?: boolean;
}

export const MessageItem = React.forwardRef<HTMLDivElement, MessageItemProps>(({
  message,
  onFetchWikipedia,
  isWorkspaceProcessing = false
}, ref) => {
  const handleCopyMessage = (event: React.ClipboardEvent) => {
    const selection = window.getSelection()?.toString().trim();
    if (selection) {
      event.preventDefault();
      event.clipboardData.setData('text/plain', selection);
    }
  };

  return (
    <div
      ref={ref}
      onCopy={handleCopyMessage}
      className={`flex ${
        message.role === 'user' ? 'justify-end' : 'justify-start'
      }`}
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
        {message.role === 'assistant' &&
          (message.context && message.context.length > 0 ? (
            <ContextDisplay context={message.context} />
          ) : (
            !isWorkspaceProcessing && (
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                  No relevant context found in documents.
                </p>
                {onFetchWikipedia && (
                  <button
                    onClick={() => onFetchWikipedia(message.content)}
                    className="px-3 py-1 bg-blue-500 text-white text-xs rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    Fetch from Wikipedia?
                  </button>
                )}
              </div>
            )
          ))}
      </div>
    </div>
  );
});