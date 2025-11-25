import type { Meta, StoryObj } from '@storybook/react-vite';
import RagConfigSettings from './RagConfigSettings';
import {
    EmbeddingConfigSection,
    RetrieverConfigSection,
    ChunkingConfigSection,
    RetrievalConfigSection,
    RerankingConfigSection,
} from './RagConfigSections';

const meta: Meta<typeof RagConfigSettings> = {
    title: 'Settings/RagConfigSettings',
    component: RagConfigSettings,
    parameters: {
        layout: 'padded',
        docs: {
            description: {
                component:
                    'Complete RAG configuration form for customizing retrieval and generation parameters.',
            },
        },
    },
    tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    parameters: {
        docs: {
            description: {
                story: 'Basic RAG configuration form with all settings sections.',
            },
        },
    },
};

export const SettingsPageLayout: Story = {
    render: () => (
        <div className="max-w-4xl mx-auto">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                <div className="border-b border-gray-200 dark:border-gray-700">
                    <nav className="flex">
                        <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                            Profile
                        </button>
                        <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                            Password
                        </button>
                        <button className="px-6 py-4 text-sm font-medium text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400">
                            RAG Config
                        </button>
                    </nav>
                </div>

                <div className="p-6">
                    <div className="mb-6">
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                            RAG Configuration
                        </h2>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Customize your RAG system settings for optimal performance.
                        </p>
                    </div>

                    <RagConfigSettings />
                </div>
            </div>
        </div>
    ),
};

// Individual section stories
export const EmbeddingSection: Story = {
    render: () => (
        <div className="max-w-2xl">
            <EmbeddingConfigSection
                config={{
                    embedding_model: 'nomic-embed-text',
                }}
                onChange={(field, value) => console.log(`${field}:`, value)}
            />
        </div>
    ),
    parameters: {
        docs: {
            description: {
                story: 'Embedding configuration section showing model selection.',
            },
        },
    },
};

export const RetrieverSection: Story = {
    render: () => (
        <div className="max-w-2xl">
            <RetrieverConfigSection
                config={{
                    retriever_type: 'vector',
                }}
                onChange={(field, value) => console.log(`${field}:`, value)}
            />
        </div>
    ),
    parameters: {
        docs: {
            description: {
                story: 'Retriever type configuration section.',
            },
        },
    },
};

export const ChunkingSection: Story = {
    render: () => (
        <div className="max-w-2xl">
            <ChunkingConfigSection
                config={{
                    chunk_size: 1000,
                    chunk_overlap: 200,
                }}
                onChange={(field, value) => console.log(`${field}:`, value)}
            />
        </div>
    ),
    parameters: {
        docs: {
            description: {
                story: 'Document chunking configuration with size and overlap controls.',
            },
        },
    },
};

export const RetrievalSection: Story = {
    render: () => (
        <div className="max-w-2xl">
            <RetrievalConfigSection
                config={{
                    top_k: 8,
                }}
                onChange={(field, value) => console.log(`${field}:`, value)}
            />
        </div>
    ),
    parameters: {
        docs: {
            description: {
                story: 'Retrieval settings for controlling result count.',
            },
        },
    },
};

export const RerankingSection: Story = {
    render: () => (
        <div className="max-w-2xl">
            <RerankingConfigSection
                config={{
                    rerank_enabled: true,
                    rerank_model: 'cross-encoder/ms-marco-MiniLM-L-6-v2',
                }}
                onChange={(field, value) => console.log(`${field}:`, value)}
            />
        </div>
    ),
    parameters: {
        docs: {
            description: {
                story: 'Reranking configuration with enable toggle and model selection.',
            },
        },
    },
};

export const RerankingDisabled: Story = {
    render: () => (
        <div className="max-w-2xl">
            <RerankingConfigSection
                config={{
                    rerank_enabled: false,
                }}
                onChange={(field, value) => console.log(`${field}:`, value)}
            />
        </div>
    ),
    parameters: {
        docs: {
            description: {
                story: 'Reranking section when reranking is disabled.',
            },
        },
    },
};

export const BasicForm: Story = {
    args: {},
    parameters: {
        docs: {
            description: {
                story: 'Basic RAG configuration form with all default settings.',
            },
        },
    },
};

export const InSettingsPage: Story = {
    render: () => (
        <div className="max-w-4xl mx-auto">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                <div className="border-b border-gray-200 dark:border-gray-700">
                    <nav className="flex">
                        <button className="px-6 py-4 text-sm font-medium text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400">
                            RAG Configuration
                        </button>
                        <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                            Profile
                        </button>
                        <button className="px-6 py-4 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
                            Password
                        </button>
                    </nav>
                </div>

                <RagConfigSettings />
            </div>
        </div>
    ),
};
