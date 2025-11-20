import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { StatusBadge, LoadingSpinner } from '../components/shared';
import type { RootState } from '../store';
import type { WorkspaceStatus } from '../store/slices/statusSlice';
import api from '../services/api';

interface Workspace {
    id: number;
    name: string;
    description: string | null;
    created_at: string;
    updated_at: string;
    document_count: number;
    status: WorkspaceStatus;
    status_message: string | null;
}

export default function WorkspacesPage() {
    const { token } = useSelector((state: RootState) => state.auth);
    const statusUpdates = useSelector((state: RootState) => state.status.workspaces);
    const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

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
            const response = await api.get('/workspaces', {
                headers: { Authorization: `Bearer ${token}` },
            });
            setWorkspaces(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load workspaces');
        } finally {
            setLoading(false);
        }
    };

    const createWorkspace = async () => {
        try {
            const name = prompt('Enter workspace name:');
            if (!name) return;

            const description = prompt('Enter workspace description (optional):');

            const response = await api.post(
                '/workspaces',
                { name, description },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            setWorkspaces((prev) => [...prev, response.data]);
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to create workspace');
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
                        onClick={createWorkspace}
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
                                    <span>{workspace.document_count} documents</span>
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
        </div>
    );
}
