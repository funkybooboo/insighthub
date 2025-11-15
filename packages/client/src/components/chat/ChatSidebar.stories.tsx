import type { Meta, StoryObj } from '@storybook/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ChatSidebar from './ChatSidebar';
import chatReducer, { createSession, addMessageToSession } from '@/store/slices/chatSlice';

const meta: Meta<typeof ChatSidebar> = {
    title: 'Chat/ChatSidebar',
    component: ChatSidebar,
    parameters: {
        layout: 'padded',
    },
    decorators: [
        (Story, context) => {
            const store = configureStore({
                reducer: {
                    chat: chatReducer,
                },
            });

            // Add mock sessions based on story
            if (context.name === 'With Multiple Sessions') {
                store.dispatch(createSession({ id: 'session-1', title: 'TypeScript Best Practices' }));
                store.dispatch(
                    addMessageToSession({
                        sessionId: 'session-1',
                        message: { role: 'user', content: 'What are TypeScript best practices?' },
                    })
                );
                store.dispatch(
                    addMessageToSession({
                        sessionId: 'session-1',
                        message: {
                            role: 'bot',
                            content: 'Here are some TypeScript best practices...',
                        },
                    })
                );

                store.dispatch(createSession({ id: 'session-2', title: 'React Hooks Deep Dive' }));
                store.dispatch(
                    addMessageToSession({
                        sessionId: 'session-2',
                        message: { role: 'user', content: 'Explain React hooks' },
                    })
                );

                store.dispatch(createSession({ id: 'session-3', title: 'New Chat' }));
            } else if (context.name === 'With Single Session') {
                store.dispatch(createSession({ id: 'session-1', title: 'My First Chat' }));
                store.dispatch(
                    addMessageToSession({
                        sessionId: 'session-1',
                        message: { role: 'user', content: 'Hello!' },
                    })
                );
            }

            return (
                <Provider store={store}>
                    <div style={{ height: '600px', display: 'flex' }}>
                        <Story />
                    </div>
                </Provider>
            );
        },
    ],
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ChatSidebar>;

export const Empty: Story = {};

export const WithSingleSession: Story = {};

export const WithMultipleSessions: Story = {};
