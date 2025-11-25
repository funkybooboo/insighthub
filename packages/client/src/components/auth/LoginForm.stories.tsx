import type { Meta, StoryObj } from '@storybook/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { configureStore } from '@reduxjs/toolkit';
import authSlice from '../../store/slices/authSlice';
import themeSlice from '../../store/slices/themeSlice';
import LoginForm from './LoginForm';

// Create a mock store for Storybook
const createMockStore = (initialState = {
  auth: { user: null, token: null },
  theme: { theme: 'light' }
}) => {
  return configureStore({
    reducer: {
      auth: authSlice,
      theme: themeSlice,
    },
    preloadedState: initialState,
  });
};

const meta: Meta<typeof LoginForm> = {
  title: 'Auth/LoginForm',
  component: LoginForm,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: 'Login form component with authentication functionality.',
      },
    },
  },
  tags: ['autodocs'],
  decorators: [
    (Story, context) => {
      const store = createMockStore(context.args?.initialState || {
        auth: { user: null, token: null },
        theme: { theme: 'light' }
      });
      return (
        <Provider store={store}>
          <BrowserRouter>
            <Story />
          </BrowserRouter>
        </Provider>
      );
    },
  ],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    initialState: {
      auth: { user: null, token: null },
      theme: { theme: 'light' }
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Basic login form display with light theme.',
      },
    },
  },
};

export const DarkMode: Story = {
  args: {
    initialState: {
      auth: { user: null, token: null },
      theme: { theme: 'dark' }
    },
  },
  parameters: {
    docs: {
      description: {
        story: 'Login form display with dark theme.',
      },
    },
  },
};