import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
    fetchDefaultRagConfig,
    updateDefaultRagConfig,
    selectDefaultRagConfig,
    selectUserSettingsLoading,
    selectUserSettingsError,
    clearUserSettingsError,
} from '../store/slices/userSettingsSlice';
import { selectUser } from '../store/slices/authSlice';
import { logger } from '../lib/logger';
import { type AppDispatch } from '../store';
import RagConfigForm from '../components/workspace/RagConfigForm';
import ProfileSettings from '../components/settings/ProfileSettings';
import PasswordChangeForm from '../components/settings/PasswordChangeForm';
import ThemePreferences from '../components/settings/ThemePreferences';
import Modal from '../components/shared/Modal';
import { type RagConfig } from '../types/workspace';

// Simple hook to temporarily prevent view movement during button interactions
function usePreventViewMovement() {
    const preventMovement = useCallback(() => {
        // Store current position and prevent scroll for a short duration
        const currentX = window.scrollX;
        const currentY = window.scrollY;

        const preventScroll = (e: Event) => {
            e.preventDefault();
            window.scrollTo(currentX, currentY);
        };

        // Add temporary listeners that auto-remove
        document.addEventListener('scroll', preventScroll, { once: true, passive: false });
        document.addEventListener('wheel', preventScroll, { once: true, passive: false });

        setTimeout(() => {
            document.removeEventListener('scroll', preventScroll);
            document.removeEventListener('wheel', preventScroll);
        }, 100);
    }, []);

    return { preventMovement };
}

interface SettingsPageProps {
    isOpen: boolean;
    onClose: () => void;
}

