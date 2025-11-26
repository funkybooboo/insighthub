import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Link } from 'react-router-dom';
import { AxiosError } from 'axios';
import { StatusBadge, LoadingSpinner } from '../components/shared';
import type { RootState, AppDispatch } from '../store';
import {
    fetchDefaultRagConfig,
    selectDefaultRagConfig,
    selectUserSettingsLoading,
} from '../store/slices/userSettingsSlice';
import type { WorkspaceStatus } from '../store/slices/statusSlice';
import { type Workspace as BaseWorkspace } from '../types/workspace';
import apiService from '../services/api';
import RagConfigForm from '../components/workspace/RagConfigForm'; // Import the new component

interface WorkspaceWithStatus extends Omit<BaseWorkspace, 'status'> {
    status: WorkspaceStatus;
    status_message: string | null;
}

function getErrorMessage(error: unknown): string {
    if (error instanceof AxiosError) {
        return error.response?.data?.message || error.message;
    }
    if (error instanceof Error) {
        return error.message;
    }
    return 'An unexpected error occurred';
}

// Simple hook to temporarily prevent view movement during button interactions
function usePreventViewMovement() {
    const preventMovement = useCallback(() => {
        // Store current position
        const currentX = window.scrollX;
        const currentY = window.scrollY;

        // Prevent scroll for a short duration
        const preventScroll = (e: Event) => {
            e.preventDefault();
            window.scrollTo(currentX, currentY);
        };

        // Add temporary listeners
        document.addEventListener('scroll', preventScroll, { once: true, passive: false });
        document.addEventListener('wheel', preventScroll, { once: true, passive: false });

        // Auto-remove after short delay
        setTimeout(() => {
            document.removeEventListener('scroll', preventScroll);
            document.removeEventListener('wheel', preventScroll);
        }, 100);
    }, []);

    return { preventMovement };
}

