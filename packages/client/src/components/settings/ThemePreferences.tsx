import { useSelector, useDispatch } from 'react-redux';
import { useState } from 'react';
import type { RootState } from '../../store';
import { setTheme } from '../../store/slices/themeSlice';
import api from '../../services/api';

export default function ThemePreferences() {
    const dispatch = useDispatch();
    const { theme } = useSelector((state: RootState) => state.theme);
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(
        null
    );

    const handleThemeChange = async (newTheme: 'light' | 'dark') => {
        setIsLoading(true);
        setMessage(null);

        try {
            // Update theme in Redux
            dispatch(setTheme(newTheme));

            // Save to server
            await api.patch('/auth/preferences', {
                theme_preference: newTheme,
            });

            setMessage({
                type: 'success',
                text: 'Theme preference saved',
            });
        } catch (error: any) {
            setMessage({
                type: 'error',
                text: error.response?.data?.error || 'Failed to save theme preference',
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Theme Preferences
            </h2>

            <div className="space-y-4 max-w-md">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                    Choose your preferred color theme
                </p>

                {/* Theme Options */}
                <div className="space-y-3">
                    <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 border-gray-300 dark:border-gray-600">
                        <input
                            type="radio"
                            name="theme"
                            value="light"
                            checked={theme === 'light'}
                            onChange={() => handleThemeChange('light')}
                            disabled={isLoading}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                        />
                        <div className="ml-3">
                            <span className="block text-sm font-medium text-gray-900 dark:text-white">
                                Light Mode
                            </span>
                            <span className="block text-sm text-gray-500 dark:text-gray-400">
                                Use light backgrounds and dark text
                            </span>
                        </div>
                    </label>

                    <label className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 border-gray-300 dark:border-gray-600">
                        <input
                            type="radio"
                            name="theme"
                            value="dark"
                            checked={theme === 'dark'}
                            onChange={() => handleThemeChange('dark')}
                            disabled={isLoading}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                        />
                        <div className="ml-3">
                            <span className="block text-sm font-medium text-gray-900 dark:text-white">
                                Dark Mode
                            </span>
                            <span className="block text-sm text-gray-500 dark:text-gray-400">
                                Use dark backgrounds and light text
                            </span>
                        </div>
                    </label>
                </div>

                {/* Message */}
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
            </div>
        </div>
    );
}
