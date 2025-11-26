import { useState, useEffect } from 'react';
import apiService from '../../services/api';
import type { RagConfig, VectorRagConfig, GraphRagConfig } from '../../types/workspace';
import {
    EmbeddingConfigSection,
    RetrieverConfigSection,
    ChunkingConfigSection,
    RetrievalConfigSection,
    RerankingConfigSection,
    GraphRagConfigSection,
} from './RagConfigSections';

const DEFAULT_VECTOR_CONFIG: VectorRagConfig = {
    embedding_model: 'nomic-embed-text',
    retriever_type: 'vector',
    chunk_size: 1000,
    chunk_overlap: 200,
    top_k: 8,
    rerank_enabled: false,
};

const DEFAULT_GRAPH_CONFIG: GraphRagConfig = {
    embedding_model: 'nomic-embed-text',
    retriever_type: 'graph',
    chunk_size: 1000,
    chunk_overlap: 200,
    top_k: 8,
    entity_extraction_algorithm: 'llm-based',
    relationship_extraction_algorithm: 'llm-based',
    clustering_algorithm: 'leiden',
};

function getErrorMessage(error: unknown): string {
    if (error instanceof Error) {
        return error.message;
    }
    return 'An unexpected error occurred';
}

interface AlgorithmOption {
    value: string;
    label: string;
    description?: string;
}

export default function RagConfigSettings() {
    const [config, setConfig] = useState<RagConfig>(DEFAULT_VECTOR_CONFIG);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(
        null
    );
    const [vectorAlgorithms, setVectorAlgorithms] = useState<{
        embedding_algorithms: AlgorithmOption[];
        chunking_algorithms: AlgorithmOption[];
        rerank_algorithms: AlgorithmOption[];
    } | null>(null);
    const [graphAlgorithms, setGraphAlgorithms] = useState<{
        entity_extraction_algorithms: AlgorithmOption[];
        relationship_extraction_algorithms: AlgorithmOption[];
        clustering_algorithms: AlgorithmOption[];
    } | null>(null);

    useEffect(() => {
        loadConfig();
        loadAlgorithms();
    }, []);

    const loadAlgorithms = async () => {
        try {
            const [vectorData, graphData] = await Promise.all([
                apiService.getVectorAlgorithms(),
                apiService.getGraphAlgorithms(),
            ]);
            setVectorAlgorithms(vectorData);
            setGraphAlgorithms(graphData);
        } catch (error: unknown) {
            setMessage({ type: 'error', text: getErrorMessage(error) });
        }
    };

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

    const handleChange = (field: string, value: string | number | boolean | undefined) => {
        setConfig((prev) => {
            const newConfig = { ...prev, [field]: value };

            // When retriever_type changes, reset to appropriate defaults
            if (field === 'retriever_type') {
                if (value === 'vector') {
                    return {
                        ...DEFAULT_VECTOR_CONFIG,
                        retriever_type: 'vector',
                    };
                } else if (value === 'graph') {
                    return {
                        ...DEFAULT_GRAPH_CONFIG,
                        retriever_type: 'graph',
                    };
                }
            }

            return newConfig;
        });
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
                <RetrieverConfigSection
                    config={{
                        retriever_type: config.retriever_type || 'vector',
                    }}
                    onChange={handleChange}
                />
                <EmbeddingConfigSection
                    config={{
                        embedding_model: config.embedding_model || 'nomic-embed-text',
                    }}
                    algorithms={
                        vectorAlgorithms
                            ? { embedding_algorithms: vectorAlgorithms.embedding_algorithms }
                            : undefined
                    }
                    onChange={handleChange}
                />

                {config.retriever_type === 'vector' && (
                    <>
                        <ChunkingConfigSection
                            config={{
                                chunk_size: config.chunk_size || 1000,
                                chunk_overlap: config.chunk_overlap || 200,
                            }}
                            onChange={handleChange}
                        />
                        <RetrievalConfigSection
                            config={{
                                top_k: config.top_k || 8,
                            }}
                            onChange={handleChange}
                        />
                        <RerankingConfigSection
                            config={{
                                rerank_enabled: config.rerank_enabled || false,
                                rerank_model: config.rerank_model,
                            }}
                            algorithms={
                                vectorAlgorithms
                                    ? { rerank_algorithms: vectorAlgorithms.rerank_algorithms }
                                    : undefined
                            }
                            onChange={handleChange}
                        />
                    </>
                )}

                {config.retriever_type === 'graph' && (
                    <GraphRagConfigSection
                        config={{
                            entity_extraction_algorithm: config.entity_extraction_algorithm,
                            relationship_extraction_algorithm:
                                config.relationship_extraction_algorithm,
                            clustering_algorithm: config.clustering_algorithm,
                        }}
                        algorithms={graphAlgorithms || undefined}
                        onChange={handleChange}
                    />
                )}

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
