import React, { useState, useEffect } from 'react';
import { type RagConfig } from '../../types/workspace';
import apiService from '../../services/api';
import { logger } from '../../lib/logger';

interface RagConfigFormProps {
    initialConfig?: Partial<RagConfig>;
    onConfigChange: (config: Partial<RagConfig>) => void;
    readOnly?: boolean;
}

interface AlgorithmOption {
    value: string;
    label: string;
    description?: string;
}

const RagConfigForm: React.FC<RagConfigFormProps> = ({
    initialConfig = {},
    onConfigChange,
    readOnly = false,
}) => {
    const [config, setConfig] = useState<Partial<RagConfig>>(() => ({
        retriever_type: initialConfig.retriever_type || 'vector',
        embedding_model: initialConfig.embedding_model || 'nomic-embed-text',
        chunk_size: initialConfig.chunk_size || 1000,
        chunk_overlap: initialConfig.chunk_overlap || 200,
        top_k: initialConfig.top_k || 8,
        rerank_enabled: initialConfig.rerank_enabled || false,
        rerank_model: initialConfig.rerank_model,
        entity_extraction_algorithm: initialConfig.entity_extraction_algorithm,
        relationship_extraction_algorithm: initialConfig.relationship_extraction_algorithm,
        clustering_algorithm: initialConfig.clustering_algorithm,
    }));

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

    const [loadingAlgorithms, setLoadingAlgorithms] = useState(true);

    useEffect(() => {
        const fetchAlgorithms = async () => {
            try {
                const [vectorData, graphData] = await Promise.all([
                    apiService.getVectorAlgorithms(),
                    apiService.getGraphAlgorithms(),
                ]);
                setVectorAlgorithms(vectorData);
                setGraphAlgorithms(graphData);
            } catch (error) {
                logger.error('Failed to fetch algorithms', error as Error);
                // Fallback defaults
                setVectorAlgorithms({
                    embedding_algorithms: [
                        { value: 'nomic-embed-text', label: 'Nomic Embed Text' },
                    ],
                    chunking_algorithms: [{ value: 'sentence', label: 'Sentence-based' }],
                    rerank_algorithms: [
                        {
                            value: 'cross-encoder/ms-marco-MiniLM-L-6-v2',
                            label: 'Cross-Encoder MiniLM',
                        },
                    ],
                });
                setGraphAlgorithms({
                    entity_extraction_algorithms: [{ value: 'llm', label: 'LLM-based' }],
                    relationship_extraction_algorithms: [{ value: 'llm', label: 'LLM-based' }],
                    clustering_algorithms: [{ value: 'leiden', label: 'Leiden' }],
                });
            } finally {
                setLoadingAlgorithms(false);
            }
        };

        fetchAlgorithms();
    }, []);

    useEffect(() => {
        onConfigChange(config);
    }, [config, onConfigChange]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        let newValue: string | number | boolean = value;

        if (type === 'number') {
            newValue = parseInt(value, 10);
            if (isNaN(newValue)) newValue = 0;
        } else if (type === 'checkbox') {
            newValue = (e.target as HTMLInputElement).checked;
        }

        setConfig((prev) => {
            const newConfig = { ...prev, [name]: newValue };

            // When retriever_type changes, reset to appropriate defaults
            if (name === 'retriever_type') {
                if (value === 'vector') {
                    return {
                        retriever_type: 'vector',
                        embedding_model: 'nomic-embed-text',
                        chunk_size: 1000,
                        chunk_overlap: 200,
                        top_k: 8,
                        rerank_enabled: false,
                    };
                } else if (value === 'graph') {
                    return {
                        retriever_type: 'graph',
                        embedding_model: 'nomic-embed-text',
                        chunk_size: 1000,
                        chunk_overlap: 200,
                        top_k: 8,
                        entity_extraction_algorithm: 'llm',
                        relationship_extraction_algorithm: 'llm',
                        clustering_algorithm: 'leiden',
                    };
                }
            }

            return newConfig;
        });
    };

    return (
        <div className="space-y-6">
            {/* Retriever Type Selection - Always at the top */}
            <div>
                <label
                    htmlFor="retriever_type"
                    className="block text-sm font-semibold text-gray-900 dark:text-gray-100"
                >
                    RAG Type
                </label>
                <select
                    id="retriever_type"
                    name="retriever_type"
                    value={config.retriever_type || 'vector'}
                    onChange={handleChange}
                    disabled={readOnly || loadingAlgorithms}
                    className="mt-1 block w-full pl-3 pr-10 py-3 text-base border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-lg shadow-sm transition-all duration-200"
                >
                    <option value="vector">Vector RAG</option>
                    <option value="graph">Graph RAG</option>
                </select>
                <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 font-medium">
                    Choose between Vector-based or Graph-based retrieval
                </p>
            </div>

            {/* Embedding Configuration - Common to both */}
            <div>
                <label
                    htmlFor="embedding_model"
                    className="block text-sm font-semibold text-gray-900 dark:text-gray-100"
                >
                    Embedding Model
                </label>
                <select
                    id="embedding_model"
                    name="embedding_model"
                    value={config.embedding_model || 'nomic-embed-text'}
                    onChange={handleChange}
                    disabled={readOnly || loadingAlgorithms}
                    className="mt-1 block w-full pl-3 pr-10 py-3 text-base border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-lg shadow-sm transition-all duration-200"
                >
                    {vectorAlgorithms?.embedding_algorithms?.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    )) || <option value="nomic-embed-text">Nomic Embed Text</option>}
                </select>
                <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 font-medium">
                    Model used to convert text into vector embeddings
                </p>
            </div>

            {/* Vector RAG Specific Fields */}
            {config.retriever_type === 'vector' && (
                <>
                    <div>
                        <label
                            htmlFor="chunk_size"
                            className="block text-sm font-semibold text-gray-900 dark:text-gray-100"
                        >
                            Chunk Size
                        </label>
                        <input
                            type="number"
                            id="chunk_size"
                            name="chunk_size"
                            value={config.chunk_size || 1000}
                            onChange={handleChange}
                            disabled={readOnly}
                            min="100"
                            max="5000"
                            step="100"
                            className="mt-1 block w-full border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg shadow-sm py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-all duration-200"
                        />
                        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 font-medium">
                            Characters per chunk (100-5000)
                        </p>
                    </div>

                    <div>
                        <label
                            htmlFor="chunk_overlap"
                            className="block text-sm font-semibold text-gray-900 dark:text-gray-100"
                        >
                            Chunk Overlap
                        </label>
                        <input
                            type="number"
                            id="chunk_overlap"
                            name="chunk_overlap"
                            value={config.chunk_overlap || 200}
                            onChange={handleChange}
                            disabled={readOnly}
                            min="0"
                            max="1000"
                            step="50"
                            className="mt-1 block w-full border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg shadow-sm py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-all duration-200"
                        />
                        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 font-medium">
                            Overlap between chunks (0-1000)
                        </p>
                    </div>

                    <div>
                        <label
                            htmlFor="top_k"
                            className="block text-sm font-semibold text-gray-900 dark:text-gray-100"
                        >
                            Top K Results
                        </label>
                        <input
                            type="number"
                            id="top_k"
                            name="top_k"
                            value={config.top_k || 8}
                            onChange={handleChange}
                            disabled={readOnly}
                            min="1"
                            max="50"
                            step="1"
                            className="mt-1 block w-full border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg shadow-sm py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm transition-all duration-200"
                        />
                        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 font-medium">
                            Number of results to retrieve (1-50)
                        </p>
                    </div>

                    <div className="flex items-center bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border-2 border-gray-200 dark:border-gray-700">
                        <input
                            id="rerank_enabled"
                            name="rerank_enabled"
                            type="checkbox"
                            checked={config.rerank_enabled || false}
                            onChange={handleChange}
                            disabled={readOnly}
                            className="focus:ring-blue-500 h-5 w-5 text-blue-600 border-2 border-gray-400 rounded transition-all duration-200"
                        />
                        <label
                            htmlFor="rerank_enabled"
                            className="ml-3 block text-sm font-semibold text-gray-900 dark:text-gray-100"
                        >
                            Enable Reranking
                        </label>
                        <p className="ml-2 text-xs text-gray-600 dark:text-gray-400">
                            Improve result quality with additional ranking
                        </p>
                    </div>

                    {config.rerank_enabled && (
                        <div>
                            <label
                                htmlFor="rerank_model"
                                className="block text-sm font-medium text-gray-700"
                            >
                                Rerank Model
                            </label>
                            <select
                                id="rerank_model"
                                name="rerank_model"
                                value={config.rerank_model || ''}
                                onChange={handleChange}
                                disabled={readOnly || loadingAlgorithms}
                                className="mt-1 block w-full pl-3 pr-10 py-3 text-base border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-lg shadow-sm transition-all duration-200"
                            >
                                {vectorAlgorithms?.rerank_algorithms?.map((option) => (
                                    <option key={option.value} value={option.value}>
                                        {option.label}
                                    </option>
                                )) || (
                                    <option value="cross-encoder/ms-marco-MiniLM-L-6-v2">
                                        Cross-Encoder MiniLM
                                    </option>
                                )}
                            </select>
                            <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 font-medium">
                                Algorithm used to rerank retrieved results
                            </p>
                        </div>
                    )}
                </>
            )}

            {/* Graph RAG Specific Fields */}
            {config.retriever_type === 'graph' && (
                <>
                    <div>
                        <label
                            htmlFor="entity_extraction_algorithm"
                            className="block text-sm font-semibold text-gray-900 dark:text-gray-100"
                        >
                            Entity Extraction Algorithm
                        </label>
                        <select
                            id="entity_extraction_algorithm"
                            name="entity_extraction_algorithm"
                            value={config.entity_extraction_algorithm || ''}
                            onChange={handleChange}
                            disabled={readOnly || loadingAlgorithms}
                            className="mt-1 block w-full pl-3 pr-10 py-3 text-base border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-lg shadow-sm transition-all duration-200"
                        >
                            {graphAlgorithms?.entity_extraction_algorithms?.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            )) || <option value="llm">LLM-based</option>}
                        </select>
                        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 font-medium">
                            Algorithm used to extract entities from documents
                        </p>
                    </div>

                    <div>
                        <label
                            htmlFor="relationship_extraction_algorithm"
                            className="block text-sm font-semibold text-gray-900 dark:text-gray-100"
                        >
                            Relationship Extraction Algorithm
                        </label>
                        <select
                            id="relationship_extraction_algorithm"
                            name="relationship_extraction_algorithm"
                            value={config.relationship_extraction_algorithm || ''}
                            onChange={handleChange}
                            disabled={readOnly || loadingAlgorithms}
                            className="mt-1 block w-full pl-3 pr-10 py-3 text-base border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-lg shadow-sm transition-all duration-200"
                        >
                            {graphAlgorithms?.relationship_extraction_algorithms?.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            )) || <option value="llm">LLM-based</option>}
                        </select>
                        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 font-medium">
                            Algorithm used to extract relationships between entities
                        </p>
                    </div>

                    <div>
                        <label
                            htmlFor="clustering_algorithm"
                            className="block text-sm font-semibold text-gray-900 dark:text-gray-100"
                        >
                            Clustering Algorithm
                        </label>
                        <select
                            id="clustering_algorithm"
                            name="clustering_algorithm"
                            value={config.clustering_algorithm || ''}
                            onChange={handleChange}
                            disabled={readOnly || loadingAlgorithms}
                            className="mt-1 block w-full pl-3 pr-10 py-3 text-base border-2 border-gray-400 dark:border-gray-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-lg shadow-sm transition-all duration-200"
                        >
                            {graphAlgorithms?.clustering_algorithms?.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            )) || <option value="leiden">Leiden</option>}
                        </select>
                        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400 font-medium">
                            Algorithm used for community detection and clustering
                        </p>
                    </div>
                </>
            )}
        </div>
    );
};

export default RagConfigForm;
