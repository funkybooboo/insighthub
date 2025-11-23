import { useState, useEffect, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { FaPlus, FaChevronDown, FaFolderOpen } from 'react-icons/fa';
import type { RootState } from '@/store';
import { createSession, setActiveSession, deleteSession } from '@/store/slices/chatSlice';
import {
    setWorkspaces,
    setActiveWorkspace,
    addWorkspace,
    setLoading,
    setError,
} from '@/store/slices/workspaceSlice';
import { ConfirmDialog } from '@/components/shared';
import { apiService, type DefaultRagConfig } from '@/services/api';
import { validateWorkspaceName, validateDescription } from '@/lib/validation';

const DEFAULT_RAG_CONFIG: DefaultRagConfig = {
    embedding_model: 'nomic-embed-text',
    retriever_type: 'vector',
    chunk_size: 1000,
    chunk_overlap: 200,
    top_k: 8,
    rerank_enabled: false,
};

const ChatSidebar = () => {
    const dispatch = useDispatch();
    const { sessions, activeSessionId } = useSelector((state: RootState) => state.chat);
    const {
        workspaces,
        activeWorkspaceId,
        isLoading: workspacesLoading,
    } = useSelector((state: RootState) => state.workspace);

    const [deleteConfirm, setDeleteConfirm] = useState<{
        isOpen: boolean;
        sessionId: string | null;
    }>({
        isOpen: false,
        sessionId: null,
    });

    const [showWorkspaceDropdown, setShowWorkspaceDropdown] = useState(false);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newWorkspaceName, setNewWorkspaceName] = useState('');
    const [newWorkspaceDescription, setNewWorkspaceDescription] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [validationError, setValidationError] = useState<string | null>(null);
    const [ragConfig, setRagConfig] = useState<DefaultRagConfig>(DEFAULT_RAG_CONFIG);

    const activeWorkspace = workspaces.find((w) => w.id === activeWorkspaceId);

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

    const loadDefaultRagConfig = useCallback(async () => {
        try {
            const config = await apiService.getDefaultRagConfig();
            if (config) {
                setRagConfig(config);
            }
        } catch {
            // Use default config if none exists
        }
    }, []);

    useEffect(() => {
        loadWorkspaces();
    }, [loadWorkspaces]);

    useEffect(() => {
        if (showCreateModal) {
            loadDefaultRagConfig();
        }
    }, [showCreateModal, loadDefaultRagConfig]);

    const handleNewChat = () => {
        if (!activeWorkspaceId) return;
        const newSessionId = `session-${Date.now()}`;
        dispatch(createSession({ id: newSessionId }));
    };

    const handleSelectSession = (sessionId: string) => {
        dispatch(setActiveSession(sessionId));
    };

    const handleDeleteClick = (sessionId: string, event: React.MouseEvent) => {
        event.stopPropagation();
        setDeleteConfirm({ isOpen: true, sessionId });
    };

    const handleConfirmDelete = () => {
        if (deleteConfirm.sessionId) {
            dispatch(deleteSession(deleteConfirm.sessionId));
        }
        setDeleteConfirm({ isOpen: false, sessionId: null });
    };

    const handleCancelDelete = () => {
        setDeleteConfirm({ isOpen: false, sessionId: null });
    };

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
            // Create the workspace
            const workspace = await apiService.createWorkspace({
                name: newWorkspaceName.trim(),
                description: newWorkspaceDescription.trim() || undefined,
            });

            // Create RAG config for the workspace
            await apiService.createRagConfig(workspace.id, {
                embedding_model: ragConfig.embedding_model,
                retriever_type: ragConfig.retriever_type,
                chunk_size: ragConfig.chunk_size,
                chunk_overlap: ragConfig.chunk_overlap,
                top_k: ragConfig.top_k,
            });

            dispatch(addWorkspace(workspace));
            dispatch(setActiveWorkspace(workspace.id));
            setShowCreateModal(false);
            setNewWorkspaceName('');
            setNewWorkspaceDescription('');
            setValidationError(null);
            setRagConfig(DEFAULT_RAG_CONFIG);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to create workspace';
            setValidationError(message);
        } finally {
            setIsCreating(false);
        }
    };

    const formatDate = (timestamp: number): string => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;

        return date.toLocaleDateString();
    };

    return (
        <div className="w-72 bg-white dark:bg-gray-900 flex flex-col h-full border-r border-gray-200/80 dark:border-gray-800">
            {/* Header Section */}
            <div className="p-5 space-y-4">
                {/* Logo */}
                <div className="flex items-center gap-3">
                    <img src="/logo.png" alt="InsightHub" className="h-8 w-8 object-contain" />
                    <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        InsightHub
                    </span>
                </div>

                {/* Workspace Selector */}
                <div className="relative">
                    <button
                        onClick={() => setShowWorkspaceDropdown(!showWorkspaceDropdown)}
                        className="w-full flex items-center justify-between px-3 py-2.5 bg-gray-50 dark:bg-gray-800 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700/70 transition-colors border border-gray-200/60 dark:border-gray-700/50"
                        disabled={workspacesLoading}
                    >
                        <div className="flex items-center gap-2.5 min-w-0">
                            <FaFolderOpen className="text-blue-500 dark:text-blue-400 flex-shrink-0" />
                            <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                                {activeWorkspace?.name || 'Select Workspace'}
                            </span>
                        </div>
                        <FaChevronDown
                            className={`w-3 h-3 text-gray-400 transition-transform flex-shrink-0 ${
                                showWorkspaceDropdown ? 'rotate-180' : ''
                            }`}
                        />
                    </button>

                    {showWorkspaceDropdown && (
                        <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-10 max-h-64 overflow-y-auto overflow-hidden">
                            {workspaces.length === 0 ? (
                                <div className="p-4 text-sm text-gray-500 dark:text-gray-400 text-center">
                                    No workspaces yet
                                </div>
                            ) : (
                                <div className="py-1">
                                    {workspaces.map((workspace) => (
                                        <button
                                            key={workspace.id}
                                            onClick={() => handleWorkspaceChange(workspace.id)}
                                            className={`w-full px-4 py-2.5 text-left text-sm transition-colors ${
                                                workspace.id === activeWorkspaceId
                                                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'
                                                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                                            }`}
                                        >
                                            {workspace.name}
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
                                >
                                    <FaPlus className="w-3 h-3" />
                                    Create New Workspace
                                </button>
                            </div>
                        </div>
                    )}
                </div>

            </div>

            {/* Chat Sessions List */}
            <div className="flex-1 overflow-y-auto px-3 py-2">
                {sessions.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center px-4">
                        <div className="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-3">
                            <svg
                                className="w-6 h-6 text-gray-400 dark:text-gray-500"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={1.5}
                                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                                />
                            </svg>
                        </div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                            No chats yet
                        </p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                            Start a new conversation
                        </p>
                    </div>
                ) : (
                    <div className="space-y-1">
                        {sessions.map((session) => (
                            <div
                                key={session.id}
                                onClick={() => handleSelectSession(session.id)}
                                className={`group relative px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                                    activeSessionId === session.id
                                        ? 'bg-blue-50 dark:bg-blue-900/20'
                                        : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
                                }`}
                            >
                                <div className="flex items-start justify-between gap-2">
                                    <div className="flex-1 min-w-0">
                                        <h3
                                            className={`text-sm font-medium truncate ${
                                                activeSessionId === session.id
                                                    ? 'text-blue-700 dark:text-blue-300'
                                                    : 'text-gray-700 dark:text-gray-200'
                                            }`}
                                        >
                                            {session.title}
                                        </h3>
                                        <div className="flex items-center gap-1.5 mt-0.5 text-xs text-gray-400 dark:text-gray-500">
                                            <span>{session.messages.length} messages</span>
                                            <span className="text-gray-300 dark:text-gray-600">
                                                |
                                            </span>
                                            <span>{formatDate(session.updatedAt)}</span>
                                        </div>
                                    </div>
                                    <button
                                        onClick={(e) => handleDeleteClick(session.id, e)}
                                        className="opacity-0 group-hover:opacity-100 p-1.5 text-gray-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
                                        title="Delete chat"
                                    >
                                        <svg
                                            className="w-4 h-4"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                        >
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                                            />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="px-5 py-4 border-t border-gray-100 dark:border-gray-800 space-y-3">
                {/* New Chat Button */}
                <button
                    onClick={handleNewChat}
                    disabled={!activeWorkspaceId}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-sm"
                    title={!activeWorkspaceId ? 'Select a workspace first' : 'Create new chat'}
                >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 4v16m8-8H4"
                        />
                    </svg>
                    New Chat
                </button>
                {!activeWorkspaceId && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                        Select or create a workspace to start chatting
                    </p>
                )}
                <div className="text-xs text-gray-400 dark:text-gray-500 text-center">
                    {sessions.length} {sessions.length === 1 ? 'chat' : 'chats'} saved locally
                </div>
            </div>

            {/* Delete Confirmation Dialog */}
            <ConfirmDialog
                isOpen={deleteConfirm.isOpen}
                title="Delete Chat"
                message="Are you sure you want to delete this chat? This action cannot be undone."
                confirmLabel="Delete"
                variant="danger"
                onConfirm={handleConfirmDelete}
                onCancel={handleCancelDelete}
            />

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
                                    Workspace Name *
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
                                    rows={2}
                                />
                            </div>

                            {/* RAG Configuration */}
                            <div className="border-t border-gray-200 dark:border-gray-700 pt-4 mb-4">
                                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                                    RAG Configuration
                                </h3>

                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                            Embedding Model
                                        </label>
                                        <select
                                            value={ragConfig.embedding_model}
                                            onChange={(e) =>
                                                setRagConfig({
                                                    ...ragConfig,
                                                    embedding_model: e.target.value,
                                                })
                                            }
                                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                        >
                                            <option value="nomic-embed-text">
                                                Nomic Embed Text (Local)
                                            </option>
                                            <option value="text-embedding-ada-002">
                                                OpenAI Ada-002
                                            </option>
                                            <option value="all-MiniLM-L6-v2">
                                                Sentence Transformers MiniLM
                                            </option>
                                        </select>
                                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                                            Model used to convert text into vector embeddings
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                            Retriever Type
                                        </label>
                                        <select
                                            value={ragConfig.retriever_type}
                                            onChange={(e) =>
                                                setRagConfig({
                                                    ...ragConfig,
                                                    retriever_type: e.target.value,
                                                })
                                            }
                                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                        >
                                            <option value="vector">Vector RAG</option>
                                            <option value="graph">Graph RAG</option>
                                            <option value="hybrid">Hybrid RAG</option>
                                        </select>
                                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                                            The retrieval strategy for finding relevant documents
                                        </p>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                                Chunk Size
                                            </label>
                                            <input
                                                type="number"
                                                value={ragConfig.chunk_size}
                                                onChange={(e) =>
                                                    setRagConfig({
                                                        ...ragConfig,
                                                        chunk_size:
                                                            parseInt(e.target.value) || 1000,
                                                    })
                                                }
                                                min="100"
                                                max="5000"
                                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                                Chunk Overlap
                                            </label>
                                            <input
                                                type="number"
                                                value={ragConfig.chunk_overlap}
                                                onChange={(e) =>
                                                    setRagConfig({
                                                        ...ragConfig,
                                                        chunk_overlap:
                                                            parseInt(e.target.value) || 200,
                                                    })
                                                }
                                                min="0"
                                                max="1000"
                                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                            Top K Results
                                        </label>
                                        <input
                                            type="number"
                                            value={ragConfig.top_k}
                                            onChange={(e) =>
                                                setRagConfig({
                                                    ...ragConfig,
                                                    top_k: parseInt(e.target.value) || 8,
                                                })
                                            }
                                            min="1"
                                            max="50"
                                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                        />
                                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                                            Number of results to retrieve (1-50)
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div className="flex justify-end gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setShowCreateModal(false);
                                        setNewWorkspaceName('');
                                        setNewWorkspaceDescription('');
                                        setValidationError(null);
                                        setRagConfig(DEFAULT_RAG_CONFIG);
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

export default ChatSidebar;
