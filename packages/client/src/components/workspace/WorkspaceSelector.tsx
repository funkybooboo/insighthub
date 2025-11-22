import { useEffect, useState, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { FaPlus, FaFolderOpen } from 'react-icons/fa';
import type { RootState } from '../../store';
import {
    setWorkspaces,
    setActiveWorkspace,
    addWorkspace,
    setLoading,
    setError,
} from '../../store/slices/workspaceSlice';
import { apiService } from '../../services/api';
import { validateWorkspaceName, validateDescription } from '../../lib/validation';

const WorkspaceSelector = () => {
    const dispatch = useDispatch();
    const { workspaces, activeWorkspaceId, isLoading } = useSelector(
        (state: RootState) => state.workspace
    );
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newWorkspaceName, setNewWorkspaceName] = useState('');
    const [newWorkspaceDescription, setNewWorkspaceDescription] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [validationError, setValidationError] = useState<string | null>(null);

    const loadWorkspaces = useCallback(async () => {
        dispatch(setLoading(true));
        try {
            const workspaceList = await apiService.listWorkspaces();
            dispatch(setWorkspaces(workspaceList));

            if (workspaceList.length > 0 && !activeWorkspaceId) {
                dispatch(setActiveWorkspace(workspaceList[0].id));
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to load workspaces';
            dispatch(setError(message));
        }
    }, [dispatch, activeWorkspaceId]);

    useEffect(() => {
        loadWorkspaces();
    }, [loadWorkspaces]);

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
            });
            dispatch(addWorkspace(workspace));
            setShowCreateModal(false);
            setNewWorkspaceName('');
            setNewWorkspaceDescription('');
            setValidationError(null);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to create workspace';
            dispatch(setError(message));
        } finally {
            setIsCreating(false);
        }
    };

    const handleWorkspaceChange = (workspaceId: number) => {
        dispatch(setActiveWorkspace(workspaceId));
    };

    return (
        <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            <FaFolderOpen className="text-gray-500 dark:text-gray-400" />
            <select
                value={activeWorkspaceId || ''}
                onChange={(e) => handleWorkspaceChange(Number(e.target.value))}
                disabled={isLoading || workspaces.length === 0}
                className="flex-1 bg-transparent border-0 text-sm font-medium text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-0"
            >
                {workspaces.length === 0 ? (
                    <option value="">No workspaces</option>
                ) : (
                    workspaces.map((workspace) => (
                        <option key={workspace.id} value={workspace.id}>
                            {workspace.name}
                        </option>
                    ))
                )}
            </select>
            <button
                onClick={() => setShowCreateModal(true)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                title="Create new workspace"
            >
                <FaPlus className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>

            {showCreateModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
                        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
                            Create New Workspace
                        </h2>
                        <form onSubmit={handleCreateWorkspace}>
                            {validationError && (
                                <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 rounded-lg text-sm">
                                    {validationError}
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
                                        setValidationError(null);
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
                                        setValidationError(null);
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
                                        setValidationError(null);
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
};

export default WorkspaceSelector;
