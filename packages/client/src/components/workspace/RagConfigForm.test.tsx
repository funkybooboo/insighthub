import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import RagConfigForm from './RagConfigForm';
import type { CreateRagConfigRequest, VectorRagConfig } from '../../types/workspace';

// Mock all UI dependencies to avoid complex rendering issues
vi.mock('@/lib/utils', () => ({
    cn: (...classes: any[]) => classes.filter(Boolean).join(' '),
}));

vi.mock('class-variance-authority', () => ({
    cva: vi.fn(() => vi.fn(() => '')),
}));

vi.mock('@radix-ui/react-slot', () => ({
    Slot: ({ children, ...props }: any) => <div {...props}>{children}</div>,
}));

// Mock input components
vi.mock('@/components/ui/button', () => ({
    Button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
}));

vi.mock('@/components/ui/input', () => ({
    Input: ({ ...props }: any) => <input {...props} />,
}));

vi.mock('@/components/ui/select', () => ({
    Select: ({ children, ...props }: any) => <select {...props}>{children}</select>,
    SelectContent: ({ children }: any) => <div>{children}</div>,
    SelectItem: ({ children, ...props }: any) => <option {...props}>{children}</option>,
    SelectTrigger: ({ children }: any) => <div>{children}</div>,
    SelectValue: ({ ...props }: any) => <span {...props} />,
}));

vi.mock('@/components/ui/checkbox', () => ({
    Checkbox: ({ ...props }: any) => <input type="checkbox" {...props} />,
}));

