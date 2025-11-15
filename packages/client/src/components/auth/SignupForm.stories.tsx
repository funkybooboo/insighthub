import type { Meta, StoryObj } from '@storybook/react-vite';
import { fn } from '@storybook/test';
import { BrowserRouter } from 'react-router-dom';
import SignupForm from './SignupForm';

const meta: Meta<typeof SignupForm> = {
    title: 'Auth/SignupForm',
    component: SignupForm,
    parameters: {
        layout: 'centered',
    },
    decorators: [
        (Story) => (
            <BrowserRouter>
                <div style={{ width: '400px' }}>
                    <Story />
                </div>
            </BrowserRouter>
        ),
    ],
    args: {
        onSignupSuccess: fn(),
    },
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof SignupForm>;

/**
 * Default signup form ready for user input
 */
export const Default: Story = {};

/**
 * Form with pre-filled values for demonstration
 */
export const PreFilled: Story = {
    play: async ({ canvasElement }) => {
        const canvas = canvasElement;
        const usernameInput = canvas.querySelector('input[name="username"]') as HTMLInputElement;
        const emailInput = canvas.querySelector('input[name="email"]') as HTMLInputElement;
        const fullNameInput = canvas.querySelector('input[name="fullName"]') as HTMLInputElement;

        if (usernameInput) usernameInput.value = 'johndoe';
        if (emailInput) emailInput.value = 'john.doe@example.com';
        if (fullNameInput) fullNameInput.value = 'John Doe';
    },
};

/**
 * Form showing validation error states
 */
export const WithValidationErrors: Story = {
    play: async ({ canvasElement }) => {
        const canvas = canvasElement;
        const submitButton = canvas.querySelector('button[type="submit"]') as HTMLButtonElement;

        if (submitButton) {
            submitButton.click();
        }
    },
};
