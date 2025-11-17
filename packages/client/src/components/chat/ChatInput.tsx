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
        <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-6 py-4">
            <form onSubmit={handleFormSubmit} onKeyDown={handleKeyDown}>
                <div className="relative flex items-end gap-2 border border-gray-300 dark:border-gray-600 rounded-2xl bg-white dark:bg-gray-800 px-4 py-3 shadow-sm focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all">
                    <textarea
                        {...register('prompt', {
                            required: true,
                            validate: (data: string): boolean => data.trim().length > 0,
                        })}
                        autoFocus
                        rows={1}
                        className="flex-1 resize-none border-0 focus:outline-none bg-transparent text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
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
                            className="rounded-full w-10 h-10 p-0 flex-shrink-0 bg-red-500 hover:bg-red-600"
                            title="Cancel (Ctrl+C)"
                        >
                            <MdCancel className="w-5 h-5" />
                        </Button>
                    ) : (
                        <Button
                            disabled={!formState.isValid}
                            className="rounded-full w-10 h-10 p-0 flex-shrink-0"
                            title="Send message"
                        >
                            <FaArrowUp className="w-4 h-4" />
                        </Button>
                    )}
                </div>
            </form>
        </div>
    );
};

export default ChatInput;
