import type { Meta, StoryObj } from '@storybook/react-vite';
import TypingIndicator from './TypingIndicator';

const meta: Meta<typeof TypingIndicator> = {
    title: 'Chat/TypingIndicator',
    component: TypingIndicator,
    parameters: {
        layout: 'centered',
        docs: {
            description: {
                component: 'Animated typing indicator showing three bouncing dots.',
            },
        },
    },
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    parameters: {
        docs: {
            description: {
                story: 'Standard typing indicator with animated bouncing dots.',
            },
        },
    },
};

export const InChatContext: Story = {
    render: () => (
        <div className="max-w-3xl mx-auto p-4 space-y-4">
            {/* Previous messages */}
            <div className="flex justify-end">
                <div className="max-w-[75%] bg-blue-600 text-white rounded-2xl rounded-br-md px-4 py-3">
                    Hello! How can I help you today?
                </div>
            </div>

            {/* Typing indicator */}
            <div className="flex justify-start">
                <TypingIndicator />
            </div>
        </div>
    ),
    parameters: {
        docs: {
            description: {
                story: 'Typing indicator shown in a chat conversation context.',
            },
        },
    },
};
