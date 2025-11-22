import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { AxiosError } from 'axios';
import { LoadingSpinner, ConfirmDialog, StatusBadge } from '../components/shared';
import DocumentList, { type DocumentListRef } from '../components/upload/DocumentList';
import FileUpload from '../components/upload/FileUpload';
import apiService from '../services/api';
import type { Workspace } from '../types/workspace';
import { setActiveWorkspace } from '../store/slices/workspaceSlice';
import type { RootState } from '../store';
import type { WorkspaceStatus } from '../store/slices/statusSlice';

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


    // Edit workspace modal state
    const [showEditModal, setShowEditModal] = useState(false);
    const [editName, setEditName] = useState('');
    const [editDescription, setEditDescription] = useState('');
    const [savingWorkspace, setSavingWorkspace] = useState(false);
    const [editError, setEditError] = useState<string | null>(null);

    // Document list ref for refreshing
    const documentListRef = useRef<DocumentListRef>(null);

    // Get real-time workspace status from Redux
    const workspaceStatusUpdates = useSelector((state: RootState) => state.status.workspaces);
    const workspaceStatus: WorkspaceStatus = workspaceId
        ? workspaceStatusUpdates[parseInt(workspaceId, 10)]?.status || 'ready'
        : 'ready';

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

            // Initialize edit form
            setEditName(data.name);
            setEditDescription(data.description || '');
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

    const handleSaveWorkspace = async () => {
        if (!workspace) return;

        setSavingWorkspace(true);
        setEditError(null);

        try {
            const updated = await apiService.updateWorkspace(workspace.id, {
                name: editName.trim(),
                description: editDescription.trim() || undefined,
            });
            setWorkspace(updated);
            setShowEditModal(false);
        } catch (err: unknown) {
            setEditError(getErrorMessage(err));
        } finally {
            setSavingWorkspace(false);
        }
    };

    const handleDocumentChange = () => {
        // Refresh document list
        documentListRef.current?.refresh();
        // Reload workspace to get updated document count
        if (workspaceId) {
            loadWorkspace(parseInt(workspaceId, 10));
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

    const parsedWorkspaceId = parseInt(workspaceId!, 10);

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
            <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
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
                        <div className="flex items-start gap-4">
                            <div>
                                <div className="flex items-center gap-3">
                                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                        {workspace.name}
                                    </h1>
                                    <StatusBadge status={workspaceStatus} size="md" />
                                </div>
                                {workspace.description && (
                                    <p className="mt-2 text-gray-600 dark:text-gray-400">
                                        {workspace.description}
                                    </p>
                                )}
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setShowEditModal(true)}
                                className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md font-medium transition-colors"
                            >
                                Edit
                            </button>
                            <button
                                onClick={handleOpenInChat}
                                disabled={workspaceStatus !== 'ready'}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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

                    {/* Status message for provisioning */}
                    {workspaceStatus === 'provisioning' && (
                        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                            <div className="flex items-center gap-3">
                                <LoadingSpinner size="sm" />
                                <div>
                                    <p className="font-medium text-blue-700 dark:text-blue-300">
                                        Setting up workspace...
                                    </p>
                                    <p className="text-sm text-blue-600 dark:text-blue-400">
                                        Creating RAG infrastructure. This may take a minute.
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {workspaceStatus === 'error' && (
                        <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                            <p className="font-medium text-red-700 dark:text-red-300">
                                Workspace setup failed
                            </p>
                            <p className="text-sm text-red-600 dark:text-red-400">
                                There was an error setting up this workspace. Please try again or contact support.
                            </p>
                        </div>
                    )}

                    {/* Stats Grid */}
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

                {/* RAG Configuration (Read-only - set at workspace creation) */}
                <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 mb-6">
                    <div className="mb-4">
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                            RAG Configuration
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            Configuration is set when the workspace is created and cannot be changed.
                        </p>
                    </div>

                    {workspace.rag_config ? (
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
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
                            <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Chunk Overlap
                                </p>
                                <p className="font-medium text-gray-900 dark:text-white">
                                    {workspace.rag_config.chunk_overlap ?? 'N/A'}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Top K</p>
                                <p className="font-medium text-gray-900 dark:text-white">
                                    {workspace.rag_config.top_k ?? 'N/A'}
                                </p>
                            </div>
                        </div>
                    ) : (
                        <p className="text-gray-500 dark:text-gray-400">
                            No RAG configuration available for this workspace.
                        </p>
                    )}
                </div>

                {/* Documents Section */}
                <div className="bg-white dark:bg-gray-900 rounded-lg shadow overflow-hidden">
                    <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                            Documents
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            Upload and manage documents for this workspace
                        </p>
                    </div>

                    <FileUpload
                        workspaceId={parsedWorkspaceId}
                        onUploadSuccess={handleDocumentChange}
                    />

                    <DocumentList
                        ref={documentListRef}
                        workspaceId={parsedWorkspaceId}
                        onDocumentChange={handleDocumentChange}
                    />
                </div>
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

            {/* Edit Workspace Modal */}
            {showEditModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
                        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
                            Edit Workspace
                        </h2>
                        <form onSubmit={(e) => { e.preventDefault(); handleSaveWorkspace(); }}>
                            {editError && (
                                <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 rounded-lg text-sm">
                                    {editError}
                                </div>
                            )}
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Workspace Name
                                </label>
                                <input
                                    type="text"
                                    value={editName}
                                    onChange={(e) => setEditName(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                    maxLength={100}
                                    required
                                />
                            </div>
                            <div className="mb-6">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Description (optional)
                                </label>
                                <textarea
                                    value={editDescription}
                                    onChange={(e) => setEditDescription(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                    maxLength={500}
                                    rows={3}
                                />
                            </div>
                            <div className="flex justify-end gap-2">
                                <button
                                    type="button"
                                    onClick={() => setShowEditModal(false)}
                                    className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                                    disabled={savingWorkspace}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={savingWorkspace || !editName.trim()}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {savingWorkspace ? 'Saving...' : 'Save'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

        </div>
    );
}
