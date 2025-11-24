import React, { useEffect, useState } from 'react';
import {
    type RagConfig,
    type CreateRagConfigRequest,
    type VectorRagConfig,
    type GraphRagConfig,
} from '../../types/workspace';

interface RagConfigFormProps {
    initialConfig?: Partial<RagConfig> | Partial<CreateRagConfigRequest>;
    onConfigChange: (config: Partial<CreateRagConfigRequest>) => void;
    readOnly?: boolean;
}

const RAG_TYPE_OPTIONS = [
    { value: 'vector', label: 'Vector RAG' },
    { value: 'graph', label: 'Graph RAG' },
];

const EMBEDDING_MODEL_OPTIONS = [
    { value: 'nomic-embed-text', label: 'Nomic Embed Text' },
    { value: 'openai', label: 'OpenAI Embeddings' },
    // Add other relevant embedding models
];

const RRERANK_MODEL_OPTIONS = [
    { value: 'rerank-model-1', label: 'Rerank Model 1' },
    { value: 'rerank-model-2', label: 'Rerank Model 2' },
    // Add other relevant rerank models
];

const ENTITY_EXTRACTION_MODEL_OPTIONS = [
    { value: 'ollama', label: 'Ollama' },
    { value: 'spacy', label: 'SpaCy' },
];

const RELATIONSHIP_EXTRACTION_MODEL_OPTIONS = [
    { value: 'ollama', label: 'Ollama' },
    { value: 'custom', label: 'Custom Rule-based' },
];