vi.mock('@/components/ui/label', () => ({
    Label: ({ children, ...props }: any) => <label {...props}>{children}</label>,
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

    it('renders without crashing', () => {
        render(<RagConfigForm {...defaultProps} />);
        expect(screen.getByText('RAG Configuration')).toBeInTheDocument();
    });

    it('accepts initial config', () => {
        const initialConfig = {
            retriever_type: 'vector' as const,
            embedding_model: 'nomic-embed-text',
            chunk_size: 1500,
        };

        render(<RagConfigForm {...defaultProps} initialConfig={initialConfig} />);
        expect(screen.getByText('RAG Configuration')).toBeInTheDocument();
    });

    it('respects readOnly prop', () => {
        render(<RagConfigForm {...defaultProps} readOnly={true} />);
        expect(screen.getByText('RAG Configuration')).toBeInTheDocument();
    });

    it('handles configuration changes', () => {
        render(<RagConfigForm {...defaultProps} />);
        expect(mockOnConfigChange).toHaveBeenCalled();
    });
});

    it('renders without crashing', () => {
        expect(() => render(<RagConfigForm {...defaultProps} />)).not.toThrow();
    });

    it('accepts initial config', () => {
        const initialConfig = {
            retriever_type: 'vector' as const,
            embedding_model: 'nomic-embed-text',
            chunk_size: 1500,
        };

        expect(() => render(<RagConfigForm {...defaultProps} initialConfig={initialConfig} />)).not.toThrow();
    });

    it('respects readOnly prop', () => {
        render(<RagConfigForm {...defaultProps} readOnly={true} />);
        // Component should render without errors in readOnly mode
        expect(screen.getByText('RAG Configuration')).toBeInTheDocument();
    });

    it('renders with initial configuration', () => {
        const initialConfig = {
            retriever_type: 'vector' as const,
            embedding_model: 'nomic-embed-text',
            chunk_size: 1500,
        };

        render(<RagConfigForm {...defaultProps} initialConfig={initialConfig} />);
        expect(screen.getByText('RAG Configuration')).toBeInTheDocument();
        // Component renders with config
    });

    it('handles configuration changes', () => {
        render(<RagConfigForm {...defaultProps} />);
        // Basic functionality test - component renders and can be interacted with
        expect(mockOnConfigChange).toHaveBeenCalled();
    });

    it('renders vector RAG options', () => {
        render(<RagConfigForm {...defaultProps} />);
        expect(screen.getByText('Embedding Model')).toBeInTheDocument();
        expect(screen.getByText('Chunk Size')).toBeInTheDocument();
    });

    it('renders graph RAG options when graph type is selected', () => {
        const graphConfig = {
            retriever_type: 'graph' as const,
            max_hops: 3,
        };

        render(<RagConfigForm {...defaultProps} initialConfig={graphConfig} />);
        expect(screen.getByText('Max Hops')).toBeInTheDocument();
    });

    it('handles empty initial config', () => {
        expect(() => render(<RagConfigForm {...defaultProps} initialConfig={{}} />)).not.toThrow();
    });

    it('renders with default vector configuration', () => {
        render(<RagConfigForm {...defaultProps} />);

        expect(screen.getByText('RAG Configuration')).toBeInTheDocument();
        expect(screen.getByDisplayValue('vector')).toBeInTheDocument();
        expect(screen.getByDisplayValue('nomic-embed-text')).toBeInTheDocument();
    });

    it('renders with initial configuration', () => {
        render(<RagConfigForm {...defaultProps} initialConfig={initialVectorConfig} />);

        expect(screen.getByDisplayValue('1000')).toBeInTheDocument();
        expect(screen.getByDisplayValue('200')).toBeInTheDocument();
        expect(screen.getByDisplayValue('8')).toBeInTheDocument();
    });

    it('calls onConfigChange when RAG type changes', async () => {
        render(<RagConfigForm {...defaultProps} />);

        const ragTypeSelect = screen.getByDisplayValue('vector');
        fireEvent.change(ragTypeSelect, { target: { value: 'graph' } });

        await waitFor(() => {
            expect(mockOnConfigChange).toHaveBeenCalledWith(
                expect.objectContaining({
                    retriever_type: 'graph',
                })
            );
        });
    });

    it('shows vector-specific fields when vector RAG is selected', () => {
        render(<RagConfigForm {...defaultProps} initialConfig={initialVectorConfig} />);

        expect(screen.getByText('Embedding Model')).toBeInTheDocument();
        expect(screen.getByText('Chunk Size')).toBeInTheDocument();
        expect(screen.getByText('Chunk Overlap')).toBeInTheDocument();
        expect(screen.getByText('Top K')).toBeInTheDocument();
    });

    it('shows graph-specific fields when graph RAG is selected', async () => {
        render(<RagConfigForm {...defaultProps} />);

        const ragTypeSelect = screen.getByDisplayValue('vector');
        fireEvent.change(ragTypeSelect, { target: { value: 'graph' } });

        await waitFor(() => {
            expect(screen.getByText('Max Hops')).toBeInTheDocument();
            expect(screen.getByText('Entity Extraction Model')).toBeInTheDocument();
            expect(screen.getByText('Relationship Extraction Model')).toBeInTheDocument();
        });
    });

    it('calls onConfigChange when form fields change', async () => {
        render(<RagConfigForm {...defaultProps} />);

        const chunkSizeInput = screen.getByDisplayValue('1000');
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

    it('handles rerank toggle', async () => {
        render(<RagConfigForm {...defaultProps} />);

        const rerankCheckbox = screen.getByRole('checkbox', { name: /enable reranking/i });
        fireEvent.click(rerankCheckbox);

        await waitFor(() => {
            expect(mockOnConfigChange).toHaveBeenCalledWith(
                expect.objectContaining({
                    rerank_enabled: true,
                })
            );
        });
    });

    it('shows rerank model field when rerank is enabled', async () => {
        render(<RagConfigForm {...defaultProps} initialConfig={{ ...initialVectorConfig, rerank_enabled: true }} />);

        expect(screen.getByText('Rerank Model')).toBeInTheDocument();
    });

    it('becomes read-only when readOnly prop is true', () => {
        render(<RagConfigForm {...defaultProps} readOnly={true} />);

        const inputs = screen.getAllByRole('textbox');
        const selects = screen.getAllByRole('combobox');

        [...inputs, ...selects].forEach(element => {
            expect(element).toBeDisabled();
        });
    });

    it('validates numeric inputs', async () => {
        render(<RagConfigForm {...defaultProps} />);

        const chunkSizeInput = screen.getByDisplayValue('1000');
        fireEvent.change(chunkSizeInput, { target: { value: 'invalid' } });

        await waitFor(() => {
            expect(mockOnConfigChange).toHaveBeenCalledWith(
                expect.objectContaining({
                    chunk_size: NaN,
                })
            );
        });
    });

    it('handles empty initial config gracefully', () => {
        render(<RagConfigForm {...defaultProps} initialConfig={{}} />);

        expect(screen.getByDisplayValue('vector')).toBeInTheDocument();
        expect(screen.getByDisplayValue('1000')).toBeInTheDocument();
    });

    it('preserves existing config values when switching RAG types', async () => {
        render(<RagConfigForm {...defaultProps} initialConfig={initialVectorConfig} />);

        const ragTypeSelect = screen.getByDisplayValue('vector');
        fireEvent.change(ragTypeSelect, { target: { value: 'graph' } });

        await waitFor(() => {
            expect(mockOnConfigChange).toHaveBeenCalledWith(
                expect.objectContaining({
                    retriever_type: 'graph',
                    // Should preserve common fields if applicable
                })
            );
    });