/**
 * Workspace types for multi-workspace document and chats management
 * Local implementation replacing shared package
 */

// Base RAG configuration
export interface BaseRagConfig {
    embedding_model?: string;
    embedding_dim?: number | null;
    retriever_type?: string;
    chunk_size?: number;
    chunk_overlap?: number;
    top_k?: number;
    rerank_enabled?: boolean;
    rerank_model?: string | null;
}

// Vector RAG configuration
export interface VectorRagConfig extends BaseRagConfig {
    embedding_algorithm?: string;
    chunking_algorithm?: string;
    rerank_algorithm?: string;
}

// Graph RAG configuration
export interface GraphRagConfig extends BaseRagConfig {
    entity_extraction_algorithm?: string;
    relationship_extraction_algorithm?: string;
    clustering_algorithm?: string;
}

// Union type for RAG configurations
export type RagConfig = VectorRagConfig | GraphRagConfig;

// Workspace model
export interface Workspace {
    id: number;
    user_id?: number;
    name: string;
    description: string | null;
    rag_type: string;
    status?: string;
    created_at: string;
    updated_at: string;
    document_count?: number;
}

// Request types for workspace operations
export interface CreateWorkspaceRequest {
    name: string;
    description?: string;
    rag_type?: string;
    rag_config?: CreateRagConfigRequest;
}

export interface UpdateWorkspaceRequest {
    name?: string;
    description?: string;
}

// Request types for RAG config operations
export interface CreateRagConfigRequest {
    rag_type: string;
    config: RagConfig;
}

export interface UpdateRagConfigRequest {
    rag_type?: string;
    config?: RagConfig;
}

// Legacy type for backward compatibility - represents RAG config as flat object
export interface FlatRagConfig {
    embedding_algorithm?: string;
    chunking_algorithm?: string;
    rerank_algorithm?: string;
    chunk_size?: number;
    chunk_overlap?: number;
    top_k?: number;
    rerank_enabled?: boolean;
}

// Client-specific extensions
export interface WorkspaceState {
    workspaces: Workspace[];
    activeWorkspaceId: number | null;
    isLoading: boolean;
    error: string | null;
}
