/**
 * Workspace types for multi-workspace document and chat management
 */

export interface RagConfig {
    id: number;
    workspace_id: number;
    embedding_model: string;
    retriever_type: string;
    chunk_size: number;
    chunk_overlap?: number;
    top_k?: number;
    created_at: string;
    updated_at: string;
}

export interface Workspace {
    id: number;
    name: string;
    description?: string;
    created_at: string;
    updated_at: string;
    rag_config?: RagConfig;
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
    rag_config?: CreateRagConfigRequest;
}

export interface UpdateWorkspaceRequest {
    name?: string;
    description?: string;
}

export interface CreateRagConfigRequest {
    embedding_model: string;
    retriever_type: string;
    chunk_size: number;
    chunk_overlap?: number;
    top_k?: number;
}

export interface UpdateRagConfigRequest {
    embedding_model?: string;
    retriever_type?: string;
    chunk_size?: number;
    chunk_overlap?: number;
    top_k?: number;
}
