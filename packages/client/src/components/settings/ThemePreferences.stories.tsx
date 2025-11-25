import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import themeSlice from '../../store/slices/themeSlice';

// Mock ThemePreferences component for Storybook to avoid API calls
const MockThemePreferences = () => {
  const [currentTheme, setCurrentTheme] = React.useState<'light' | 'dark'>('light');
  const [isLoading, setIsLoading] = React.useState(false);
  const [message, setMessage] = React.useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleThemeChange = async (newTheme: 'light' | 'dark') => {
    setIsLoading(true);
    setMessage(null);

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));

    setCurrentTheme(newTheme);
    setMessage({
      type: 'success',
      text: 'Theme preference saved',
    });
    setIsLoading(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
          Theme Preferences
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Choose your preferred theme for the application.
        </p>
      </div>

      {message && (
        <div
          className={`p-4 rounded-md ${
            message.type === 'success'
              ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
              : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
          }`}
        >
          {message.text}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 block">
            Theme
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => handleThemeChange('light')}
              disabled={isLoading}
              className={`p-4 border rounded-lg text-left transition-all ${
                currentTheme === 'light'
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className="flex items-center gap-3">
                <div className="w-4 h-4 rounded-full bg-yellow-400"></div>
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">Light</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Bright theme</div>
                </div>
              </div>
            </button>

            <button
              onClick={() => handleThemeChange('dark')}
              disabled={isLoading}
              className={`p-4 border rounded-lg text-left transition-all ${
                currentTheme === 'dark'
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className="flex items-center gap-3">
                <div className="w-4 h-4 rounded-full bg-gray-800"></div>
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">Dark</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Dark theme</div>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={() => handleThemeChange(currentTheme)}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-md font-medium transition-colors disabled:cursor-not-allowed"
        >
          {isLoading ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
    </div>
  );
};

// Create a mock store for Storybook
const createMockStore = (initialState = { theme: { theme: 'light' } }) => {
  return configureStore({
    reducer: {
      theme: themeSlice,
    },
    preloadedState: initialState,
  });
};

const meta: Meta<typeof MockThemePreferences> = {
  title: 'Settings/ThemePreferences',
  component: MockThemePreferences,
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Theme preference settings with light/dark mode selection. (Mock implementation for Storybook)',
      },
    },
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const InSettingsPage: Story = {
  render: () => (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex">
            <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              Profile
            </button>
            <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
              Password
            </button>
            <button className="px-6 py-4 text-sm font-medium text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400">
              Preferences
            </button>
          </nav>
        </div>

        <div className="p-6">
          <MockThemePreferences />
        </div>
      </div>
    </div>
  ),
};