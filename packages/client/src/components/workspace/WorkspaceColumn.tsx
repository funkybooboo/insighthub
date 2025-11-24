import React, { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { FaPlus, FaCog } from 'react-icons/fa';
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
import {
    type CreateRagConfigRequest,
    type VectorRagConfig,
    type GraphRagConfig,
} from '@/types/workspace';
import WorkspaceHeader from './WorkspaceHeader'; // Import the new component
import { selectIsWorkspaceDeleting } from '@/store/slices/statusSlice';

const WorkspaceColumn: React.FC = () => {
    const dispatch = useDispatch<AppDispatch>();
    const workspaces = useSelector(selectWorkspaces);
    const activeWorkspaceId = useSelector(selectActiveWorkspaceId);
    const workspacesLoading = useSelector((state: RootState) => state.workspace.isLoading);
    const workspacesError = useSelector((state: RootState) => state.workspace.error);
    const isAnyWorkspaceDeleting = useSelector((state: RootState) =>
        Object.values(state.status.workspaces).some((ws) =>
            selectIsWorkspaceDeleting(ws.workspace_id)(state)
        )
    );

    const defaultRagConfig = useSelector(selectDefaultRagConfig);
    const loadingDefaultRagConfig = useSelector(selectUserSettingsLoading);

    const [showWorkspaceDropdown, setShowWorkspaceDropdown] = useState(false);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newWorkspaceName, setNewWorkspaceName] = useState('');
    const [newWorkspaceDescription, setNewWorkspaceDescription] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [validationError, setValidationError] = useState<string | null>(null);

    // RAG config state for create modal (local state, pre-populated by defaultRagConfig)
    const [ragConfigForWorkspace, setRagConfigForWorkspace] = useState<
        Partial<CreateRagConfigRequest>
    >({});

    const activeWorkspace = workspaces.find((w) => w.id === activeWorkspaceId);

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

    // Load user's default RAG config when modal opens
    // and set it as the initial config for the workspace creation form
    useEffect(() => {
        if (showCreateModal) {
            dispatch(fetchDefaultRagConfig());
        }
    }, [showCreateModal, dispatch]);

    useEffect(() => {
        if (defaultRagConfig) {
            setRagConfigForWorkspace(defaultRagConfig);
        }
    }, [defaultRagConfig]);

    const handleWorkspaceChange = (workspaceId: number) => {
        dispatch(setActiveWorkspace(workspaceId));
        setShowWorkspaceDropdown(false);
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
            // Ensure required fields are present with defaults if not explicitly set
            let finalRagConfig: CreateRagConfigRequest;

            if (ragConfigForWorkspace.retriever_type === 'graph') {
                finalRagConfig = {
                    retriever_type: 'graph',
                    max_hops: (ragConfigForWorkspace as Partial<GraphRagConfig>).max_hops || 2,
                    entity_extraction_model:
                        (ragConfigForWorkspace as Partial<GraphRagConfig>)
                            .entity_extraction_model || 'ollama',
                    relationship_extraction_model:
                        (ragConfigForWorkspace as Partial<GraphRagConfig>)
                            .relationship_extraction_model || 'ollama',
                };
            } else {
                // Default to vector if retriever_type is not 'graph' or undefined
                finalRagConfig = {
                    retriever_type: 'vector',
                    embedding_model:
                        (ragConfigForWorkspace as Partial<VectorRagConfig>).embedding_model ||
                        'nomic-embed-text',
                    chunk_size:
                        (ragConfigForWorkspace as Partial<VectorRagConfig>).chunk_size || 1000,
                    chunk_overlap:
                        (ragConfigForWorkspace as Partial<VectorRagConfig>).chunk_overlap || 200,
                    top_k: (ragConfigForWorkspace as Partial<VectorRagConfig>).top_k || 8,
                    rerank_enabled:
                        (ragConfigForWorkspace as Partial<VectorRagConfig>).rerank_enabled || false,
                    rerank_model: (ragConfigForWorkspace as Partial<VectorRagConfig>).rerank_model,
                };
            }

            const workspace = await apiService.createWorkspace({
                name: newWorkspaceName.trim(),
                description: newWorkspaceDescription.trim() || undefined,
                rag_config: finalRagConfig,
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
            {/* Logo */}
            <div className="flex items-center gap-3">
                <img src="/logo.png" alt="InsightHub" className="h-8 w-8 object-contain" />
                <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    InsightHub
                </span>
            </div>

            {/* Workspace Selector */}
            <WorkspaceHeader
                activeWorkspace={activeWorkspace}
                workspacesLoading={workspacesLoading}
                showWorkspaceDropdown={showWorkspaceDropdown}
                setShowWorkspaceDropdown={setShowWorkspaceDropdown}
            />

            {showWorkspaceDropdown && (
                <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-10 max-h-64 overflow-y-auto">
                    {workspacesLoading && (
                        <div className="p-4 text-center">
                            <LoadingSpinner size="sm" />
                        </div>
                    )}
                    {workspacesError && (
                        <div className="p-4 text-red-500 text-sm text-center">
                            {workspacesError}
                        </div>
                    )}
                    {!workspacesLoading && !workspacesError && workspaces.length === 0 ? (
                        <div className="p-4 text-sm text-gray-500 dark:text-gray-400 text-center">
                            No workspaces yet
                        </div>
                    ) : (
                        <div className="py-1">
                            {workspaces.map((workspace) => (
                                <button
                                    key={workspace.id}
                                    onClick={() => handleWorkspaceChange(workspace.id)}
                                    className={`w-full px-4 py-2.5 text-left text-sm transition-colors flex items-center justify-between gap-2 ${
                                        workspace.id === activeWorkspaceId
                                            ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                                    }`}
                                    disabled={isAnyWorkspaceDeleting}
                                >
                                    <span className="truncate">{workspace.name}</span>
                                    {workspace.status !== 'ready' && (
                                        <span
                                            className={`text-xs px-2 py-0.5 rounded-full ${
                                                workspace.status === 'provisioning'
                                                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                                                    : workspace.status === 'deleting'
                                                      ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
                                                      : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                                            }`}
                                        >
                                            {workspace.status}
                                        </span>
                                    )}
                                </button>
                            ))}
                        </div>
                    )}
                    <div className="border-t border-gray-100 dark:border-gray-700">
                        <button
                            onClick={() => {
                                setShowWorkspaceDropdown(false);
                                setShowCreateModal(true);
                            }}
                            className="w-full px-4 py-2.5 text-left text-sm text-blue-600 dark:text-blue-400 hover:bg-gray-50 dark:hover:bg-gray-700/50 flex items-center gap-2 transition-colors"
                            disabled={isAnyWorkspaceDeleting}
                        >
                            <FaPlus className="w-3 h-3" />
                            Create New Workspace
                        </button>
                        {activeWorkspaceId && (
                            <Link
                                to={`/workspaces/${activeWorkspaceId}`}
                                onClick={() => setShowWorkspaceDropdown(false)}
                                className="w-full px-4 py-2.5 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 flex items-center gap-2 transition-colors"
                                disabled={isAnyWorkspaceDeleting} // Disable settings link if any workspace is deleting
                            >
                                <FaCog className="w-4 h-4" />
                                Workspace Settings
                            </Link>
                        )}
                    </div>
                </div>
            )}

            {/* Create Workspace Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
                        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
                            Create New Workspace
                        </h2>
                        <form onSubmit={handleCreateWorkspace}>
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
                                            initialConfig={ragConfigForWorkspace}
                                            onConfigChange={setRagConfigForWorkspace}
                                        />
                                    </div>
                                )}
                            </div>

                            {/* Info about provisioning */}
                            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                <p className="text-sm text-blue-700 dark:text-blue-300">
                                    Creating a workspace will set up the required RAG
                                    infrastructure. This may take a moment.
                                </p>
                            </div>

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
                                    disabled={isCreating || !newWorkspaceName.trim()}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isCreating ? 'Creating...' : 'Create Workspace'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default WorkspaceColumn;
