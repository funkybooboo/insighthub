import { render } from '@testing-library/react';
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

    it('renders without crashing', () => {
        expect(() => render(<RagConfigForm {...defaultProps} />)).not.toThrow();
    });

    it('accepts initial config', () => {
        const initialConfig = {
            retriever_type: 'vector' as const,
            embedding_model: 'nomic-embed-text',
            chunk_size: 1500,
        };

        expect(() =>
            render(<RagConfigForm {...defaultProps} initialConfig={initialConfig} />)
        ).not.toThrow();
    });

    it('respects readOnly prop', () => {
        expect(() => render(<RagConfigForm {...defaultProps} readOnly={true} />)).not.toThrow();
    });

    it('handles configuration changes', () => {
        render(<RagConfigForm {...defaultProps} />);
        expect(mockOnConfigChange).toHaveBeenCalled();
    });
});
