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
        <form
            onSubmit={handleFormSubmit}
            onKeyDown={handleKeyDown}
            className="flex flex-col gap-2 items-end border-2 p-4 rounded-3xl"
        >
            <textarea
                {...register('prompt', {
                    required: true,
                    validate: (data: string): boolean => data.trim().length > 0,
                })}
                autoFocus
                className="w-full border-0 focus:outline-0 resize-none"
                placeholder="Ask anything"
                maxLength={1000}
            />
            <Button disabled={!formState.isValid} className="rounded-full w-9 h-9">
                <FaArrowUp />
            </Button>
        </form>
    );
};

export default ChatInput;
