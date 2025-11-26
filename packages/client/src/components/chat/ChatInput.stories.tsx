import type { Meta, StoryObj } from '@storybook/react-vite';
import ChatInput, { type ChatFormData } from './ChatInput';

const meta: Meta<typeof ChatInput> = {
    title: 'Chat/ChatInput',
    component: ChatInput,
    parameters: {
        layout: 'padded',
    },
    tags: ['autodocs'],
    argTypes: {
        isTyping: {
            control: 'boolean',
        },
    },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    args: {
        isTyping: false,
        onSubmit: (data: ChatFormData) => {
            console.log('Submitted:', data);
        },
        onCancel: () => {
            console.log('Cancelled');
        },
    },
};

export const Typing: Story = {
    args: {
        isTyping: true,
        onSubmit: (data: ChatFormData) => {
            console.log('Submitted:', data);
        },
        onCancel: () => {
            console.log('Cancelled');
        },
    },
};

export const InChatContext: Story = {
    render: () => (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <div className="flex flex-col h-full">
                {/* Mock chats messages area */}
                <div className="flex-1 p-4 space-y-4">
                    <div className="max-w-3xl mx-auto">
                        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                            <p className="text-gray-800 dark:text-gray-100">
                                Hello! How can I help you with your RAG system today?
                            </p>
                        </div>
                    </div>
                </div>

                {/* Chat input */}
                <ChatInput
                    isTyping={false}
                    onSubmit={(data) => console.log('Message sent:', data)}
                    onCancel={() => console.log('Cancelled')}
                />
            </div>
        </div>
    ),
};
