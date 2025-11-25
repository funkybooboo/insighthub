import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';
import { VectorRagConfig } from '../../types/workspace';

interface VectorRagConfigFormProps {
    initialConfig?: Partial<VectorRagConfig>;
    onConfigChange: (config: Partial<VectorRagConfig>) => void;
    readOnly?: boolean;
}

interface AlgorithmOption {
    value: string;
    label: string;
}

const VectorRagConfigForm: React.FC<VectorRagConfigFormProps> = ({
    initialConfig = {},
    onConfigChange,
    readOnly = false,
}) => {
    const [config, setConfig] = useState<Partial<VectorRagConfig>>(() => ({
        embedding_algorithm: initialConfig.embedding_algorithm || 'nomic-embed-text',
        chunking_algorithm: initialConfig.chunking_algorithm || 'sentence',
        chunk_size: initialConfig.chunk_size || 1000,
        chunk_overlap: initialConfig.chunk_overlap || 200,
        top_k: initialConfig.top_k || 8,
        rerank_enabled: initialConfig.rerank_enabled || false,
        rerank_algorithm: initialConfig.rerank_algorithm,
    }));

    const [algorithms, setAlgorithms] = useState<{
        embedding_algorithms: AlgorithmOption[];
        chunking_algorithms: AlgorithmOption[];
        rerank_algorithms: AlgorithmOption[];
    }>({
        embedding_algorithms: [],
        chunking_algorithms: [],
        rerank_algorithms: [],
    });

    const [loadingAlgorithms, setLoadingAlgorithms] = useState(true);

    useEffect(() => {
        const fetchAlgorithms = async () => {
            try {
                const data = await apiService.getVectorAlgorithms();
                setAlgorithms(data);
            } catch (error) {
                console.error('Failed to fetch vector algorithms:', error);
                // Fallback to defaults if API fails
                setAlgorithms({
                    embedding_algorithms: [
                        { value: 'nomic-embed-text', label: 'Nomic Embed Text' },
                    ],
                    chunking_algorithms: [
                        { value: 'sentence', label: 'Sentence-based' },
                    ],
                    rerank_algorithms: [
                        { value: 'cross-encoder/ms-marco-MiniLM-L-6-v2', label: 'Cross-Encoder MiniLM' },
                    ],
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

        setConfig((prev) => ({
            ...prev,
            [name]: newValue,
        }));
    };

    const handleRerankToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { checked } = e.target;
        setConfig((prev) => ({
            ...prev,
            rerank_enabled: checked,
            rerank_algorithm: checked
                ? (prev.rerank_algorithm || RERANK_ALGORITHMS[0]?.value)
                : undefined,
        }));
    };

    return (
        <div className="space-y-6">
            <div>
                <label htmlFor="embedding_algorithm" className="block text-sm font-medium text-gray-700">
                    Embedding Algorithm
                </label>
                <select
                    id="embedding_algorithm"
                    name="embedding_algorithm"
                    value={config.embedding_algorithm}
                    onChange={handleChange}
                    disabled={readOnly || loadingAlgorithms}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                    {algorithms.embedding_algorithms.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                    Algorithm used to convert text into vector embeddings
                </p>
            </div>

            <div>
                <label htmlFor="chunking_algorithm" className="block text-sm font-medium text-gray-700">
                    Chunking Algorithm
                </label>
                <select
                    id="chunking_algorithm"
                    name="chunking_algorithm"
                    value={config.chunking_algorithm}
                    onChange={handleChange}
                    disabled={readOnly || loadingAlgorithms}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                    {algorithms.chunking_algorithms.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                    Method used to split documents into chunks
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label htmlFor="chunk_size" className="block text-sm font-medium text-gray-700">
                        Chunk Size
                    </label>
                    <input
                        type="number"
                        id="chunk_size"
                        name="chunk_size"
                        value={config.chunk_size}
                        onChange={handleChange}
                        disabled={readOnly}
                        min="100"
                        max="5000"
                        step="100"
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        Characters per chunk (100-5000)
                    </p>
                </div>

                <div>
                    <label htmlFor="chunk_overlap" className="block text-sm font-medium text-gray-700">
                        Chunk Overlap
                    </label>
                    <input
                        type="number"
                        id="chunk_overlap"
                        name="chunk_overlap"
                        value={config.chunk_overlap}
                        onChange={handleChange}
                        disabled={readOnly}
                        min="0"
                        max="1000"
                        step="50"
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        Overlap between chunks (0-1000)
                    </p>
                </div>
            </div>

            <div>
                <label htmlFor="top_k" className="block text-sm font-medium text-gray-700">
                    Top K Results
                </label>
                <input
                    type="number"
                    id="top_k"
                    name="top_k"
                    value={config.top_k}
                    onChange={handleChange}
                    disabled={readOnly}
                    min="1"
                    max="50"
                    step="1"
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
                <p className="mt-1 text-xs text-gray-500">
                    Number of results to retrieve (1-50)
                </p>
            </div>

            <div className="flex items-center">
                <input
                    id="rerank_enabled"
                    name="rerank_enabled"
                    type="checkbox"
                    checked={config.rerank_enabled}
                    onChange={handleRerankToggle}
                    disabled={readOnly}
                    className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                />
                <label htmlFor="rerank_enabled" className="ml-2 block text-sm text-gray-900">
                    Enable Reranking
                </label>
            </div>

            {config.rerank_enabled && (
                <div>
                    <label htmlFor="rerank_algorithm" className="block text-sm font-medium text-gray-700">
                        Rerank Algorithm
                    </label>
                    <select
                        id="rerank_algorithm"
                        name="rerank_algorithm"
                        value={config.rerank_algorithm || ''}
                        onChange={handleChange}
                        disabled={readOnly || loadingAlgorithms}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    >
                        {algorithms.rerank_algorithms.map((option) => (
                            <option key={option.value} value={option.value}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                    <p className="mt-1 text-xs text-gray-500">
                        Algorithm used to rerank retrieved results
                    </p>
                </div>
            )}
        </div>
    );
};

export default VectorRagConfigForm;