// Shared types for InsightHub across CLI and Client

// ===== AUTHENTICATION TYPES =====

export interface User {
  id: number;
  email: string;
  full_name?: string;
  created_at: string;
  theme_preference?: "light" | "dark";
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name?: string;
}

// ===== WORKSPACE TYPES =====

// Separate config types for Vector and Graph RAG
export interface VectorRagConfig {
  id?: number;
  workspace_id: number;
  embedding_algorithm: string;
  chunking_algorithm: string;
  chunk_size: number;
  chunk_overlap: number;
  top_k: number;
  rerank_enabled: boolean;
  rerank_algorithm?: string;
  created_at?: string;
  updated_at?: string;
}

export interface GraphRagConfig {
  id?: number;
  workspace_id: number;
  entity_extraction_algorithm: string;
  relationship_extraction_algorithm: string;
  clustering_algorithm: string;
  max_hops: number;
  min_cluster_size: number;
  max_cluster_size: number;
  created_at?: string;
  updated_at?: string;
}

// Legacy types for backward compatibility
export interface BaseRagConfig {
  retriever_type: "vector" | "graph";
}

export type RagConfig = (VectorRagConfig | GraphRagConfig) & {
  id: number;
  workspace_id: number;
  created_at: string;
  updated_at: string;
};

export type CreateRagConfigRequest = VectorRagConfig | GraphRagConfig;
export type UpdateRagConfigRequest =
  | Partial<VectorRagConfig>
  | Partial<GraphRagConfig>;

export interface Workspace {
  id: number;
  name: string;
  description?: string;
  status: "provisioning" | "ready" | "failed" | "deleting";
  rag_config?: RagConfig;
  document_count?: number;
  session_count?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateWorkspaceRequest {
  name: string;
  description?: string;
  rag_type?: string;
  rag_config?: CreateRagConfigRequest;
}

export interface UpdateWorkspaceRequest {
  name?: string;
  description?: string;
  status?: "provisioning" | "ready" | "failed";
}

// ===== DOCUMENT TYPES =====

export interface Document {
  id: string;
  filename: string;
  content_type: string;
  file_size: number;
  status:
    | "pending"
    | "parsing"
    | "chunking"
    | "embedding"
    | "indexing"
    | "ready"
    | "failed";
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface UploadResponse {
  message: string;
  document: Document;
}

export interface DocumentsListResponse {
  documents: Document[];
  count: number;
}

// ===== CHAT TYPES =====

export interface Context {
  text: string;
  score: number;
  metadata: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatRequest {
  content: string;
  rag_mode?: "vector" | "graph" | "hybrid";
}

export interface ChatResponse {
  message: string;
  message_id: string;
}

// ===== API RESPONSE TYPES =====

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// ===== CONFIGURATION TYPES =====

export interface CliConfig {
  api: {
    url: string;
    timeout: number;
    retries: number;
  };
  workspace: {
    default?: string;
    autoCreate: boolean;
  };
  output: {
    format: "table" | "json" | "yaml";
    color: boolean;
    pager?: string;
  };
  chat: {
    streaming: boolean;
    showSources: boolean;
    saveHistory: boolean;
  };
  upload: {
    chunkSize: string;
    parallel: number;
    autoProcess: boolean;
  };
}

// ===== HEALTH CHECK TYPES =====

export interface HealthResponse {
  status: string;
  version?: string;
  services?: Record<string, string>;
}
