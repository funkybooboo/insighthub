import { FaArrowUp } from 'react-icons/fa';
import { useForm } from 'react-hook-form';

import { Button } from '../ui/button';

export type ChatFormData = {
    prompt: string;
};

type Props = {
    onSubmit: (data: ChatFormData) => void;
};

const ChatInput = ({ onSubmit }: Props) => {
    const { register, handleSubmit, reset, formState } = useForm<ChatFormData>();

    const handleFormSubmit = handleSubmit((data) => {
        reset({ prompt: '' });
        onSubmit(data);
    });

    const handleKeyDown = (event: React.KeyboardEvent): void => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleFormSubmit();
        }
    };

    return (
        <div className="border-t border-gray-200 bg-white px-4 py-4">
            <form
                onSubmit={handleFormSubmit}
                onKeyDown={handleKeyDown}
                className="max-w-3xl mx-auto"
            >
                <div className="relative flex items-end gap-2 border border-gray-300 rounded-2xl bg-white px-4 py-3 shadow-sm focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all">
                    <textarea
                        {...register('prompt', {
                            required: true,
                            validate: (data: string): boolean => data.trim().length > 0,
                        })}
                        autoFocus
                        rows={1}
                        className="flex-1 resize-none border-0 focus:outline-none bg-transparent text-gray-900 placeholder-gray-500"
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
                    <Button
                        disabled={!formState.isValid}
                        className="rounded-full w-10 h-10 p-0 flex-shrink-0"
                        title="Send message"
                    >
                        <FaArrowUp className="w-4 h-4" />
                    </Button>
                </div>
            </form>
        </div>
    );
};

export default ChatInput;
