import type { Meta, StoryObj } from '@storybook/react';
import TypingIndicator from './TypingIndicator';

const meta: Meta<typeof TypingIndicator> = {
    title: 'Chat/TypingIndicator',
    component: TypingIndicator,
    parameters: {
        layout: 'centered',
    },
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof TypingIndicator>;

export const Default: Story = {};

export const InChatContext: Story = {
    decorators: [
        (Story) => (
            <div className="w-96 p-4 bg-white rounded-lg shadow-md">
                <div className="space-y-2">
                    <div className="flex justify-end">
                        <div className="bg-blue-500 text-white px-4 py-2 rounded-lg max-w-xs">
                            Hello! How are you?
                        </div>
                    </div>
                    <div className="flex justify-start">
                        <Story />
                    </div>
                </div>
            </div>
        ),
    ],
};
