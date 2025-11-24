import { useState, useEffect, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { FaCog, FaTrash } from 'react-icons/fa';
import type { RootState } from '../../store';
import { removeWorkspace, updateWorkspace, setError } from '../../store/slices/workspaceSlice';
import { apiService } from '../../services/api';
import {
    type RagConfig,
    type VectorRagConfig,
    type GraphRagConfig,
    type UpdateRagConfigRequest,
} from '../../types/workspace';
import RagConfigForm from './RagConfigForm'; // Import RagConfigForm

type FormData = {
    name: string;
    description: string;
    ragConfig: Partial<UpdateRagConfigRequest>;
};

const WorkspaceSettings = () => {
    const dispatch = useDispatch();
    const { workspaces, activeWorkspaceId } = useSelector((state: RootState) => state.workspace);
    const [showModal, setShowModal] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [ragConfig, setRagConfig] = useState<RagConfig | null>(null);
    const [formData, setFormData] = useState<FormData>({
        name: '',
        description: '',
        ragConfig: {}, // Initialize with empty object
    });
    const [saveError, setSaveError] = useState<string | null>(null);
    const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

    const activeWorkspace = workspaces.find((w) => w.id === activeWorkspaceId);
    // RAG config is editable only if the workspace status is 'provisioning'
    // or if the rag_config itself is not yet set (meaning it's a very new workspace)
    const isRagConfigEditable = activeWorkspace?.status === 'provisioning';

    const loadRagConfig = useCallback(async () => {
        if (!activeWorkspaceId) return;

        try {
            const config = await apiService.getRagConfig(activeWorkspaceId);
            setRagConfig(config);
            setFormData((prev) => ({
                ...prev,
                ragConfig: config,
            }));
        } catch (error) {
            console.error('Failed to load RAG config:', error);
            // If no config found, initialize with default values for form
            setRagConfig(null);
            setFormData((prev) => ({
                ...prev,
                ragConfig: {
                    retriever_type: 'vector',
                    embedding_model: 'nomic-embed-text',
                    chunk_size: 1000,
                    chunk_overlap: 200,
                    top_k: 8,
                    rerank_enabled: false,
                },
            }));
        }
    }, [activeWorkspaceId]);

    useEffect(() => {
        if (showModal && activeWorkspace) {
            setFormData((prev) => ({
                ...prev,
                name: activeWorkspace.name,
                description: activeWorkspace.description || '',
            }));
            loadRagConfig();
        }
    }, [showModal, activeWorkspace, loadRagConfig]);

    const handleSave = async () => {
        if (!activeWorkspaceId || !activeWorkspace) return;

        setIsLoading(true);
        setSaveError(null);

        try {
            const updatedWorkspace = await apiService.updateWorkspace(activeWorkspaceId, {
                name: formData.name,
                description: formData.description || undefined,
            });
            dispatch(updateWorkspace(updatedWorkspace));

            // Only update RAG config if the workspace is in provisioning state
            if (isRagConfigEditable) {
                let ragConfigToSave: UpdateRagConfigRequest = {};
                if (formData.ragConfig.retriever_type === 'graph') {
                    ragConfigToSave = {
                        retriever_type: 'graph',
                        max_hops: (formData.ragConfig as Partial<GraphRagConfig>).max_hops,
                        entity_extraction_model: (formData.ragConfig as Partial<GraphRagConfig>)
                            .entity_extraction_model,
                        relationship_extraction_model: (formData.ragConfig as Partial<GraphRagConfig>)
                            .relationship_extraction_model,
                    };
                } else {
                    ragConfigToSave = {
                        retriever_type: 'vector',
                        embedding_model: (formData.ragConfig as Partial<VectorRagConfig>)
                            .embedding_model,
                        chunk_size: (formData.ragConfig as Partial<VectorRagConfig>).chunk_size,
                        chunk_overlap: (formData.ragConfig as Partial<VectorRagConfig>)
                            .chunk_overlap,
                        top_k: (formData.ragConfig as Partial<VectorRagConfig>).top_k,
                        rerank_enabled: (formData.ragConfig as Partial<VectorRagConfig>)
                            .rerank_enabled,
                        rerank_model: (formData.ragConfig as Partial<VectorRagConfig>).rerank_model,
                    };
                }

                if (ragConfig) {
                    await apiService.updateRagConfig(activeWorkspaceId, ragConfigToSave);
                } else {
                    await apiService.createRagConfig(activeWorkspaceId, ragConfigToSave as CreateRagConfigRequest);
                }
            }

            setShowModal(false);
        } catch (error) {
            const message =
                error instanceof AxiosError ? error.response?.data?.message : 'Failed to save settings';
            setSaveError(message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!activeWorkspaceId || !activeWorkspace) return;

        setIsLoading(true);
        setDeleteConfirmOpen(false); // Close confirm dialog
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
                        {saveError && (
                            <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 rounded-lg text-sm">
                                {saveError}
                            </div>
                        )}

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

                            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                                RAG Configuration
                            </h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                                RAG configuration can only be modified for new workspaces or those still being provisioned.
                            </p>

                            <RagConfigForm
                                initialConfig={formData.ragConfig}
                                onConfigChange={(newConfig) =>
                                    setFormData((prev) => ({ ...prev, ragConfig: newConfig }))
                                }
                                readOnly={!isRagConfigEditable}
                            />
                        </div>

                        <div className="flex justify-between mt-6 pt-6 border-t border-gray-300 dark:border-gray-600">
                            <button
                                onClick={() => setDeleteConfirmOpen(true)}
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
            <ConfirmDialog
                isOpen={deleteConfirmOpen}
                title="Delete Workspace"
                message={`Are you sure you want to delete "${activeWorkspace.name}"? All documents and chat sessions in this workspace will be permanently deleted.`}
                confirmLabel="Delete Workspace"
                variant="danger"
                onConfirm={handleDelete}
                onCancel={() => setDeleteConfirmOpen(false)}
            />
        </>
    );
};

export default WorkspaceSettings;
