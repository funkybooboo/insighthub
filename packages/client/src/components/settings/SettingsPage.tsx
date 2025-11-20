import { useState } from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store';
import PasswordChangeForm from './PasswordChangeForm';
import ThemePreferences from './ThemePreferences';
import ProfileSettings from './ProfileSettings';
import RagConfigSettings from './RagConfigSettings';

type SettingsTab = 'profile' | 'password' | 'preferences' | 'rag-config';

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
    const { user } = useSelector((state: RootState) => state.auth);

    const tabs = [
        { id: 'profile' as SettingsTab, label: 'Profile' },
        { id: 'password' as SettingsTab, label: 'Password' },
        { id: 'preferences' as SettingsTab, label: 'Preferences' },
        { id: 'rag-config' as SettingsTab, label: 'RAG Config' },
    ];

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
            <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                        Settings
                    </h1>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                        Manage your account settings and preferences
                    </p>
                </div>

                {/* Tabs */}
                <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
                    <nav className="-mb-px flex space-x-8">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`
                                    py-4 px-1 border-b-2 font-medium text-sm
                                    ${
                                        activeTab === tab.id
                                            ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                                    }
                                `}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Content */}
                <div className="bg-white dark:bg-gray-900 shadow rounded-lg">
                    {activeTab === 'profile' && <ProfileSettings user={user} />}
                    {activeTab === 'password' && <PasswordChangeForm />}
                    {activeTab === 'preferences' && <ThemePreferences />}
                    {activeTab === 'rag-config' && <RagConfigSettings />}
                </div>
            </div>
        </div>
    );
}
