import React, { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { FaPlus, FaCog, FaFolderOpen } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import type { RootState, AppDispatch } from '@/store';
import {
    setWorkspaces,
    setActiveWorkspace,
    addWorkspace,
    setLoading,
    setError,
    selectActiveWorkspaceId,
    selectWorkspaces,
} from '@/store/slices/workspaceSlice';
import {
    fetchDefaultRagConfig,
    selectDefaultRagConfig,
    selectUserSettingsLoading,
} from '@/store/slices/userSettingsSlice';
import { LoadingSpinner } from '@/components/shared';
import { apiService } from '@/services/api';
import { validateWorkspaceName, validateDescription } from '@/lib/validation';
import RagConfigForm from './RagConfigForm';
import { type RagConfig, type CreateRagConfigRequest } from '@/types/workspace';
import { selectIsWorkspaceDeleting } from '@/store/slices/statusSlice';

import Modal from '@/components/shared/Modal';

const WorkspaceColumn: React.FC = () => {
    const dispatch = useDispatch<AppDispatch>();
    const workspaces = useSelector(selectWorkspaces);
    const activeWorkspaceId = useSelector(selectActiveWorkspaceId);
    const workspacesLoading = useSelector((state: RootState) => state.workspace.isLoading);
    const workspacesError = useSelector((state: RootState) => state.workspace.error);
    const workspaceStatuses = useSelector((state: RootState) => state.status.workspaces);
    const isAnyWorkspaceDeleting = useSelector((state: RootState) =>
        Object.values(state.status.workspaces).some((ws) =>
            selectIsWorkspaceDeleting(ws.workspace_id)(state)
        )
    );

    const defaultRagConfig = useSelector(selectDefaultRagConfig);
    const loadingDefaultRagConfig = useSelector(selectUserSettingsLoading);

    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newWorkspaceName, setNewWorkspaceName] = useState('');
    const [newWorkspaceDescription, setNewWorkspaceDescription] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [validationError, setValidationError] = useState<string | null>(null);

    // RAG config state for create modal (local state, pre-populated by defaultRagConfig)
    const [ragConfigForWorkspace, setRagConfigForWorkspace] = useState<Partial<RagConfig>>({});

    const _activeWorkspace = workspaces.find((w) => w.id === activeWorkspaceId);

    const handleRagConfigChange = useCallback((config: Partial<CreateRagConfigRequest>) => {
        setRagConfigForWorkspace(config.config || {});
    }, []);

    const loadWorkspaces = useCallback(async () => {
        dispatch(setLoading(true));
        try {
            const workspaceList = await apiService.listWorkspaces();
            dispatch(setWorkspaces(workspaceList));

            if (workspaceList.length > 0 && !activeWorkspaceId) {
                dispatch(setActiveWorkspace(workspaceList[0].id));
            }
        } catch (error: unknown) {
            const err = error as { response?: { data?: { message?: string } }; message?: string };
            const message =
                err.response?.data?.message || err.message || 'Failed to load workspaces';
            dispatch(setError(message));
        }
    }, [dispatch, activeWorkspaceId]);

    // Load workspaces on mount
    useEffect(() => {
        loadWorkspaces();
    }, [loadWorkspaces]);

    // Load users's default RAG config when modal opens
    // and set it as the initial config for the workspace creation form
    useEffect(() => {
        if (showCreateModal) {
            dispatch(fetchDefaultRagConfig());
        }
    }, [showCreateModal, dispatch]);

    useEffect(() => {
        if (defaultRagConfig) {
            // Convert RagConfig to the format expected by RagConfigForm
            setRagConfigForWorkspace(defaultRagConfig || {});
        }
    }, [defaultRagConfig]);

    const handleWorkspaceChange = (workspaceId: number) => {
        dispatch(setActiveWorkspace(workspaceId));
    };

    const handleCreateWorkspace = async (e: React.FormEvent) => {
        e.preventDefault();
        setValidationError(null);

        const nameValidation = validateWorkspaceName(newWorkspaceName);
        if (!nameValidation.valid) {
            setValidationError(nameValidation.error || 'Invalid workspace name');
            return;
        }

        const descValidation = validateDescription(newWorkspaceDescription);
        if (!descValidation.valid) {
            setValidationError(descValidation.error || 'Invalid description');
            return;
        }

        setIsCreating(true);
        try {
            const workspace = await apiService.createWorkspace({
                name: newWorkspaceName.trim(),
                description: newWorkspaceDescription.trim() || undefined,
                rag_config: ragConfigForWorkspace as CreateRagConfigRequest,
            });

            dispatch(addWorkspace(workspace));
            dispatch(setActiveWorkspace(workspace.id));
            handleCloseModal();
        } catch (error: unknown) {
            const err = error as { response?: { data?: { message?: string } }; message?: string };
            const message =
                err.response?.data?.message || err.message || 'Failed to create workspace';
            setValidationError(message);
        } finally {
            setIsCreating(false);
        }
    };

    const handleCloseModal = () => {
        setShowCreateModal(false);
        setNewWorkspaceName('');
        setNewWorkspaceDescription('');
        setRagConfigForWorkspace({}); // Reset local config state
        setValidationError(null);
    };

    return (
        <div className="p-5 space-y-4">
            {/* New Workspace Button */}
            <div className="border-b border-gray-200/80 dark:border-gray-800 pb-4">
                <button
                    onClick={() => setShowCreateModal(true)}
                    disabled={isAnyWorkspaceDeleting}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-sm"
                >
                    <FaPlus className="w-5 h-5" />
                    New Workspace
                </button>
            </div>

            {/* Workspaces List */}
            <div className="flex-1 overflow-y-auto">
                {workspacesLoading ? (
                    <div className="flex items-center justify-center py-8">
                        <LoadingSpinner size="md" />
                    </div>
                ) : workspacesError ? (
                    <div className="p-4 text-red-500 text-sm text-center">{workspacesError}</div>
                ) : workspaces.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-8 text-center px-4 text-gray-500 dark:text-gray-400">
                        <FaFolderOpen className="w-12 h-12 mb-3 text-gray-400 dark:text-gray-500" />
                        <p className="text-sm font-medium">No workspaces yet</p>
                        <p className="text-xs mt-1">Create your first workspace to get started</p>
                    </div>
                ) : (
                    <div className="space-y-1 p-3">
                        {workspaces.map((workspace) => {
                            const workspaceStatus =
                                workspaceStatuses[workspace.id]?.status || 'ready';
                            return (
                                <div
                                    key={workspace.id}
                                    onClick={() => handleWorkspaceChange(workspace.id)}
                                    className={`group relative px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                                        workspace.id === activeWorkspaceId
                                            ? 'bg-blue-50 dark:bg-blue-900/20'
                                            : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
                                    }`}
                                >
                                    <div className="flex items-center justify-between gap-2">
                                        <div className="flex-1 min-w-0">
                                            <h3
                                                className={`text-sm font-medium truncate ${
                                                    workspace.id === activeWorkspaceId
                                                        ? 'text-blue-700 dark:text-blue-300'
                                                        : 'text-gray-700 dark:text-gray-200'
                                                }`}
                                            >
                                                {workspace.name}
                                            </h3>
                                            {workspace.description && (
                                                <p className="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">
                                                    {workspace.description}
                                                </p>
                                            )}
                                        </div>
                                        {workspaceStatus !== 'ready' && (
                                            <span
                                                className={`text-xs px-2 py-0.5 rounded-full flex-shrink-0 ${
                                                    workspaceStatus === 'provisioning'
                                                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                                                        : workspaceStatus === 'deleting'
                                                          ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
                                                          : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                                                }`}
                                            >
                                                {workspaceStatus}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Workspace Settings Link */}
            {activeWorkspaceId && (
                <div className="border-t border-gray-200/80 dark:border-gray-800 p-3">
                    <Link
                        to={`/workspaces/${activeWorkspaceId}`}
                        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/50 rounded-lg transition-colors"
                    >
                        <FaCog className="w-4 h-4" />
                        Workspace Settings
                    </Link>
                </div>
            )}

            {/* Create Workspace Modal */}
            <Modal
                show={showCreateModal}
                onClose={handleCloseModal}
                title="Create New Workspace"
                footer={
                    <div className="flex justify-end gap-2 mt-6">
                        <button
                            type="button"
                            onClick={handleCloseModal}
                            className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                            disabled={isCreating}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            form="create-workspace-form"
                            disabled={isCreating || !newWorkspaceName.trim()}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isCreating ? 'Creating...' : 'Create Workspace'}
                        </button>
                    </div>
                }
            >
                <form id="create-workspace-form" onSubmit={handleCreateWorkspace}>
                    {validationError && (
                        <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 rounded-lg text-sm">
                            {validationError}
                        </div>
                    )}

                    {/* Basic Info */}
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Workspace Name
                        </label>
                        <input
                            type="text"
                            value={newWorkspaceName}
                            onChange={(e) => {
                                setNewWorkspaceName(e.target.value);
                                setValidationError(null);
                            }}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                            placeholder="e.g., Research Papers"
                            maxLength={100}
                            required
                            autoFocus
                        />
                    </div>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Description (optional)
                        </label>
                        <textarea
                            value={newWorkspaceDescription}
                            onChange={(e) => {
                                setNewWorkspaceDescription(e.target.value);
                                setValidationError(null);
                            }}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                            placeholder="What is this workspace for?"
                            maxLength={500}
                            rows={2}
                        />
                    </div>

                    {/* RAG Configuration */}
                    <div className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-4">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            RAG Configuration
                        </span>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 mb-4">
                            Configure retrieval settings for this workspace.
                        </p>

                        {loadingDefaultRagConfig && (
                            <div className="mt-2 flex items-center gap-2 text-sm text-gray-500">
                                <LoadingSpinner size="sm" />
                                Loading default configuration...
                            </div>
                        )}

                        {!loadingDefaultRagConfig && (
                            <div className="mt-4">
                                <RagConfigForm
                                    initialConfig={defaultRagConfig || {}}
                                    onConfigChange={handleRagConfigChange}
                                />
                            </div>
                        )}
                    </div>

                    {/* Info about provisioning */}
                    <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <p className="text-sm text-blue-700 dark:text-blue-300">
                            Creating a workspace will set up the required RAG infrastructure. This
                            may take a moment.
                        </p>
                    </div>
                </form>
            </Modal>
        </div>
    );
};

export default WorkspaceColumn;
