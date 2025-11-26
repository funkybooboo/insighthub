import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
    fetchDefaultRagConfig,
    updateDefaultRagConfig,
    selectDefaultRagConfig,
    selectUserSettingsLoading,
    selectUserSettingsError,
    clearUserSettingsError,
} from '../store/slices/userSettingsSlice';
import { logger } from '../lib/logger';
import { type AppDispatch, type RootState } from '../store';
import RagConfigForm from '../components/workspace/RagConfigForm';
import ProfileSettings from '../components/settings/ProfileSettings';
import PasswordChangeForm from '../components/settings/PasswordChangeForm';
import ThemePreferences from '../components/settings/ThemePreferences';
import Modal from '../components/shared/Modal';
import {
    type CreateRagConfigRequest,
    type VectorRagConfig,
    type GraphRagConfig,
} from '../types/workspace';

interface SettingsPageProps {
    isOpen: boolean;
    onClose: () => void;
}

const SettingsPage: React.FC<SettingsPageProps> = ({ isOpen, onClose }) => {
    const dispatch = useDispatch<AppDispatch>();
    const { user } = useSelector((state: RootState) => state.auth);
    const defaultRagConfig = useSelector(selectDefaultRagConfig);
    const isLoading = useSelector(selectUserSettingsLoading);
    const error = useSelector(selectUserSettingsError);

    const [currentConfig, setCurrentConfig] = useState<Partial<CreateRagConfigRequest>>(
        defaultRagConfig || {}
    );
    const [isEditing, setIsEditing] = useState(false);
    const [saveSuccess, setSaveSuccess] = useState(false);

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

    const handleConfigChange = (newConfig: Partial<CreateRagConfigRequest>) => {
        setCurrentConfig(newConfig);
        setSaveSuccess(false); // Reset success message on change
    };

    const handleSave = async () => {
        if (!isEditing) {
            setIsEditing(true);
            return;
        }

        if (error) {
            dispatch(clearUserSettingsError());
        }
        setSaveSuccess(false);

        let configToSave: CreateRagConfigRequest;

        if (currentConfig.retriever_type === 'graph') {
            configToSave = {
                retriever_type: 'graph',
                // Add default values for graph-specific fields if not set
                max_hops: (currentConfig as GraphRagConfig).max_hops || 2,
                entity_extraction_model:
                    (currentConfig as GraphRagConfig).entity_extraction_model || 'ollama',
                relationship_extraction_model:
                    (currentConfig as GraphRagConfig).relationship_extraction_model || 'ollama',
            };
        } else {
            // Default to vector if retriever_type is not 'graph' or undefined
            configToSave = {
                retriever_type: 'vector',
                embedding_model:
                    (currentConfig as VectorRagConfig).embedding_model || 'nomic-embed-text',
                chunk_size: (currentConfig as VectorRagConfig).chunk_size || 1000,
                chunk_overlap: (currentConfig as VectorRagConfig).chunk_overlap || 200,
                top_k: (currentConfig as VectorRagConfig).top_k || 8,
                rerank_enabled: (currentConfig as VectorRagConfig).rerank_enabled || false,
                rerank_model: (currentConfig as VectorRagConfig).rerank_model,
            };
        }

        const resultAction = await dispatch(updateDefaultRagConfig(configToSave));
        if (updateDefaultRagConfig.fulfilled.match(resultAction)) {
            setSaveSuccess(true);
            setIsEditing(false);
        } else {
            // Error handled by slice, just ensure editing mode stays for users to correct
            setIsEditing(true);
        }
    };

    const handleCancel = () => {
        if (defaultRagConfig) {
            setCurrentConfig(defaultRagConfig); // Revert to last saved config
        } else {
            setCurrentConfig({}); // Clear if no default was ever set
        }
        setIsEditing(false);
        setSaveSuccess(false);
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
                    <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">
                        Default RAG Configuration
                    </h2>
                    {isLoading && (
                        <p className="text-gray-600 dark:text-gray-400">
                            Loading RAG configuration...
                        </p>
                    )}
                    {error && <p className="text-red-500 mb-4">Error: {error}</p>}

                    {!isLoading && (
                        <>
                            <RagConfigForm
                                initialConfig={defaultRagConfig || {}}
                                onConfigChange={handleConfigChange}
                                readOnly={!isEditing}
                            />

                            <div className="mt-6 flex justify-end space-x-3">
                                {isEditing && (
                                    <button
                                        onClick={handleCancel}
                                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                    >
                                        Cancel
                                    </button>
                                )}
                                <button
                                    onClick={handleSave}
                                    className={`px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                                        isEditing
                                            ? 'bg-indigo-600 hover:bg-indigo-700'
                                            : 'bg-gray-600 hover:bg-gray-700'
                                    } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
                                    disabled={isLoading}
                                >
                                    {isLoading
                                        ? 'Saving...'
                                        : isEditing
                                          ? 'Save Changes'
                                          : 'Edit Configuration'}
                                </button>
                            </div>
                            {saveSuccess && (
                                <p className="mt-3 text-sm text-green-600 text-right">
                                    Configuration saved successfully!
                                </p>
                            )}
                        </>
                    )}
                </section>
            </div>
        </Modal>
    );
};

export default SettingsPage;
