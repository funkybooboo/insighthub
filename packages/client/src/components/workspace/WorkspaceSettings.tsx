import { useState, useEffect, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { FaCog, FaTrash } from 'react-icons/fa';
import type { RootState } from '../../store';
import { removeWorkspace, updateWorkspace, setError } from '../../store/slices/workspaceSlice';
import { apiService } from '../../services/api';
import type { RagConfig } from '../../types/workspace';

const WorkspaceSettings = () => {
    const dispatch = useDispatch();
    const { workspaces, activeWorkspaceId } = useSelector((state: RootState) => state.workspace);
    const [showModal, setShowModal] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [ragConfig, setRagConfig] = useState<RagConfig | null>(null);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        embedding_model: 'nomic-embed-text',
        retriever_type: 'vector',
        chunk_size: 1000,
        chunk_overlap: 200,
        top_k: 5,
    });

    const activeWorkspace = workspaces.find((w) => w.id === activeWorkspaceId);

    const loadRagConfig = useCallback(async () => {
        if (!activeWorkspaceId) return;

        try {
            const config = await apiService.getRagConfig(activeWorkspaceId);
            setRagConfig(config);
            setFormData((prev) => ({
                ...prev,
                embedding_model: config.embedding_model,
                retriever_type: config.retriever_type,
                chunk_size: config.chunk_size,
                chunk_overlap: config.chunk_overlap || 200,
                top_k: config.top_k || 5,
            }));
        } catch {
            console.log('No RAG config found, will create on save');
        }
    }, [activeWorkspaceId]);

    useEffect(() => {
        if (showModal && activeWorkspace) {
            setFormData({
                name: activeWorkspace.name,
                description: activeWorkspace.description || '',
                embedding_model: ragConfig?.embedding_model || 'nomic-embed-text',
                retriever_type: ragConfig?.retriever_type || 'vector',
                chunk_size: ragConfig?.chunk_size || 1000,
                chunk_overlap: ragConfig?.chunk_overlap || 200,
                top_k: ragConfig?.top_k || 5,
            });
            loadRagConfig();
        }
    }, [showModal, activeWorkspace, ragConfig, loadRagConfig]);

    const handleSave = async () => {
        if (!activeWorkspaceId) return;

        setIsLoading(true);
        try {
            const updatedWorkspace = await apiService.updateWorkspace(activeWorkspaceId, {
                name: formData.name,
                description: formData.description || undefined,
            });
            dispatch(updateWorkspace(updatedWorkspace));

            if (ragConfig) {
                await apiService.updateRagConfig(activeWorkspaceId, {
                    embedding_model: formData.embedding_model,
                    retriever_type: formData.retriever_type,
                    chunk_size: formData.chunk_size,
                    chunk_overlap: formData.chunk_overlap,
                    top_k: formData.top_k,
                });
            } else {
                await apiService.createRagConfig(activeWorkspaceId, {
                    embedding_model: formData.embedding_model,
                    retriever_type: formData.retriever_type,
                    chunk_size: formData.chunk_size,
                    chunk_overlap: formData.chunk_overlap,
                    top_k: formData.top_k,
                });
            }

            setShowModal(false);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to save settings';
            dispatch(setError(message));
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!activeWorkspaceId || !activeWorkspace) return;

        const confirmed = window.confirm(
            `Are you sure you want to delete workspace "${activeWorkspace.name}"? This will delete all documents and chat sessions.`
        );
        if (!confirmed) return;

        setIsLoading(true);
        try {
            await apiService.deleteWorkspace(activeWorkspaceId);
            dispatch(removeWorkspace(activeWorkspaceId));
            setShowModal(false);
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Failed to delete workspace';
            dispatch(setError(message));
        } finally {
            setIsLoading(false);
        }
    };

    if (!activeWorkspace) return null;

    return (
        <>
            <button
                onClick={() => setShowModal(true)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                title="Workspace settings"
            >
                <FaCog className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>

            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
                        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
                            Workspace Settings
                        </h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Workspace Name
                                </label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) =>
                                        setFormData({ ...formData, name: e.target.value })
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Description
                                </label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) =>
                                        setFormData({ ...formData, description: e.target.value })
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                    rows={3}
                                />
                            </div>

                            <hr className="border-gray-300 dark:border-gray-600" />

                            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                                RAG Configuration
                            </h3>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Embedding Model
                                </label>
                                <select
                                    value={formData.embedding_model}
                                    onChange={(e) =>
                                        setFormData({
                                            ...formData,
                                            embedding_model: e.target.value,
                                        })
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                >
                                    <option value="nomic-embed-text">Nomic Embed Text</option>
                                    <option value="openai">OpenAI</option>
                                    <option value="sentence-transformer">
                                        Sentence Transformer
                                    </option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Retriever Type
                                </label>
                                <select
                                    value={formData.retriever_type}
                                    onChange={(e) =>
                                        setFormData({ ...formData, retriever_type: e.target.value })
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                >
                                    <option value="vector">Vector RAG</option>
                                    <option value="graph">Graph RAG</option>
                                </select>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                        Chunk Size
                                    </label>
                                    <input
                                        type="number"
                                        value={formData.chunk_size}
                                        onChange={(e) =>
                                            setFormData({
                                                ...formData,
                                                chunk_size: parseInt(e.target.value),
                                            })
                                        }
                                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                        min="100"
                                        max="5000"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                        Chunk Overlap
                                    </label>
                                    <input
                                        type="number"
                                        value={formData.chunk_overlap}
                                        onChange={(e) =>
                                            setFormData({
                                                ...formData,
                                                chunk_overlap: parseInt(e.target.value),
                                            })
                                        }
                                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                        min="0"
                                        max="1000"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Top K Results
                                </label>
                                <input
                                    type="number"
                                    value={formData.top_k}
                                    onChange={(e) =>
                                        setFormData({
                                            ...formData,
                                            top_k: parseInt(e.target.value),
                                        })
                                    }
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100"
                                    min="1"
                                    max="20"
                                />
                            </div>
                        </div>

                        <div className="flex justify-between mt-6 pt-6 border-t border-gray-300 dark:border-gray-600">
                            <button
                                onClick={handleDelete}
                                disabled={isLoading}
                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                            >
                                <FaTrash />
                                Delete Workspace
                            </button>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setShowModal(false)}
                                    disabled={isLoading}
                                    className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSave}
                                    disabled={isLoading || !formData.name.trim()}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {isLoading ? 'Saving...' : 'Save Changes'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default WorkspaceSettings;
