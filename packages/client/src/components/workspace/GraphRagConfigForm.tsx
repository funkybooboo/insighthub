import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';
import { GraphRagConfig } from '../../types/workspace';
import { logger } from '../../lib/logger';

interface GraphRagConfigFormProps {
    initialConfig?: Partial<GraphRagConfig>;
    onConfigChange: (config: Partial<GraphRagConfig>) => void;
    readOnly?: boolean;
}

interface AlgorithmOption {
    value: string;
    label: string;
}

const GraphRagConfigForm: React.FC<GraphRagConfigFormProps> = ({
    initialConfig = {},
    onConfigChange,
    readOnly = false,
}) => {
    const [config, setConfig] = useState<Partial<GraphRagConfig>>(() => ({
        entity_extraction_algorithm: initialConfig.entity_extraction_algorithm || 'ollama',
        relationship_extraction_algorithm: initialConfig.relationship_extraction_algorithm || 'ollama',
        clustering_algorithm: initialConfig.clustering_algorithm || 'leiden',
        max_hops: initialConfig.max_hops || 2,
        min_cluster_size: initialConfig.min_cluster_size || 5,
        max_cluster_size: initialConfig.max_cluster_size || 50,
    }));

    const [algorithms, setAlgorithms] = useState<{
        entity_extraction_algorithms: AlgorithmOption[];
        relationship_extraction_algorithms: AlgorithmOption[];
        clustering_algorithms: AlgorithmOption[];
    }>({
        entity_extraction_algorithms: [],
        relationship_extraction_algorithms: [],
        clustering_algorithms: [],
    });

    const [loadingAlgorithms, setLoadingAlgorithms] = useState(true);

    useEffect(() => {
        const fetchAlgorithms = async () => {
            try {
                const data = await apiService.getGraphAlgorithms();
                setAlgorithms(data);
            } catch (error) {
                 logger.error('Failed to fetch graph algorithms', error as Error);
                 // Fallback to defaults if API fails
                setAlgorithms({
                    entity_extraction_algorithms: [
                        { value: 'ollama', label: 'Ollama LLM' },
                    ],
                    relationship_extraction_algorithms: [
                        { value: 'ollama', label: 'Ollama LLM' },
                    ],
                    clustering_algorithms: [
                        { value: 'leiden', label: 'Leiden Algorithm' },
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
        let newValue: string | number = value;

        if (type === 'number') {
            newValue = parseInt(value, 10);
            if (isNaN(newValue)) newValue = 0;
        }

        setConfig((prev) => ({
            ...prev,
            [name]: newValue,
        }));
    };

    return (
        <div className="space-y-6">
            <div>
                <label htmlFor="entity_extraction_algorithm" className="block text-sm font-medium text-gray-700">
                    Entity Extraction Algorithm
                </label>
                <select
                    id="entity_extraction_algorithm"
                    name="entity_extraction_algorithm"
                    value={config.entity_extraction_algorithm}
                    onChange={handleChange}
                    disabled={readOnly || loadingAlgorithms}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                    {algorithms.entity_extraction_algorithms.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                    Algorithm used to extract entities from text
                </p>
            </div>

            <div>
                <label htmlFor="relationship_extraction_algorithm" className="block text-sm font-medium text-gray-700">
                    Relationship Extraction Algorithm
                </label>
                <select
                    id="relationship_extraction_algorithm"
                    name="relationship_extraction_algorithm"
                    value={config.relationship_extraction_algorithm}
                    onChange={handleChange}
                    disabled={readOnly || loadingAlgorithms}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                    {algorithms.relationship_extraction_algorithms.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                    Algorithm used to extract relationships between entities
                </p>
            </div>

            <div>
                <label htmlFor="clustering_algorithm" className="block text-sm font-medium text-gray-700">
                    Clustering Algorithm
                </label>
                <select
                    id="clustering_algorithm"
                    name="clustering_algorithm"
                    value={config.clustering_algorithm}
                    onChange={handleChange}
                    disabled={readOnly || loadingAlgorithms}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                    {algorithms.clustering_algorithms.map((option) => (
                        <option key={option.value} value={option.value}>
                            {option.label}
                        </option>
                    ))}
                </select>
                <p className="mt-1 text-xs text-gray-500">
                    Algorithm used to cluster entities in the knowledge graph
                </p>
            </div>

            <div>
                <label htmlFor="max_hops" className="block text-sm font-medium text-gray-700">
                    Max Hops
                </label>
                <input
                    type="number"
                    id="max_hops"
                    name="max_hops"
                    value={config.max_hops}
                    onChange={handleChange}
                    disabled={readOnly}
                    min="1"
                    max="10"
                    step="1"
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
                <p className="mt-1 text-xs text-gray-500">
                    Maximum hops to traverse in graph queries (1-10)
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label htmlFor="min_cluster_size" className="block text-sm font-medium text-gray-700">
                        Min Cluster Size
                    </label>
                    <input
                        type="number"
                        id="min_cluster_size"
                        name="min_cluster_size"
                        value={config.min_cluster_size}
                        onChange={handleChange}
                        disabled={readOnly}
                        min="1"
                        max="100"
                        step="1"
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        Minimum entities per cluster
                    </p>
                </div>

                <div>
                    <label htmlFor="max_cluster_size" className="block text-sm font-medium text-gray-700">
                        Max Cluster Size
                    </label>
                    <input
                        type="number"
                        id="max_cluster_size"
                        name="max_cluster_size"
                        value={config.max_cluster_size}
                        onChange={handleChange}
                        disabled={readOnly}
                        min="1"
                        max="1000"
                        step="10"
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                        Maximum entities per cluster
                    </p>
                </div>
            </div>
        </div>
    );
};

export default GraphRagConfigForm;