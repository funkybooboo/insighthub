/**
 * Workspace types for multi-workspace document and chat management
 */

// Common RAG configuration properties
export interface BaseRagConfig {
    retriever_type: 'vector' | 'graph'; // Discriminant property
    // Add any other properties common to both Vector and Graph RAG
}

// Vector RAG specific configuration
export interface VectorRagConfig extends BaseRagConfig {
    retriever_type: 'vector';
    embedding_model: string;
    chunk_size: number;
    chunk_overlap?: number;
    top_k?: number;
    rerank_enabled?: boolean;
    rerank_model?: string;
}

// Graph RAG specific configuration
export interface GraphRagConfig extends BaseRagConfig {
    retriever_type: 'graph';
    max_hops?: number;
    entity_extraction_model?: string;
    relationship_extraction_model?: string;
    // Add other graph-specific algorithm fields here
}

// Union type for the full RAG configuration received from the backend
export type RagConfig = (VectorRagConfig | GraphRagConfig) & {
    id: number;
    workspace_id: number;
    created_at: string;
    updated_at: string;
};

// Request type for creating RAG configuration - client sends either Vector or Graph specific config
export type CreateRagConfigRequest = VectorRagConfig | GraphRagConfig;

// Request type for updating RAG configuration - client sends partial updates for either
export type UpdateRagConfigRequest = Partial<VectorRagConfig> | Partial<GraphRagConfig>;

export interface Workspace {
    id: number;
    name: string;
    description?: string;
    status: 'provisioning' | 'ready' | 'failed' | 'deleting'; // Added deleting status
    created_at: string;
    updated_at: string;
    rag_config?: RagConfig; // Now uses the union type
    document_count?: number;
    session_count?: number;
}

export interface WorkspaceState {
    workspaces: Workspace[];
    activeWorkspaceId: number | null;
    isLoading: boolean;
    error: string | null;
}

export interface CreateWorkspaceRequest {
    name: string;
    description?: string;
    rag_config?: CreateRagConfigRequest; // Now uses the union type
}

export interface UpdateWorkspaceRequest {
    name?: string;
    description?: string;
    status?: 'provisioning' | 'ready' | 'failed';
}
