import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import RagConfigForm from './RagConfigForm';

// Mock all UI dependencies to avoid complex rendering issues
vi.mock('@/lib/utils', () => ({
    cn: (...classes: (string | undefined | null | false)[]) => classes.filter(Boolean).join(' '),
}));

vi.mock('class-variance-authority', () => ({
    cva: vi.fn(() => vi.fn(() => '')),
}));

vi.mock('@radix-ui/react-slot', () => ({
    Slot: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
        <div {...props}>{children}</div>
    ),
}));

// Mock input components
vi.mock('@/components/ui/button', () => ({
    Button: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
        <button {...props}>{children}</button>
    ),
}));

vi.mock('@/components/ui/input', () => ({
    Input: (props: Record<string, unknown>) => <input {...props} />,
}));

vi.mock('@/components/ui/select', () => ({
    Select: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
        <select {...props}>{children}</select>
    ),
    SelectContent: ({ children }: React.PropsWithChildren<Record<string, unknown>>) => (
        <div>{children}</div>
    ),
    SelectItem: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
        <option {...props}>{children}</option>
    ),
    SelectTrigger: ({ children }: React.PropsWithChildren<Record<string, unknown>>) => (
        <div>{children}</div>
    ),
    SelectValue: (props: Record<string, unknown>) => <span {...props} />,
}));

vi.mock('@/components/ui/checkbox', () => ({
    Checkbox: (props: Record<string, unknown>) => <input type="checkbox" {...props} />,
}));

vi.mock('@/components/ui/label', () => ({
    Label: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
        <label {...props}>{children}</label>
    ),
}));

