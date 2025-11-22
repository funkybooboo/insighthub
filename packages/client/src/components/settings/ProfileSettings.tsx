import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useDispatch } from 'react-redux';
import api from '../../services/api';
import { setUser } from '../../store/slices/authSlice';

interface ProfileFormData {
    full_name: string;
    email: string;
}

interface User {
    id?: number;
    username?: string;
    email?: string;
    full_name?: string;
}

interface ProfileSettingsProps {
    user: User | null;
}

export default function ProfileSettings({ user }: ProfileSettingsProps) {
    const dispatch = useDispatch();
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<ProfileFormData>({
        defaultValues: {
            full_name: user?.full_name || '',
            email: user?.email || '',
        },
    });
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(
        null
    );

    const onSubmit = async (data: ProfileFormData) => {
        setIsLoading(true);
        setMessage(null);

        try {
            const response = await api.patch('/auth/profile', {
                full_name: data.full_name,
                email: data.email,
            });

            dispatch(setUser(response.data.user));
            setMessage({
                type: 'success',
                text: 'Profile updated successfully',
            });
        } catch (error: unknown) {
            const axiosError = error as { response?: { data?: { error?: string } } };
            setMessage({
                type: 'error',
                text: axiosError.response?.data?.error || 'Failed to update profile',
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Profile Information
            </h2>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-md">
                {/* Username (read-only) */}
                <div>
                    <label
                        htmlFor="username"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                        Username
                    </label>
                    <input
                        type="text"
                        id="username"
                        value={user?.username || ''}
                        disabled
                        className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-3 py-2 text-gray-500 dark:text-gray-400 cursor-not-allowed"
                    />
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        Username cannot be changed
                    </p>
                </div>

                {/* Full Name */}
                <div>
                    <label
                        htmlFor="full_name"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                        Full Name
                    </label>
                    <input
                        {...register('full_name', {
                            maxLength: {
                                value: 255,
                                message: 'Name is too long',
                            },
                        })}
                        type="text"
                        id="full_name"
                        className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-gray-900 dark:text-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    {errors.full_name && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                            {errors.full_name.message}
                        </p>
                    )}
                </div>

                {/* Email */}
                <div>
                    <label
                        htmlFor="email"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                        Email
                    </label>
                    <input
                        {...register('email', {
                            required: 'Email is required',
                            pattern: {
                                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                message: 'Invalid email address',
                            },
                        })}
                        type="email"
                        id="email"
                        className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-2 text-gray-900 dark:text-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    {errors.email && (
                        <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                            {errors.email.message}
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
                    {isLoading ? 'Saving...' : 'Save Changes'}
                </button>
            </form>
        </div>
    );
}
