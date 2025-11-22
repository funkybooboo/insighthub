import { useState } from 'react';
import { useForm } from 'react-hook-form';
import api from '../../services/api';

interface PasswordFormData {
    currentPassword: string;
    newPassword: string;
    confirmPassword: string;
}

export default function PasswordChangeForm() {
    const {
        register,
        handleSubmit,
        watch,
        reset,
        formState: { errors },
    } = useForm<PasswordFormData>();
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(
        null
    );

    const newPassword = watch('newPassword');

    const onSubmit = async (data: PasswordFormData) => {
        setIsLoading(true);
        setMessage(null);

        try {
            await api.post('/auth/change-password', {
                current_password: data.currentPassword,
                new_password: data.newPassword,
            });

            setMessage({
                type: 'success',
                text: 'Password changed successfully',
            });
            reset();
        } catch (error: unknown) {
            const axiosError = error as { response?: { data?: { error?: string } } };
            setMessage({
                type: 'error',
                text: axiosError.response?.data?.error || 'Failed to change password',
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Change Password
            </h2>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-md">
                {/* Current Password */}
                <div>
                    <label
                        htmlFor="currentPassword"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                        Current Password
                    </label>
                    <input
                        {...register('currentPassword', {
                            required: 'Current password is required',
                        })}
                        type="password"
                        id="currentPassword"
                        className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-gray-900 dark:text-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    {errors.currentPassword && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                            {errors.currentPassword.message}
                        </p>
                    )}
                </div>

                {/* New Password */}
                <div>
                    <label
                        htmlFor="newPassword"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                        New Password
                    </label>
                    <input
                        {...register('newPassword', {
                            required: 'New password is required',
                            minLength: {
                                value: 8,
                                message: 'Password must be at least 8 characters',
                            },
                        })}
                        type="password"
                        id="newPassword"
                        className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-gray-900 dark:text-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    {errors.newPassword && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                            {errors.newPassword.message}
                        </p>
                    )}
                </div>

                {/* Confirm Password */}
                <div>
                    <label
                        htmlFor="confirmPassword"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                        Confirm New Password
                    </label>
                    <input
                        {...register('confirmPassword', {
                            required: 'Please confirm your password',
                            validate: (value) =>
                                value === newPassword || 'Passwords do not match',
                        })}
                        type="password"
                        id="confirmPassword"
                        className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-gray-900 dark:text-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    {errors.confirmPassword && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                            {errors.confirmPassword.message}
                        </p>
                    )}
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

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isLoading ? 'Changing Password...' : 'Change Password'}
                </button>
            </form>
        </div>
    );
}