describe('RagConfigForm', () => {
    const mockOnConfigChange = vi.fn();

    const defaultProps = {
        onConfigChange: mockOnConfigChange,
        readOnly: false,
    };

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Initial Rendering', () => {
    it('renders without crashing', () => {
        const { container } = render(<RagConfigForm {...defaultProps} />);
        expect(container).toBeInTheDocument();
        screen.debug(); // Debug what is actually rendered
    });

        it('renders RAG type selector with default vector option', () => {
            render(<RagConfigForm {...defaultProps} />);
            const select = document.querySelector('select[name="retriever_type"]') as HTMLSelectElement;
            expect(select).toBeInTheDocument();
            expect(select.value).toBe('vector');
        });

        it('renders Vector RAG fields by default', () => {
            render(<RagConfigForm {...defaultProps} />);
            expect(screen.getByDisplayValue('Nomic Embed Text')).toBeInTheDocument(); // Embedding Model
            expect(screen.getByDisplayValue('1000')).toBeInTheDocument(); // Chunk Size
            expect(screen.getByDisplayValue('200')).toBeInTheDocument(); // Chunk Overlap
            expect(screen.getByDisplayValue('8')).toBeInTheDocument(); // Top K
            expect(screen.getByText('Enable Reranking')).toBeInTheDocument(); // Checkbox label
        });

        it('does not render Graph RAG fields by default', () => {
            render(<RagConfigForm {...defaultProps} />);
            expect(screen.queryByLabelText('Max Hops (Graph Traversal)')).not.toBeInTheDocument();
            expect(screen.queryByLabelText('Entity Extraction Model')).not.toBeInTheDocument();
            expect(screen.queryByLabelText('Relationship Extraction Model')).not.toBeInTheDocument();
        });
    });

    describe('RAG Type Switching', () => {
        it('switches to Graph RAG when selected', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const ragTypeSelect = screen.getByLabelText('RAG Type');

            fireEvent.change(ragTypeSelect, { target: { value: 'graph' } });

            await waitFor(() => {
                expect(screen.getByLabelText('Max Hops (Graph Traversal)')).toBeInTheDocument();
                expect(screen.getByLabelText('Entity Extraction Model')).toBeInTheDocument();
                expect(screen.getByLabelText('Relationship Extraction Model')).toBeInTheDocument();
            });

            // Vector fields should be hidden
            expect(screen.queryByLabelText('Embedding Model')).not.toBeInTheDocument();
            expect(screen.queryByLabelText('Chunk Size')).not.toBeInTheDocument();
        });

        it('switches back to Vector RAG when selected', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const ragTypeSelect = screen.getByLabelText('RAG Type');

            // Switch to graph first
            fireEvent.change(ragTypeSelect, { target: { value: 'graph' } });
            await waitFor(() => {
                expect(screen.getByLabelText('Max Hops (Graph Traversal)')).toBeInTheDocument();
            });

            // Switch back to vector
            fireEvent.change(ragTypeSelect, { target: { value: 'vector' } });
            await waitFor(() => {
                expect(screen.getByLabelText('Embedding Model')).toBeInTheDocument();
                expect(screen.getByLabelText('Chunk Size')).toBeInTheDocument();
            });

            // Graph fields should be hidden
            expect(screen.queryByLabelText('Max Hops (Graph Traversal)')).not.toBeInTheDocument();
        });

        it('calls onConfigChange with correct config when switching RAG types', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const ragTypeSelect = screen.getByLabelText('RAG Type');

            fireEvent.change(ragTypeSelect, { target: { value: 'graph' } });

            await waitFor(() => {
                expect(mockOnConfigChange).toHaveBeenCalledWith(
                    expect.objectContaining({
                        retriever_type: 'graph',
                        max_hops: 2,
                        entity_extraction_model: 'ollama',
                        relationship_extraction_model: 'ollama',
                    })
                );
            });
        });
    });

    describe('Vector RAG Configuration', () => {
        it('updates embedding model when changed', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const embeddingSelect = screen.getByLabelText('Embedding Model');

            fireEvent.change(embeddingSelect, { target: { value: 'openai' } });

            await waitFor(() => {
                expect(mockOnConfigChange).toHaveBeenCalledWith(
                    expect.objectContaining({
                        retriever_type: 'vector',
                        embedding_model: 'openai',
                    })
                );
            });
        });

        it('updates chunk size when changed', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const chunkSizeInput = screen.getByLabelText('Chunk Size');

            fireEvent.change(chunkSizeInput, { target: { value: '1500' } });

            await waitFor(() => {
                expect(mockOnConfigChange).toHaveBeenCalledWith(
                    expect.objectContaining({
                        retriever_type: 'vector',
                        chunk_size: 1500,
                    })
                );
            });
        });

        it('updates chunk overlap when changed', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const chunkOverlapInput = screen.getByLabelText('Chunk Overlap');

            fireEvent.change(chunkOverlapInput, { target: { value: '300' } });

            await waitFor(() => {
                expect(mockOnConfigChange).toHaveBeenCalledWith(
                    expect.objectContaining({
                        retriever_type: 'vector',
                        chunk_overlap: 300,
                    })
                );
            });
        });

        it('updates top k when changed', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const topKInput = screen.getByLabelText('Top K (Retrieval)');

            fireEvent.change(topKInput, { target: { value: '12' } });

            await waitFor(() => {
                expect(mockOnConfigChange).toHaveBeenCalledWith(
                    expect.objectContaining({
                        retriever_type: 'vector',
                        top_k: 12,
                    })
                );
            });
        });

        it('toggles reranking when checkbox is clicked', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const rerankCheckbox = screen.getByLabelText('Enable Reranking');

            fireEvent.click(rerankCheckbox);

            await waitFor(() => {
                expect(mockOnConfigChange).toHaveBeenCalledWith(
                    expect.objectContaining({
                        retriever_type: 'vector',
                        rerank_enabled: true,
                        rerank_model: 'rerank-model-1',
                    })
                );
            });
        });

        it('shows rerank model selector when reranking is enabled', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const rerankCheckbox = screen.getByLabelText('Enable Reranking');

            fireEvent.click(rerankCheckbox);

            await waitFor(() => {
                expect(screen.getByLabelText('Rerank Model')).toBeInTheDocument();
            });
        });

        it('hides rerank model selector when reranking is disabled', () => {
            render(<RagConfigForm {...defaultProps} />);
            expect(screen.queryByLabelText('Rerank Model')).not.toBeInTheDocument();
        });
    });

    describe('Graph RAG Configuration', () => {
        it('renders Graph RAG fields when graph type is selected', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const ragTypeSelect = screen.getByLabelText('RAG Type');

            fireEvent.change(ragTypeSelect, { target: { value: 'graph' } });

            await waitFor(() => {
                expect(screen.getByLabelText('Max Hops (Graph Traversal)')).toBeInTheDocument();
                expect(screen.getByLabelText('Entity Extraction Model')).toBeInTheDocument();
                expect(screen.getByLabelText('Relationship Extraction Model')).toBeInTheDocument();
            });
        });

        it('updates max hops when changed', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const ragTypeSelect = screen.getByLabelText('RAG Type');
            fireEvent.change(ragTypeSelect, { target: { value: 'graph' } });

            await waitFor(() => {
                const maxHopsInput = screen.getByLabelText('Max Hops (Graph Traversal)');
                fireEvent.change(maxHopsInput, { target: { value: '3' } });
            });

            await waitFor(() => {
                expect(mockOnConfigChange).toHaveBeenCalledWith(
                    expect.objectContaining({
                        retriever_type: 'graph',
                        max_hops: 3,
                    })
                );
            });
        });

        it('updates entity extraction model when changed', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const ragTypeSelect = screen.getByLabelText('RAG Type');
            fireEvent.change(ragTypeSelect, { target: { value: 'graph' } });

            await waitFor(() => {
                const entityModelSelect = screen.getByLabelText('Entity Extraction Model');
                fireEvent.change(entityModelSelect, { target: { value: 'spacy' } });
            });

            await waitFor(() => {
                expect(mockOnConfigChange).toHaveBeenCalledWith(
                    expect.objectContaining({
                        retriever_type: 'graph',
                        entity_extraction_model: 'spacy',
                    })
                );
            });
        });
    });

    describe('Initial Configuration', () => {
        it('accepts initial vector config', () => {
            const initialConfig = {
                retriever_type: 'vector' as const,
                embedding_model: 'openai',
                chunk_size: 1500,
                chunk_overlap: 300,
                top_k: 10,
                rerank_enabled: true,
                rerank_model: 'rerank-model-2',
            };

            render(<RagConfigForm {...defaultProps} initialConfig={initialConfig} />);

            expect(screen.getByLabelText('RAG Type')).toHaveValue('vector');
            expect(screen.getByLabelText('Embedding Model')).toHaveValue('openai');
            expect(screen.getByLabelText('Chunk Size')).toHaveValue(1500);
            expect(screen.getByLabelText('Chunk Overlap')).toHaveValue(300);
            expect(screen.getByLabelText('Top K (Retrieval)')).toHaveValue(10);
            expect(screen.getByLabelText('Enable Reranking')).toBeChecked();
            expect(screen.getByLabelText('Rerank Model')).toHaveValue('rerank-model-2');
        });

        it('accepts initial graph config', () => {
            const initialConfig = {
                retriever_type: 'graph' as const,
                max_hops: 3,
                entity_extraction_model: 'spacy',
                relationship_extraction_model: 'custom',
            };

            render(<RagConfigForm {...defaultProps} initialConfig={initialConfig} />);

            expect(screen.getByLabelText('RAG Type')).toHaveValue('graph');
            expect(screen.getByLabelText('Max Hops (Graph Traversal)')).toHaveValue(3);
            expect(screen.getByLabelText('Entity Extraction Model')).toHaveValue('spacy');
            expect(screen.getByLabelText('Relationship Extraction Model')).toHaveValue('custom');
        });

        it('defaults to vector RAG when no retriever_type specified', () => {
            const initialConfig = {
                embedding_model: 'openai',
            };

            render(<RagConfigForm {...defaultProps} initialConfig={initialConfig} />);

            expect(screen.getByLabelText('RAG Type')).toHaveValue('vector');
            expect(screen.getByLabelText('Embedding Model')).toHaveValue('openai');
        });
    });

    describe('Read-only Mode', () => {
        it('disables all form inputs when readOnly is true', () => {
            render(<RagConfigForm {...defaultProps} readOnly={true} />);

            const ragTypeSelect = screen.getByLabelText('RAG Type');
            const embeddingSelect = screen.getByLabelText('Embedding Model');
            const chunkSizeInput = screen.getByLabelText('Chunk Size');
            const chunkOverlapInput = screen.getByLabelText('Chunk Overlap');
            const topKInput = screen.getByLabelText('Top K (Retrieval)');
            const rerankCheckbox = screen.getByLabelText('Enable Reranking');

            expect(ragTypeSelect).toBeDisabled();
            expect(embeddingSelect).toBeDisabled();
            expect(chunkSizeInput).toBeDisabled();
            expect(chunkOverlapInput).toBeDisabled();
            expect(topKInput).toBeDisabled();
            expect(rerankCheckbox).toBeDisabled();
        });
    });

    describe('Configuration Changes Callback', () => {
        it('calls onConfigChange with initial config on mount', () => {
            render(<RagConfigForm {...defaultProps} />);
            expect(mockOnConfigChange).toHaveBeenCalledWith(
                expect.objectContaining({
                    retriever_type: 'vector',
                    embedding_model: 'nomic-embed-text',
                    chunk_size: 1000,
                    chunk_overlap: 200,
                    top_k: 8,
                    rerank_enabled: false,
                })
            );
        });

        it('calls onConfigChange whenever config changes', async () => {
            render(<RagConfigForm {...defaultProps} />);
            const chunkSizeInput = screen.getByLabelText('Chunk Size');

            fireEvent.change(chunkSizeInput, { target: { value: '1200' } });

            await waitFor(() => {
                expect(mockOnConfigChange).toHaveBeenCalledTimes(2); // Initial + change
                expect(mockOnConfigChange).toHaveBeenLastCalledWith(
                    expect.objectContaining({
                        retriever_type: 'vector',
                        chunk_size: 1200,
                    })
                );
            });
        });
    });
});
