import React from 'react';
import { Button } from '../ui/button';

interface EmbeddingConfigSectionProps {
    config: {
        embedding_model: string;
    };
    onChange: (field: string, value: string | number | boolean) => void;
}

export const EmbeddingConfigSection: React.FC<EmbeddingConfigSectionProps> = ({
    config,
    onChange
}) => (
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
                    onChange={(e) => onChange('embedding_model', e.target.value)}
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
        </div>
    </div>
);

interface RetrieverConfigSectionProps {
    config: {
        retriever_type: string;
    };
    onChange: (field: string, value: string | number | boolean) => void;
}

export const RetrieverConfigSection: React.FC<RetrieverConfigSectionProps> = ({
    config,
    onChange
}) => (
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
                onChange={(e) => onChange('retriever_type', e.target.value)}
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
);

interface ChunkingConfigSectionProps {
    config: {
        chunk_size: number;
        chunk_overlap: number;
    };
    onChange: (field: string, value: string | number | boolean) => void;
}

export const ChunkingConfigSection: React.FC<ChunkingConfigSectionProps> = ({
    config,
    onChange
}) => (
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
                    onChange={(e) => onChange('chunk_size', parseInt(e.target.value))}
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
                    onChange={(e) => onChange('chunk_overlap', parseInt(e.target.value))}
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
);

interface RetrievalConfigSectionProps {
    config: {
        top_k: number;
    };
    onChange: (field: string, value: string | number | boolean) => void;
}

export const RetrievalConfigSection: React.FC<RetrievalConfigSectionProps> = ({
    config,
    onChange
}) => (
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
                onChange={(e) => onChange('top_k', parseInt(e.target.value))}
                min="1"
                max="50"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Number of results to retrieve (1-50)
            </p>
        </div>
    </div>
);

interface RerankingConfigSectionProps {
    config: {
        rerank_enabled: boolean;
        rerank_model?: string;
    };
    onChange: (field: string, value: string | number | boolean) => void;
}

export const RerankingConfigSection: React.FC<RerankingConfigSectionProps> = ({
    config,
    onChange
}) => (
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
                    onChange={(e) => onChange('rerank_enabled', e.target.checked)}
                    className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label
                    htmlFor="rerank_enabled"
                    className="ml-2 text-sm text-gray-700 dark:text-gray-300"
                >
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
                        onChange={(e) => onChange('rerank_model', e.target.value)}
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
);