export default function WorkspacesPage() {
    const dispatch = useDispatch<AppDispatch>();
    const statusUpdates = useSelector((state: RootState) => state.status.workspaces);
    const defaultRagConfig = useSelector(selectDefaultRagConfig);
    const loadingDefaultRagConfig = useSelector(selectUserSettingsLoading);

    const [workspaces, setWorkspaces] = useState<WorkspaceWithStatus[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newWorkspaceName, setNewWorkspaceName] = useState('');
    const [newWorkspaceDescription, setNewWorkspaceDescription] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [createError, setCreateError] = useState<string | null>(null);

    // RAG config state for create modal (local state, pre-populated by defaultRagConfig)
    const [ragConfigForWorkspace, setRagConfigForWorkspace] = useState<Partial<VectorRagConfig>>(
        {}
    );
    const [showAdvancedConfig, setShowAdvancedConfig] = useState(false);

    // Prevent view movement during interactions
    const { preventMovement } = usePreventViewMovement();

    const loadWorkspaces = useCallback(async () => {
        try {
            setLoading(true);
            const data = await apiService.listWorkspaces();
            // Add default status for workspaces that don't have one
            const workspacesWithStatus: WorkspaceWithStatus[] = data.map((ws) => ({
                ...ws,
                status: ws.status || 'ready', // Use existing status or default to 'ready'
                status_message: null,
            }));
            setWorkspaces(workspacesWithStatus);
        } catch (err: unknown) {
            setError(getErrorMessage(err));
        } finally {
            setLoading(false);
        }
    }, []);

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
            // For now, assume it's VectorRagConfig (we only support vector RAG)
            setRagConfigForWorkspace(defaultRagConfig as VectorRagConfig);
        }
    }, [defaultRagConfig]);

    // Update workspace status when real-time update received
    useEffect(() => {
        setWorkspaces((prev) =>
            prev.map((ws) => {
                const update = statusUpdates[ws.id];
                if (update) {
                    return {
                        ...ws,
                        status: update.status,
                        status_message: update.message,
                    };
                }
                return ws;
            })
        );
    }, [statusUpdates]);

    const handleCreateWorkspace = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newWorkspaceName.trim()) return;

        setIsCreating(true);
        setCreateError(null);

        try {
            // Build RAG config in the format expected by server
            const ragConfig = {
                embedding_algorithm:
                    ragConfigForWorkspace.embedding_algorithm || 'nomic-embed-text',
                chunking_algorithm: ragConfigForWorkspace.chunking_algorithm || 'sentence',
                rerank_algorithm: ragConfigForWorkspace.rerank_enabled
                    ? ragConfigForWorkspace.rerank_algorithm ||
                      'cross-encoder/ms-marco-MiniLM-L-6-v2'
                    : 'none',
                chunk_size: ragConfigForWorkspace.chunk_size || 1000,
                chunk_overlap: ragConfigForWorkspace.chunk_overlap || 200,
                top_k: ragConfigForWorkspace.top_k || 8,
            };

            const workspace = await apiService.createWorkspace({
                name: newWorkspaceName.trim(),
                description: newWorkspaceDescription.trim() || undefined,
                rag_type: 'vector', // Default to vector for now
                rag_config: ragConfig,
            });

            const workspaceWithStatus: WorkspaceWithStatus = {
                ...workspace,
                status: 'provisioning', // New workspaces start in provisioning
                status_message: null,
            };

            setWorkspaces((prev) => [...prev, workspaceWithStatus]);
            handleCloseModal();
        } catch (err: unknown) {
            setCreateError(getErrorMessage(err));
        } finally {
            setIsCreating(false);
        }
    };

    const handleCloseModal = () => {
        setShowCreateModal(false);
        setNewWorkspaceName('');
        setNewWorkspaceDescription('');
        setRagConfigForWorkspace({}); // Reset local config state
        setShowAdvancedConfig(false);
        setCreateError(null);
        setHasUnsavedChanges(false); // Reset unsaved changes state
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
                <div className="text-center">
                    <LoadingSpinner size="lg" />
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading workspaces...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
                <div className="text-center text-red-600 dark:text-red-400">
                    <p>Error: {error}</p>
                    <button
                        onClick={loadWorkspaces}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                            Workspaces
                        </h1>
                        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                            Organize your documents and chats into separate workspaces
                        </p>
                    </div>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors"
                    >
                        Create Workspace
                    </button>
                </div>

                {/* Workspaces Grid */}
                {workspaces.length === 0 ? (
                    <div className="text-center py-12 bg-white dark:bg-gray-900 rounded-lg shadow">
                        <p className="text-gray-500 dark:text-gray-400">
                            No workspaces yet. Create one to get started!
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {workspaces.map((workspace) => (
                            <Link
                                key={workspace.id}
                                to={`/workspaces/${workspace.id}`}
                                className="block bg-white dark:bg-gray-900 rounded-lg shadow hover:shadow-lg transition-shadow p-6"
                            >
                                <div className="flex justify-between items-start mb-4">
                                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                                        {workspace.name}
                                    </h3>
                                    <StatusBadge
                                        status={workspace.status}
                                        message={workspace.status_message || undefined}
                                    />
                                </div>

                                {workspace.description && (
                                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-4">
                                        {workspace.description}
                                    </p>
                                )}

                                <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                                    <span>{workspace.document_count ?? 0} documents</span>
                                    <span>
                                        Updated{' '}
                                        {new Date(workspace.updated_at).toLocaleDateString()}
                                    </span>
                                </div>

                                {workspace.status === 'provisioning' && (
                                    <div className="mt-4 text-sm text-blue-600 dark:text-blue-400">
                                        Setting up workspace infrastructure...
                                    </div>
                                )}

                                {workspace.status === 'failed' && workspace.status_message && (
                                    <div className="mt-4 text-sm text-red-600 dark:text-red-400">
                                        Error: {workspace.status_message}
                                    </div>
                                )}
                            </Link>
                        ))}
                    </div>
                )}
            </div>

            {/* Create Workspace Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 backdrop-blur-sm">
                    <div
                        className="bg-white dark:bg-gray-800 rounded-xl p-8 w-full max-w-2xl mx-4 max-h-[95vh] overflow-y-auto shadow-2xl border-2 border-gray-200 dark:border-gray-700 relative"
                        style={{ scrollBehavior: 'auto', overflowAnchor: 'none' }}
                    >
                        {/* Header with title, unsaved changes indicator, and close button */}
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                                Create New Workspace
                            </h2>
                            <div className="flex items-center gap-3">
                                {/* Unsaved changes indicator */}
                                {hasUnsavedChanges && (
                                    <div className="flex items-center gap-2 px-3 py-1.5 bg-orange-500 text-white rounded-lg shadow-md">
                                        <svg
                                            className="w-4 h-4"
                                            fill="currentColor"
                                            viewBox="0 0 20 20"
                                        >
                                            <path
                                                fillRule="evenodd"
                                                d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                                                clipRule="evenodd"
                                            />
                                        </svg>
                                        <span className="text-sm font-semibold">
                                            Unsaved Changes
                                        </span>
                                    </div>
                                )}
                                {/* Close button */}
                                <button
                                    onClick={(e) => {
                                        e.preventDefault();
                                        preventMovement();
                                        handleCloseModal();
                                    }}
                                    className="p-2 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                                    disabled={isCreating}
                                >
                                    <svg
                                        className="w-5 h-5"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M6 18L18 6M6 6l12 12"
                                        />
                                    </svg>
                                </button>
                            </div>
                        </div>
                        <form onSubmit={handleCreateWorkspace}>
                            {createError && (
                                <div className="mb-6 p-4 bg-red-100 dark:bg-red-950 border-2 border-red-500 dark:border-red-600 rounded-lg shadow-lg">
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
                                                Creation Error
                                            </h3>
                                            <div className="mt-2 text-sm text-red-800 dark:text-red-200">
                                                <p>{createError}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Basic Info */}
                            <div className="mb-6">
                                <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">
                                    Workspace Name
                                </label>
                                <input
                                    type="text"
                                    value={newWorkspaceName}
                                    onChange={(e) => {
                                        setNewWorkspaceName(e.target.value);
                                        setCreateError(null);
                                    }}
                                    className="w-full px-4 py-3 border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-base"
                                    placeholder="e.g., Research Papers"
                                    maxLength={100}
                                    required
                                    autoFocus
                                />
                                <p className="mt-2 text-xs text-gray-600 dark:text-gray-400 font-medium">
                                    Choose a descriptive name for your workspace
                                </p>
                            </div>
                            <div className="mb-6">
                                <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">
                                    Description (optional)
                                </label>
                                <textarea
                                    value={newWorkspaceDescription}
                                    onChange={(e) => {
                                        setNewWorkspaceDescription(e.target.value);
                                        setCreateError(null);
                                    }}
                                    className="w-full px-4 py-3 border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-base resize-none"
                                    placeholder="What is this workspace for?"
                                    maxLength={500}
                                    rows={3}
                                />
                                <p className="mt-2 text-xs text-gray-600 dark:text-gray-400 font-medium">
                                    Briefly describe the purpose of this workspace
                                </p>
                            </div>

                            {/* RAG Configuration */}
                            <div className="border-t-2 border-gray-300 dark:border-gray-600 pt-6 mt-6">
                                <button
                                    type="button"
                                    onClick={(e) => {
                                        e.preventDefault();
                                        preventMovement();
                                        setShowAdvancedConfig(!showAdvancedConfig);
                                    }}
                                    className="flex items-center justify-between w-full text-left p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border-2 border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-500 transition-all duration-200 group"
                                >
                                    <div>
                                        <span className="text-lg font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-700 dark:group-hover:text-blue-300 transition-colors">
                                            RAG Configuration
                                        </span>
                                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 font-medium">
                                            {showAdvancedConfig
                                                ? 'Configure retrieval settings for this workspace'
                                                : 'Using your default settings. Click to customize.'}
                                        </p>
                                    </div>
                                    <svg
                                        className={`h-6 w-6 text-gray-600 dark:text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-all duration-200 transform ${
                                            showAdvancedConfig ? 'rotate-180' : ''
                                        }`}
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M19 9l-7 7-7-7"
                                        />
                                    </svg>
                                </button>

                                {loadingDefaultRagConfig && (
                                    <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-950 border-2 border-blue-300 dark:border-blue-600 rounded-lg">
                                        <div className="flex items-center gap-3">
                                            <svg
                                                className="animate-spin h-5 w-5 text-blue-600 dark:text-blue-400"
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
                                            <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                                                Loading default configuration...
                                            </span>
                                        </div>
                                    </div>
                                )}

                                {showAdvancedConfig && !loadingDefaultRagConfig && (
                                    <div
                                        className="mt-6 p-6 bg-gray-50 dark:bg-gray-800/50 rounded-lg border-2 border-gray-200 dark:border-gray-700"
                                        style={{ contain: 'layout' }}
                                    >
                                        <RagConfigForm
                                            initialConfig={ragConfigForWorkspace}
                                            onConfigChange={setRagConfigForWorkspace}
                                        />
                                    </div>
                                )}
                            </div>

                            {/* Info about provisioning */}
                            <div className="mt-6 p-4 bg-blue-100 dark:bg-blue-950 border-2 border-blue-400 dark:border-blue-600 rounded-lg shadow-sm">
                                <div className="flex items-start gap-3">
                                    <svg
                                        className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                    <div>
                                        <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-1">
                                            Workspace Setup
                                        </h4>
                                        <p className="text-sm text-blue-800 dark:text-blue-200">
                                            Creating a workspace will set up the required RAG
                                            infrastructure. This may take a moment to provision the
                                            necessary resources.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-end mt-8 pt-6 border-t-2 border-gray-200 dark:border-gray-700">
                                <button
                                    type="submit"
                                    disabled={isCreating || !newWorkspaceName.trim()}
                                    onClick={preventMovement}
                                    className="px-8 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center"
                                >
                                    {isCreating && (
                                        <svg
                                            className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
                                    {isCreating ? 'Creating Workspace...' : 'Create Workspace'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
