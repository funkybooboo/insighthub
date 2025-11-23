import { FaArrowUp } from 'react-icons/fa';
import { MdCancel } from 'react-icons/md';
import { useForm } from 'react-hook-form';
import { useEffect } from 'react';

import { Button } from '../ui/button';

export type ChatFormData = {
    prompt: string;
};

type Props = {
    onSubmit: (data: ChatFormData) => void;
    onCancel: () => void;
    isTyping: boolean;
};

const ChatInput = ({ onSubmit, onCancel, isTyping }: Props) => {
    const { register, handleSubmit, reset, formState } = useForm<ChatFormData>();

    const handleFormSubmit = handleSubmit((data) => {
        if (isTyping) {
            return;
        }
        reset({ prompt: '' });
        onSubmit(data);
    });

    const handleKeyDown = (event: React.KeyboardEvent): void => {
        // Handle Ctrl+C to cancel
        if (event.ctrlKey && event.key === 'c' && isTyping) {
            event.preventDefault();
            onCancel();
            return;
        }

        // Disable Enter when AI is typing
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            if (!isTyping) {
                handleFormSubmit();
            }
        }
    };

    const handleCancelClick = () => {
        onCancel();
    };

    // Global Ctrl+C handler
    useEffect(() => {
        const handleGlobalKeyDown = (event: KeyboardEvent) => {
            if (event.ctrlKey && event.key === 'c' && isTyping) {
                event.preventDefault();
                onCancel();
            }
        };

        document.addEventListener('keydown', handleGlobalKeyDown);
        return () => {
            document.removeEventListener('keydown', handleGlobalKeyDown);
        };
    }, [isTyping, onCancel]);

    return (
        <div className="px-4 sm:px-6 lg:px-8 py-4 bg-gradient-to-t from-white via-white to-transparent dark:from-gray-900 dark:via-gray-900">
            <form
                onSubmit={handleFormSubmit}
                onKeyDown={handleKeyDown}
                className="max-w-3xl mx-auto"
            >
                <div className="relative flex items-end gap-3 bg-white dark:bg-gray-800 rounded-2xl px-4 py-3 shadow-lg shadow-gray-200/50 dark:shadow-none border border-gray-200/80 dark:border-gray-700/50 focus-within:border-blue-400 dark:focus-within:border-blue-500/50 focus-within:ring-2 focus-within:ring-blue-100 dark:focus-within:ring-blue-900/30 transition-all">
                    <textarea
                        {...register('prompt', {
                            required: true,
                            validate: (data: string): boolean => data.trim().length > 0,
                        })}
                        autoFocus
                        rows={1}
                        className="flex-1 resize-none border-0 focus:outline-none bg-transparent text-gray-800 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 text-sm leading-relaxed"
                        placeholder="Ask me anything..."
                        maxLength={1000}
                        style={{
                            minHeight: '24px',
                            maxHeight: '200px',
                        }}
                        onInput={(e) => {
                            const target = e.target as HTMLTextAreaElement;
                            target.style.height = 'auto';
                            target.style.height = `${target.scrollHeight}px`;
                        }}
                    />
                    {isTyping ? (
                        <Button
                            type="button"
                            onClick={handleCancelClick}
                            className="rounded-xl w-9 h-9 p-0 flex-shrink-0 bg-red-500 hover:bg-red-600 shadow-sm"
                            title="Cancel (Ctrl+C)"
                        >
                            <MdCancel className="w-4 h-4" />
                        </Button>
                    ) : (
                        <Button
                            type="submit"
                            disabled={!formState.isValid}
                            className="rounded-xl w-9 h-9 p-0 flex-shrink-0 shadow-sm disabled:shadow-none"
                            title="Send message"
                        >
                            <FaArrowUp className="w-3.5 h-3.5" />
                        </Button>
                    )}
                </div>
            </form>
        </div>
    );
};

export default ChatInput;
