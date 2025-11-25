import { useState, useEffect } from 'react';
import apiService from '../../services/api';
import type { VectorRagConfig } from '../../types/workspace';
import {
    EmbeddingConfigSection,
    RetrieverConfigSection,
    ChunkingConfigSection,
    RetrievalConfigSection,
    RerankingConfigSection,
} from './RagConfigSections';

const DEFAULT_CONFIG: VectorRagConfig = {
    embedding_model: 'nomic-embed-text',
    retriever_type: 'vector',
    chunk_size: 1000,
    chunk_overlap: 200,
    top_k: 8,
    rerank_enabled: false,
};

function getErrorMessage(error: unknown): string {
    if (error instanceof Error) {
        return error.message;
    }
    return 'An unexpected error occurred';
}

export default function RagConfigSettings() {
    const [config, setConfig] = useState<VectorRagConfig>(DEFAULT_CONFIG);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(
        null
    );

    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        try {
            setLoading(true);
            const data = await apiService.getDefaultRagConfig();
            if (data) {
                setConfig(data as VectorRagConfig);
            }
        } catch (error: unknown) {
            setMessage({ type: 'error', text: getErrorMessage(error) });
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);

        try {
            await apiService.saveDefaultRagConfig(config);
            setMessage({ type: 'success', text: 'Default RAG configuration saved successfully' });
        } catch (error: unknown) {
            setMessage({
                type: 'error',
                text: getErrorMessage(error),
            });
        } finally {
            setSaving(false);
        }
    };

    const handleChange = (
        field: keyof VectorRagConfig,
        value: string | number | boolean | undefined
    ) => {
        setConfig((prev) => ({ ...prev, [field]: value }));
    };

    if (loading) {
        return (
            <div className="p-6 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    Loading configuration...
                </p>
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
                    These settings will be used as defaults when creating new workspaces. You can
                    override them per workspace.
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
                <EmbeddingConfigSection config={config} onChange={handleChange} />
                <RetrieverConfigSection config={config} onChange={handleChange} />
                <ChunkingConfigSection config={config} onChange={handleChange} />
                <RetrievalConfigSection config={config} onChange={handleChange} />
                <RerankingConfigSection config={config} onChange={handleChange} />

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
