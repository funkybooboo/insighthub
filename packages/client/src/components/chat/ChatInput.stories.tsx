/**
 * Storybook stories for ChatInput component
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn } from '@storybook/test';
import { within, userEvent, expect } from '@storybook/test';
import ChatInput from './ChatInput';

const meta: Meta<typeof ChatInput> = {
    title: 'Chat/ChatInput',
    component: ChatInput,
    parameters: {
        layout: 'padded',
    },
    args: {
        onSubmit: fn(),
    },
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ChatInput>;

export const Default: Story = {
    name: 'Default Empty State',
};

export const WithText: Story = {
    name: 'With Text Entered',
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const textarea = canvas.getByPlaceholderText(/ask anything/i);

        await userEvent.type(textarea, 'What is artificial intelligence?', {
            delay: 50,
        });

        // Button should be enabled
        const button = canvas.getByRole('button');
        expect(button).not.toBeDisabled();
    },
};

export const WithMultilineText: Story = {
    name: 'With Multiline Text',
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const textarea = canvas.getByPlaceholderText(/ask anything/i);

        await userEvent.type(
            textarea,
            'Line 1{Shift>}{Enter}{/Shift}Line 2{Shift>}{Enter}{/Shift}Line 3',
            {
                delay: 30,
            }
        );

        expect(textarea).toHaveValue('Line 1\nLine 2\nLine 3');
    },
};

export const WithLongText: Story = {
    name: 'With Long Text',
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const textarea = canvas.getByPlaceholderText(/ask anything/i);

        const longText =
            'This is a very long question that contains multiple sentences and explores a complex topic in depth. It demonstrates how the textarea handles longer input and whether it provides appropriate feedback to the user about the length of their input.';

        await userEvent.type(textarea, longText, {
            delay: 10,
        });

        expect(textarea).toHaveValue(longText);
    },
};

export const DisabledButton: Story = {
    name: 'Disabled Submit Button (Empty)',
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const button = canvas.getByRole('button');

        // Button should be disabled when textarea is empty
        expect(button).toBeDisabled();
    },
};

export const WhitespaceOnly: Story = {
    name: 'With Whitespace Only',
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const textarea = canvas.getByPlaceholderText(/ask anything/i);
        const button = canvas.getByRole('button');

        await userEvent.type(textarea, '     ', {
            delay: 50,
        });

        // Button should remain disabled for whitespace-only input
        expect(button).toBeDisabled();
    },
};

export const SubmitWithEnter: Story = {
    name: 'Submit with Enter Key',
    play: async ({ canvasElement, args }) => {
        const canvas = within(canvasElement);
        const textarea = canvas.getByPlaceholderText(/ask anything/i);

        await userEvent.type(textarea, 'Quick question', {
            delay: 50,
        });
        await userEvent.keyboard('{Enter}');

        // onSubmit should be called
        expect(args.onSubmit).toHaveBeenCalledWith({
            prompt: 'Quick question',
        });

        // Textarea should be cleared
        expect(textarea).toHaveValue('');
    },
};

export const SubmitWithButton: Story = {
    name: 'Submit with Button Click',
    play: async ({ canvasElement, args }) => {
        const canvas = within(canvasElement);
        const textarea = canvas.getByPlaceholderText(/ask anything/i);
        const button = canvas.getByRole('button');

        await userEvent.type(textarea, 'Test message', {
            delay: 50,
        });
        await userEvent.click(button);

        // onSubmit should be called
        expect(args.onSubmit).toHaveBeenCalledWith({
            prompt: 'Test message',
        });

        // Textarea should be cleared
        expect(textarea).toHaveValue('');
    },
};

export const ShiftEnterNewline: Story = {
    name: 'Shift+Enter for Newline',
    play: async ({ canvasElement, args }) => {
        const canvas = within(canvasElement);
        const textarea = canvas.getByPlaceholderText(/ask anything/i);

        await userEvent.type(
            textarea,
            'First line{Shift>}{Enter}{/Shift}Second line',
            {
                delay: 50,
            }
        );

        // Should not submit
        expect(args.onSubmit).not.toHaveBeenCalled();

        // Should contain newline
        expect(textarea).toHaveValue('First line\nSecond line');
    },
};

export const MaxLengthValidation: Story = {
    name: 'Max Length Validation',
    parameters: {
        docs: {
            description: {
                story: 'The textarea has a maximum length of 1000 characters.',
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const textarea = canvas.getByPlaceholderText(/ask anything/i) as HTMLTextAreaElement;

        // Try to type more than max length
        const longText = 'a'.repeat(1001);
        await userEvent.type(textarea, longText, {
            delay: 1,
        });

        // Should respect maxLength attribute
        expect(textarea.value.length).toBeLessThanOrEqual(1000);
    },
};

export const AccessibilityFocus: Story = {
    name: 'Accessibility - Auto Focus',
    parameters: {
        docs: {
            description: {
                story: 'The textarea should automatically receive focus on mount.',
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const textarea = canvas.getByPlaceholderText(/ask anything/i);

        // Textarea should have focus
        expect(textarea).toHaveFocus();
    },
};
