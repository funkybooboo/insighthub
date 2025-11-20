import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store';
import api from '../../services/api';

interface RagConfigData {
    embedding_model: string;
    embedding_dim?: number;
    retriever_type: string;
    chunk_size: number;
    chunk_overlap: number;
    top_k: number;
    rerank_enabled: boolean;
    rerank_model?: string;
}

const DEFAULT_CONFIG: RagConfigData = {
    embedding_model: 'nomic-embed-text',
    retriever_type: 'vector',
    chunk_size: 1000,
    chunk_overlap: 200,
    top_k: 8,
    rerank_enabled: false,
};

export default function RagConfigSettings() {
    const { token } = useSelector((state: RootState) => state.auth);
    const [config, setConfig] = useState<RagConfigData>(DEFAULT_CONFIG);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        try {
            setLoading(true);
            const response = await api.get('/auth/default-rag-config', {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (response.data) {
                setConfig(response.data);
            }
        } catch (error: any) {
            // If no config exists yet, use defaults
            if (error.response?.status === 404) {
                setConfig(DEFAULT_CONFIG);
            } else {
                setMessage({ type: 'error', text: 'Failed to load RAG configuration' });
            }
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);

        try {
            await api.put('/auth/default-rag-config', config, {
                headers: { Authorization: `Bearer ${token}` },
            });
            setMessage({ type: 'success', text: 'Default RAG configuration saved successfully' });
        } catch (error: any) {
            setMessage({
                type: 'error',
                text: error.response?.data?.detail || 'Failed to save RAG configuration',
            });
        } finally {
            setSaving(false);
        }
    };

    const handleChange = (field: keyof RagConfigData, value: string | number | boolean) => {
        setConfig((prev) => ({ ...prev, [field]: value }));
    };

    if (loading) {
        return (
            <div className="p-6 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">Loading configuration...</p>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    Default RAG Configuration
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                    These settings will be used as defaults when creating new workspaces. You can override them per workspace.
                </p>
            </div>

            {message && (
                <div
                    className={`mb-4 p-4 rounded-md ${
                        message.type === 'success'
                            ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                            : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
                    }`}
                >
                    {message.text}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Embedding Configuration */}
                <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                        Embedding Configuration
                    </h3>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Embedding Model
                            </label>
                            <select
                                value={config.embedding_model}
                                onChange={(e) => handleChange('embedding_model', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                            >
                                <option value="nomic-embed-text">Nomic Embed Text</option>
                                <option value="text-embedding-ada-002">OpenAI Ada-002</option>
                                <option value="all-MiniLM-L6-v2">Sentence Transformers MiniLM</option>
                            </select>
                            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                                The model used to convert text into vector embeddings
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Embedding Dimension (Optional)
                            </label>
                            <input
                                type="number"
                                value={config.embedding_dim || ''}
                                onChange={(e) => handleChange('embedding_dim', e.target.value ? parseInt(e.target.value) : undefined)}
                                placeholder="Auto-detect"
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                            />
                            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                                Vector dimension (leave empty for auto-detection)
                            </p>
                        </div>
                    </div>
                </div>

                {/* Retriever Configuration */}
                <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                        Retriever Configuration
                    </h3>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Retriever Type
                        </label>
                        <select
                            value={config.retriever_type}
                            onChange={(e) => handleChange('retriever_type', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        >
                            <option value="vector">Vector RAG</option>
                            <option value="graph">Graph RAG</option>
                            <option value="hybrid">Hybrid RAG</option>
                        </select>
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                            The retrieval strategy for finding relevant documents
                        </p>
                    </div>
                </div>

                {/* Chunking Configuration */}
                <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                        Chunking Configuration
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Chunk Size
                            </label>
                            <input
                                type="number"
                                value={config.chunk_size}
                                onChange={(e) => handleChange('chunk_size', parseInt(e.target.value))}
                                min="100"
                                max="5000"
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                            />
                            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                                Number of characters per chunk (100-5000)
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Chunk Overlap
                            </label>
                            <input
                                type="number"
                                value={config.chunk_overlap}
                                onChange={(e) => handleChange('chunk_overlap', parseInt(e.target.value))}
                                min="0"
                                max="1000"
                                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                            />
                            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                                Character overlap between chunks (0-1000)
                            </p>
                        </div>
                    </div>
                </div>

                {/* Retrieval Configuration */}
                <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                        Retrieval Settings
                    </h3>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Top K Results
                        </label>
                        <input
                            type="number"
                            value={config.top_k}
                            onChange={(e) => handleChange('top_k', parseInt(e.target.value))}
                            min="1"
                            max="50"
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        />
                        <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                            Number of results to retrieve (1-50)
                        </p>
                    </div>
                </div>

                {/* Reranking Configuration */}
                <div>
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                        Reranking Configuration
                    </h3>
                    <div className="space-y-4">
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                id="rerank_enabled"
                                checked={config.rerank_enabled}
                                onChange={(e) => handleChange('rerank_enabled', e.target.checked)}
                                className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                            <label htmlFor="rerank_enabled" className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                                Enable Reranking
                            </label>
                        </div>

                        {config.rerank_enabled && (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Rerank Model
                                </label>
                                <input
                                    type="text"
                                    value={config.rerank_model || ''}
                                    onChange={(e) => handleChange('rerank_model', e.target.value)}
                                    placeholder="e.g., cross-encoder/ms-marco-MiniLM-L-6-v2"
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                                />
                                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                                    Model used to rerank retrieved results
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Submit Button */}
                <div className="pt-4">
                    <button
                        type="submit"
                        disabled={saving}
                        className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-md font-medium transition-colors"
                    >
                        {saving ? 'Saving...' : 'Save Default Configuration'}
                    </button>
                </div>
            </form>
        </div>
    );
}
