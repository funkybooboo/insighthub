import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { AxiosError } from 'axios';
import { LoadingSpinner, ConfirmDialog } from '../components/shared';
import apiService from '../services/api';
import type { Workspace } from '../types/workspace';
import { setActiveWorkspace } from '../store/slices/workspaceSlice';

function getErrorMessage(error: unknown): string {
    if (error instanceof AxiosError) {
        return error.response?.data?.detail || error.message;
    }
    if (error instanceof Error) {
        return error.message;
    }
    return 'An unexpected error occurred';
}

export default function WorkspaceDetailPage() {
    const { workspaceId } = useParams<{ workspaceId: string }>();
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const [workspace, setWorkspace] = useState<Workspace | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    useEffect(() => {
        if (workspaceId) {
            loadWorkspace(parseInt(workspaceId, 10));
        }
    }, [workspaceId]);

    const loadWorkspace = async (id: number) => {
        try {
            setLoading(true);
            const data = await apiService.getWorkspace(id);
            setWorkspace(data);
        } catch (err: unknown) {
            setError(getErrorMessage(err));
        } finally {
            setLoading(false);
        }
    };

    const handleOpenInChat = () => {
        if (workspace) {
            dispatch(setActiveWorkspace(workspace.id));
            navigate('/');
        }
    };

    const handleConfirmDelete = async () => {
        if (!workspace) return;

        setIsDeleting(true);
        try {
            await apiService.deleteWorkspace(workspace.id);
            navigate('/workspaces');
        } catch (err: unknown) {
            setError(getErrorMessage(err));
            setShowDeleteConfirm(false);
        } finally {
            setIsDeleting(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
                <div className="text-center">
                    <LoadingSpinner size="lg" />
                    <p className="mt-4 text-gray-600 dark:text-gray-400">Loading workspace...</p>
                </div>
            </div>
        );
    }

    if (error || !workspace) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-600 dark:text-red-400 mb-4">
                        {error || 'Workspace not found'}
                    </p>
                    <Link
                        to="/workspaces"
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        Back to Workspaces
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
            <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                {/* Breadcrumb */}
                <nav className="mb-6">
                    <Link
                        to="/workspaces"
                        className="text-blue-600 dark:text-blue-400 hover:underline"
                    >
                        Workspaces
                    </Link>
                    <span className="mx-2 text-gray-400">/</span>
                    <span className="text-gray-900 dark:text-white">{workspace.name}</span>
                </nav>

                {/* Header */}
                <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 mb-6">
                    <div className="flex justify-between items-start">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                {workspace.name}
                            </h1>
                            {workspace.description && (
                                <p className="mt-2 text-gray-600 dark:text-gray-400">
                                    {workspace.description}
                                </p>
                            )}
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={handleOpenInChat}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors"
                            >
                                Open in Chat
                            </button>
                            <button
                                onClick={() => setShowDeleteConfirm(true)}
                                disabled={isDeleting}
                                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md font-medium transition-colors disabled:opacity-50"
                            >
                                {isDeleting ? 'Deleting...' : 'Delete'}
                            </button>
                        </div>
                    </div>

                    <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Documents</p>
                            <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                                {workspace.document_count ?? 0}
                            </p>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Chat Sessions</p>
                            <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                                {workspace.session_count ?? 0}
                            </p>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Created</p>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {new Date(workspace.created_at).toLocaleDateString()}
                            </p>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Updated</p>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {new Date(workspace.updated_at).toLocaleDateString()}
                            </p>
                        </div>
                    </div>
                </div>

                {/* RAG Configuration */}
                {workspace.rag_config && (
                    <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6">
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                            RAG Configuration
                        </h2>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                            <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Embedding Model
                                </p>
                                <p className="font-medium text-gray-900 dark:text-white">
                                    {workspace.rag_config.embedding_model}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Retriever Type
                                </p>
                                <p className="font-medium text-gray-900 dark:text-white">
                                    {workspace.rag_config.retriever_type}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Chunk Size</p>
                                <p className="font-medium text-gray-900 dark:text-white">
                                    {workspace.rag_config.chunk_size}
                                </p>
                            </div>
                            {workspace.rag_config.chunk_overlap !== undefined && (
                                <div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">
                                        Chunk Overlap
                                    </p>
                                    <p className="font-medium text-gray-900 dark:text-white">
                                        {workspace.rag_config.chunk_overlap}
                                    </p>
                                </div>
                            )}
                            {workspace.rag_config.top_k !== undefined && (
                                <div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">Top K</p>
                                    <p className="font-medium text-gray-900 dark:text-white">
                                        {workspace.rag_config.top_k}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Delete Confirmation Dialog */}
            <ConfirmDialog
                isOpen={showDeleteConfirm}
                title="Delete Workspace"
                message={`Are you sure you want to delete "${workspace.name}"? All documents and chat sessions in this workspace will be permanently deleted.`}
                confirmLabel="Delete Workspace"
                variant="danger"
                onConfirm={handleConfirmDelete}
                onCancel={() => setShowDeleteConfirm(false)}
            />
        </div>
    );
}
