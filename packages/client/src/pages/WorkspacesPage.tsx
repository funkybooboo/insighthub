import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { AxiosError } from 'axios';
import { StatusBadge, LoadingSpinner } from '../components/shared';
import type { RootState } from '../store';
import type { WorkspaceStatus } from '../store/slices/statusSlice';
import type { Workspace as BaseWorkspace } from '../types/workspace';
import apiService from '../services/api';

interface WorkspaceWithStatus extends BaseWorkspace {
    status: WorkspaceStatus;
    status_message: string | null;
}

function getErrorMessage(error: unknown): string {
    if (error instanceof AxiosError) {
        return error.response?.data?.detail || error.message;
    }
    if (error instanceof Error) {
        return error.message;
    }
    return 'An unexpected error occurred';
}

export default function WorkspacesPage() {
    const statusUpdates = useSelector((state: RootState) => state.status.workspaces);
    const [workspaces, setWorkspaces] = useState<WorkspaceWithStatus[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newWorkspaceName, setNewWorkspaceName] = useState('');
    const [newWorkspaceDescription, setNewWorkspaceDescription] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [createError, setCreateError] = useState<string | null>(null);

    useEffect(() => {
        loadWorkspaces();
    }, []);

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

    const loadWorkspaces = async () => {
        try {
            setLoading(true);
            const data = await apiService.listWorkspaces();
            // Add default status for workspaces that don't have one
            const workspacesWithStatus: WorkspaceWithStatus[] = data.map((ws) => ({
                ...ws,
                status: 'ready' as WorkspaceStatus,
                status_message: null,
            }));
            setWorkspaces(workspacesWithStatus);
        } catch (err: unknown) {
            setError(getErrorMessage(err));
        } finally {
            setLoading(false);
        }
    };

    const handleCreateWorkspace = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newWorkspaceName.trim()) return;

        setIsCreating(true);
        setCreateError(null);

        try {
            const workspace = await apiService.createWorkspace({
                name: newWorkspaceName.trim(),
                description: newWorkspaceDescription.trim() || undefined,
            });

            const workspaceWithStatus: WorkspaceWithStatus = {
                ...workspace,
                status: 'provisioning',
                status_message: null,
            };

            setWorkspaces((prev) => [...prev, workspaceWithStatus]);
            setShowCreateModal(false);
            setNewWorkspaceName('');
            setNewWorkspaceDescription('');
        } catch (err: unknown) {
            setCreateError(getErrorMessage(err));
        } finally {
            setIsCreating(false);
        }
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
                                        Updated {new Date(workspace.updated_at).toLocaleDateString()}
                                    </span>
                                </div>

                                {workspace.status === 'provisioning' && (
                                    <div className="mt-4 text-sm text-blue-600 dark:text-blue-400">
                                        Setting up workspace infrastructure...
                                    </div>
                                )}

                                {workspace.status === 'error' && workspace.status_message && (
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
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
                        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
                            Create New Workspace
                        </h2>
                        <form onSubmit={handleCreateWorkspace}>
                            {createError && (
                                <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 rounded-lg text-sm">
                                    {createError}
                                </div>
                            )}
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Workspace Name
                                </label>
                                <input
                                    type="text"
                                    value={newWorkspaceName}
                                    onChange={(e) => {
                                        setNewWorkspaceName(e.target.value);
                                        setCreateError(null);
                                    }}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                    placeholder="e.g., Research Papers"
                                    maxLength={100}
                                    required
                                    autoFocus
                                />
                            </div>
                            <div className="mb-6">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Description (optional)
                                </label>
                                <textarea
                                    value={newWorkspaceDescription}
                                    onChange={(e) => {
                                        setNewWorkspaceDescription(e.target.value);
                                        setCreateError(null);
                                    }}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                    placeholder="What is this workspace for?"
                                    maxLength={500}
                                    rows={3}
                                />
                            </div>
                            <div className="flex justify-end gap-2">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowCreateModal(false);
                                        setNewWorkspaceName('');
                                        setNewWorkspaceDescription('');
                                        setCreateError(null);
                                    }}
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
                                    {isCreating ? 'Creating...' : 'Create'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