const RagConfigForm: React.FC<RagConfigFormProps> = ({
    initialConfig = {},
    onConfigChange,
    readOnly = false,
}) => {
    // Determine initial RAG type. Default to 'vector' if not specified.
    const initialRetrieverType = initialConfig.retriever_type || 'vector';

    const [config, setConfig] = useState<Partial<CreateRagConfigRequest>>(() => {
        if (initialRetrieverType === 'graph') {
            return {
                retriever_type: 'graph',
                max_hops: (initialConfig as Partial<GraphRagConfig>).max_hops || 2,
                entity_extraction_model:
                    (initialConfig as Partial<GraphRagConfig>).entity_extraction_model || 'ollama',
                relationship_extraction_model:
                    (initialConfig as Partial<GraphRagConfig>).relationship_extraction_model ||
                    'ollama',
            };
        } else {
            return {
                retriever_type: 'vector',
                embedding_model:
                    (initialConfig as Partial<VectorRagConfig>).embedding_model ||
                    'nomic-embed-text',
                chunk_size: (initialConfig as Partial<VectorRagConfig>).chunk_size || 1000,
                chunk_overlap: (initialConfig as Partial<VectorRagConfig>).chunk_overlap || 200,
                top_k: (initialConfig as Partial<VectorRagConfig>).top_k || 8,
                rerank_enabled:
                    (initialConfig as Partial<VectorRagConfig>).rerank_enabled || false,
                rerank_model: (initialConfig as Partial<VectorRagConfig>).rerank_model || undefined,
            };
        }
    });

    useEffect(() => {
        onConfigChange(config);
    }, [config, onConfigChange]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type, checked } = e.target as HTMLInputElement;
        let newValue: string | number | boolean = value;

        if (type === 'number') {
            newValue = parseInt(value, 10);
            if (isNaN(newValue)) newValue = 0; // Handle invalid number input, set to 0 or another default
        } else if (type === 'checkbox') {
            newValue = checked;
        }

        // Handle RAG type change separately to reset specific options
        if (name === 'retriever_type') {
            if (newValue === 'vector') {
                setConfig({
                    retriever_type: 'vector',
                    embedding_model: EMBEDDING_MODEL_OPTIONS[0]?.value,
                    chunk_size: 1000,
                    chunk_overlap: 200,
                    top_k: 8,
                    rerank_enabled: false,
                    rerank_model: undefined,
                });
            } else if (newValue === 'graph') {
                setConfig({
                    retriever_type: 'graph',
                    max_hops: 2,
                    entity_extraction_model: ENTITY_EXTRACTION_MODEL_OPTIONS[0]?.value,
                    relationship_extraction_model: RELATIONSHIP_EXTRACTION_MODEL_OPTIONS[0]?.value,
                });
            }
        } else {
            setConfig((prev) => ({
                ...prev,
                [name]: newValue,
            }));
        }
    };

    const handleRerankToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { checked } = e.target;
        setConfig((prev) => ({
            ...(prev as VectorRagConfig), // Cast to VectorRagConfig for rerank_enabled
            rerank_enabled: checked,
            rerank_model: checked ? (prev as VectorRagConfig).rerank_model || RERANK_MODEL_OPTIONS[0]?.value : undefined,
        }));
    };

    return (
        <div className="space-y-4">
            <div>
                <label htmlFor="retriever_type" className="block text-sm font-medium text-gray-700">
                    RAG Type
                </label>
                <select
                    id="retriever_type"
                    name="retriever_type"
                    value={config.retriever_type}
                    onChange={handleChange}
                    disabled={readOnly}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                    {RAG_TYPE_OPTIONS.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
            </div>

            {/* Vector RAG Configuration */}
            {config.retriever_type === 'vector' && (
                <>
                    <div>
                        <label
                            htmlFor="embedding_model"
                            className="block text-sm font-medium text-gray-700"
                        >
                            Embedding Model
                        </label>
                        <select
                            id="embedding_model"
                            name="embedding_model"
                            value={(config as VectorRagConfig).embedding_model}
                            onChange={handleChange}
                            disabled={readOnly}
                            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                        >
                            {EMBEDDING_MODEL_OPTIONS.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label htmlFor="chunk_size" className="block text-sm font-medium text-gray-700">
                            Chunk Size
                        </label>
                        <input
                            type="number"
                            id="chunk_size"
                            name="chunk_size"
                            value={(config as VectorRagConfig).chunk_size}
                            onChange={handleChange}
                            disabled={readOnly}
                            min="100"
                            max="2000"
                            step="100"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                    </div>

                    <div>
                        <label
                            htmlFor="chunk_overlap"
                            className="block text-sm font-medium text-gray-700"
                        >
                            Chunk Overlap
                        </label>
                        <input
                            type="number"
                            id="chunk_overlap"
                            name="chunk_overlap"
                            value={(config as VectorRagConfig).chunk_overlap}
                            onChange={handleChange}
                            disabled={readOnly}
                            min="0"
                            max="500"
                            step="50"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                    </div>

                    <div>
                        <label htmlFor="top_k" className="block text-sm font-medium text-gray-700">
                            Top K (Retrieval)
                        </label>
                        <input
                            type="number"
                            id="top_k"
                            name="top_k"
                            value={(config as VectorRagConfig).top_k}
                            onChange={handleChange}
                            disabled={readOnly}
                            min="1"
                            max="20"
                            step="1"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                    </div>

                    <div className="flex items-center">
                        <input
                            id="rerank_enabled"
                            name="rerank_enabled"
                            type="checkbox"
                            checked={(config as VectorRagConfig).rerank_enabled}
                            onChange={handleRerankToggle}
                            disabled={readOnly}
                            className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                        />
                        <label htmlFor="rerank_enabled" className="ml-2 block text-sm text-gray-900">
                            Enable Reranking
                        </label>
                    </div>

                    {(config as VectorRagConfig).rerank_enabled && (
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
                                value={(config as VectorRagConfig).rerank_model}
                                onChange={handleChange}
                                disabled={readOnly}
                                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            >
                                {RERANK_MODEL_OPTIONS.map((option) => (
                                    <option key={option.value} value={option.value}>
                                        {option.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}
                </>
            )}

            {/* Graph RAG Configuration */}
            {config.retriever_type === 'graph' && (
                <>
                    <div>
                        <label htmlFor="max_hops" className="block text-sm font-medium text-gray-700">
                            Max Hops (Graph Traversal)
                        </label>
                        <input
                            type="number"
                            id="max_hops"
                            name="max_hops"
                            value={(config as GraphRagConfig).max_hops}
                            onChange={handleChange}
                            disabled={readOnly}
                            min="1"
                            max="5"
                            step="1"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                    </div>
                    <div>
                        <label
                            htmlFor="entity_extraction_model"
                            className="block text-sm font-medium text-gray-700"
                        >
                            Entity Extraction Model
                        </label>
                        <select
                            id="entity_extraction_model"
                            name="entity_extraction_model"
                            value={(config as GraphRagConfig).entity_extraction_model}
                            onChange={handleChange}
                            disabled={readOnly}
                            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                        >
                            {ENTITY_EXTRACTION_MODEL_OPTIONS.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label
                            htmlFor="relationship_extraction_model"
                            className="block text-sm font-medium text-gray-700"
                        >
                            Relationship Extraction Model
                        </label>
                        <select
                            id="relationship_extraction_model"
                            name="relationship_extraction_model"
                            value={(config as GraphRagConfig).relationship_extraction_model}
                            onChange={handleChange}
                            disabled={readOnly}
                            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                        >
                            {RELATIONSHIP_EXTRACTION_MODEL_OPTIONS.map((option) => (
                                <option key={option.value} value={option.value}>
                                    {option.label}
                                </option>
                            ))}
                        </select>
                    </div>
                </>
            )}
        </div>
    );
};

export default RagConfigForm;

