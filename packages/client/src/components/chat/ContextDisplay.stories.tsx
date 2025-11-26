import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';

// Mock ContextDisplay component for Storybook to avoid shared package imports
const MockContextDisplay = ({
    context,
}: {
    context: Array<{ text: string; score: number; metadata: Record<string, unknown> }>;
}) => {
    const [expanded, setExpanded] = useState(false);

    if (!context || context.length === 0) {
        return null;
    }

    return (
        <div className="mt-2 text-sm text-gray-600 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700 pt-2">
            <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center justify-between w-full text-left focus:outline-none hover:text-gray-800 dark:hover:text-gray-200"
            >
                <span className="font-medium">{context.length} relevant context snippets</span>
                {expanded ? (
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 15l7-7 7 7"
                        />
                    </svg>
                ) : (
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 9l-7 7-7-7"
                        />
                    </svg>
                )}
            </button>

            {expanded && (
                <div className="mt-2 space-y-3">
                    {context.map((item, index) => (
                        <div
                            key={index}
                            className="bg-gray-50 dark:bg-gray-800/50 rounded-md p-3 border border-gray-200 dark:border-gray-700"
                        >
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                                    Source: {item.metadata.source || 'Unknown'}
                                </span>
                                <span className="text-xs text-green-600 dark:text-green-400 font-medium">
                                    Score: {(item.score * 100).toFixed(1)}%
                                </span>
                            </div>
                            <p className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed">
                                {item.text}
                            </p>
                            {item.metadata.page && (
                                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                                    Page {item.metadata.page}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

const meta: Meta<typeof MockContextDisplay> = {
    title: 'Chat/ContextDisplay',
    component: MockContextDisplay,
    parameters: {
        layout: 'padded',
        docs: {
            description: {
                component:
                    'Expandable display of retrieved context snippets with relevance scores. (Mock implementation for Storybook)',
            },
        },
    },
    tags: ['autodocs'],
    argTypes: {
        context: {
            control: 'object',
        },
    },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const SingleContext: Story = {
    args: {
        context: [
            {
                text: 'RAG (Retrieval-Augmented Generation) is a technique that combines the power of large language models with external knowledge retrieval to provide more accurate and up-to-date responses.',
                score: 0.95,
                metadata: { source: 'rag-overview.pdf', page: 1 },
            },
        ],
    },
};

export const MultipleContexts: Story = {
    args: {
        context: [
            {
                text: 'RAG systems work by first retrieving relevant documents from a knowledge base, then using those documents as context for the language model to generate responses.',
                score: 0.92,
                metadata: { source: 'rag-guide.pdf', page: 3 },
            },
            {
                text: "The retrieval step typically uses vector similarity search to find the most relevant chunks based on semantic similarity to the users's query.",
                score: 0.88,
                metadata: { source: 'vector-search.pdf', page: 7 },
            },
            {
                text: 'Document chunking strategies include character-based, sentence-based, and paragraph-based approaches, each with different trade-offs.',
                score: 0.85,
                metadata: { source: 'chunking-strategies.pdf', page: 2 },
            },
        ],
    },
};

export const HighRelevance: Story = {
    args: {
        context: [
            {
                text: 'Vector databases like Qdrant, Pinecone, and Weaviate are commonly used for storing and searching document embeddings in RAG systems.',
                score: 0.97,
                metadata: { source: 'vector-databases.pdf', page: 1 },
            },
            {
                text: 'Qdrant provides high-performance vector similarity search with support for various distance metrics including cosine similarity, Euclidean distance, and dot product.',
                score: 0.94,
                metadata: { source: 'qdrant-guide.pdf', page: 5 },
            },
        ],
    },
};

export const WithPageNumbers: Story = {
    args: {
        context: [
            {
                text: 'The chunking process divides documents into smaller, manageable pieces that can be individually embedded and retrieved. This is crucial for efficient processing and semantic search.',
                score: 0.91,
                metadata: { source: 'document-processing.pdf', page: 12 },
            },
            {
                text: 'Overlap between chunks helps maintain context continuity across chunk boundaries, reducing the chance of losing important information at split points.',
                score: 0.87,
                metadata: { source: 'document-processing.pdf', page: 13 },
            },
            {
                text: 'Different embedding models have different optimal chunk sizes. Smaller chunks work better for precise retrieval, while larger chunks maintain more context.',
                score: 0.83,
                metadata: { source: 'embedding-models.pdf', page: 8 },
            },
        ],
    },
};