const SettingsPage: React.FC<SettingsPageProps> = ({ isOpen, onClose }) => {
    const dispatch = useDispatch<AppDispatch>();
    const defaultRagConfig = useSelector(selectDefaultRagConfig);
    const isLoading = useSelector(selectUserSettingsLoading);
    const error = useSelector(selectUserSettingsError);
    const user = useSelector(selectUser);

    // Prevent view movement during interactions
    const { preventMovement } = usePreventViewMovement();

    const [currentConfig, setCurrentConfig] = useState<Partial<RagConfig>>(defaultRagConfig || {});
    const [saveSuccess, setSaveSuccess] = useState(false);
    const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

    useEffect(() => {
        if (isOpen) {
            dispatch(fetchDefaultRagConfig());
        }
    }, [isOpen, dispatch]);

    useEffect(() => {
        if (defaultRagConfig) {
            setCurrentConfig(defaultRagConfig);
        }
    }, [defaultRagConfig]);

    useEffect(() => {
        if (error) {
            // Optionally, show a toast or alert for the error
            logger.error('Settings error occurred', new Error(error));
        }
    }, [error]);

    const handleConfigChange = (newConfig: Partial<RagConfig>) => {
        setCurrentConfig(newConfig);
        setSaveSuccess(false); // Reset success message on change
        setHasUnsavedChanges(true); // Mark as having unsaved changes
    };

    const handleSave = async () => {
        if (error) {
            dispatch(clearUserSettingsError());
        }
        setSaveSuccess(false);

        const resultAction = await dispatch(updateDefaultRagConfig(currentConfig as RagConfig));
        if (updateDefaultRagConfig.fulfilled.match(resultAction)) {
            setSaveSuccess(true);
            setHasUnsavedChanges(false); // Reset unsaved changes flag
            // Auto-hide success message after 5 seconds
            setTimeout(() => setSaveSuccess(false), 5000);
        }
    };

    const handleCancel = () => {
        if (defaultRagConfig) {
            setCurrentConfig(defaultRagConfig); // Revert to last saved config
        } else {
            setCurrentConfig({}); // Clear if no default was ever set
        }
        setSaveSuccess(false);
        setHasUnsavedChanges(false); // Reset unsaved changes flag
        dispatch(clearUserSettingsError());
    };

    const handleClose = () => {
        handleCancel();
        onClose();
    };

    return (
        <Modal show={isOpen} onClose={handleClose} title="User Settings">
            <div className="space-y-6">
                <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
                        Profile Information
                    </h2>
                    <ProfileSettings user={user} />
                </section>

                <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
                        Change Password
                    </h2>
                    <PasswordChangeForm />
                </section>

                <section>
                    <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
                        Theme Preferences
                    </h2>
                    <ThemePreferences />
                </section>

                <section>
                    <div className="flex items-center mb-4">
                        <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
                            Default RAG Configuration
                        </h2>
                        {hasUnsavedChanges && (
                            <span className="ml-2 inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-orange-500 text-white shadow-md animate-pulse">
                                <svg
                                    className="w-3 h-3 mr-1.5"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path
                                        fillRule="evenodd"
                                        d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                                        clipRule="evenodd"
                                    />
                                </svg>
                                Unsaved Changes
                            </span>
                        )}
                    </div>
                    {isLoading && (
                        <p className="text-gray-600 dark:text-gray-400">
                            Loading RAG configuration...
                        </p>
                    )}
                    {error && (
                        <div className="mb-4 p-4 bg-red-100 dark:bg-red-950 border-2 border-red-500 dark:border-red-600 rounded-lg shadow-lg">
                            <div className="flex">
                                <div className="flex-shrink-0">
                                    <svg
                                        className="h-6 w-6 text-red-600 dark:text-red-400"
                                        viewBox="0 0 20 20"
                                        fill="currentColor"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                </div>
                                <div className="ml-3">
                                    <h3 className="text-sm font-bold text-red-900 dark:text-red-100">
                                        Configuration Error
                                    </h3>
                                    <div className="mt-2 text-sm text-red-800 dark:text-red-200">
                                        <p>{error}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {!isLoading && (
                        <>
                            <RagConfigForm
                                initialConfig={defaultRagConfig || {}}
                                onConfigChange={handleConfigChange}
                                readOnly={false}
                            />

                            <div className="mt-6 flex justify-end space-x-3">
                                <button
                                    onClick={handleCancel}
                                    className="px-4 py-2 border-2 border-gray-400 dark:border-gray-500 rounded-lg shadow-sm text-sm font-semibold text-gray-800 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 hover:border-gray-500 dark:hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all duration-200"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={(e) => {
                                        preventMovement();
                                        handleSave();
                                    }}
                                    className={`px-4 py-2 border-2 border-transparent rounded-lg shadow-lg text-sm font-bold text-white focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center transition-all duration-200 ${
                                        hasUnsavedChanges
                                            ? 'bg-blue-600 hover:bg-blue-700 border-blue-600 hover:border-blue-700 animate-pulse shadow-blue-500/25'
                                            : 'bg-gray-500 border-gray-500 cursor-not-allowed'
                                    }`}
                                    disabled={isLoading || !hasUnsavedChanges}
                                >
                                    {isLoading && (
                                        <svg
                                            className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                                            xmlns="http://www.w3.org/2000/svg"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                        >
                                            <circle
                                                className="opacity-25"
                                                cx="12"
                                                cy="12"
                                                r="10"
                                                stroke="currentColor"
                                                strokeWidth="4"
                                            ></circle>
                                            <path
                                                className="opacity-75"
                                                fill="currentColor"
                                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                            ></path>
                                        </svg>
                                    )}
                                    {isLoading
                                        ? 'Saving...'
                                        : hasUnsavedChanges
                                          ? 'Save Changes'
                                          : 'No Changes'}
                                </button>
                            </div>
                            {saveSuccess && (
                                <div className="mt-4 p-4 bg-green-100 dark:bg-green-950 border-2 border-green-500 dark:border-green-600 rounded-lg shadow-lg">
                                    <div className="flex">
                                        <div className="flex-shrink-0">
                                            <svg
                                                className="h-6 w-6 text-green-600 dark:text-green-400"
                                                viewBox="0 0 20 20"
                                                fill="currentColor"
                                            >
                                                <path
                                                    fillRule="evenodd"
                                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                                    clipRule="evenodd"
                                                />
                                            </svg>
                                        </div>
                                        <div className="ml-3">
                                            <p className="text-sm font-bold text-green-900 dark:text-green-100">
                                                Configuration saved successfully!
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </section>
            </div>
        </Modal>
    );
};

export default SettingsPage;
