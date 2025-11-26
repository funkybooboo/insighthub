/**
  * API service for communicating with the InsightHub backend.
  */

import axios, { type AxiosInstance } from 'axios';
import { logger } from '../lib/logger';
import type {
    Workspace,
    RagConfig,
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
    CreateRagConfigRequest,
    UpdateRagConfigRequest,
    VectorRagConfig,
    GraphRagConfig,
} from '../types/workspace';
import type { Context } from '../types/chat';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Chat request interface
export interface ChatRequest {
    message: string;
    session_id?: number;
    rag_type?: string;
}

// Client-specific request types
export interface ClientChatRequest extends ChatRequest {
    message: string;
    session_id?: number;
    workspace_id?: number;
    rag_type?: string;
}

export interface UpdatePreferencesRequest {
    theme_preference?: 'light' | 'dark';
}

export interface ChatContext {
    text: string;
    score: number;
    metadata: Record<string, unknown>;
}

export interface ChatResponse {
    answer: string;
    context: ChatContext[];
    session_id: number;
    documents_count: number;
}

export interface Document {
    id: number;
    filename: string;
    file_size: number;
    mime_type: string;
    chunk_count?: number;
    created_at: string;
}

export interface UploadResponse {
    message: string;
    document: Document;
}

export interface DocumentsListResponse {
    documents: Document[];
    count: number;
}

export interface HealthResponse {
    status: string;
}

export interface SignupRequest {
    username: string;
    email: string;
    password: string;
    full_name?: string;
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: {
        id: number;
        username: string;
        email: string;
        full_name: string | null;
        created_at: string;
        theme_preference?: string;
    };
}

export interface UserResponse {
    id: number;
    username: string;
    email: string;
    full_name: string | null;
    created_at: string;
    theme_preference?: string;
}

export interface UpdatePreferencesRequest {
    theme_preference?: 'light' | 'dark';
}

class ApiService {
    private client: AxiosInstance;

    constructor(baseURL: string = API_BASE_URL) {
        this.client = axios.create({
            baseURL,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        this.client.interceptors.request.use(
            (config) => {
                const token = localStorage.getItem('token');
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                logger.debug('API Request', {
                    method: config.method?.toUpperCase(),
                    url: config.url,
                    hasAuth: !!token,
                });
                return config;
            },
            (error) => {
                logger.error('API Request Error', error, {
                    method: error.config?.method?.toUpperCase(),
                    url: error.config?.url,
                });
                return Promise.reject(error);
            }
        );

        this.client.interceptors.response.use(
            (response) => {
                logger.debug('API Response', {
                    method: response.config.method?.toUpperCase(),
                    url: response.config.url,
                    status: response.status,
                });
                return response;
            },
            (error) => {
                logger.error('API Response Error', error, {
                    method: error.config?.method?.toUpperCase(),
                    url: error.config?.url,
                    status: error.response?.status,
                });
                if (error.response?.status === 401) {
                    logger.info('Authentication token expired, redirecting to login');
                    localStorage.removeItem('token');
                    window.location.href = '/login';
                }
                return Promise.reject(error);
            }
        );
    }

    /**
     * Check API health status
     */
    async healthCheck(): Promise<HealthResponse> {
        const { data } = await this.client.get<HealthResponse>('/health');
        return data;
    }

    /**
     * Upload a document (PDF or TXT) to a workspace
     */
    async uploadDocument(workspaceId: number, file: File): Promise<UploadResponse> {
        const formData = new FormData();
        formData.append('file', file);

        const { data } = await this.client.post<UploadResponse>(
            `/api/workspaces/${workspaceId}/documents/upload`,
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            }
        );

        return data;
    }

    /**
     * Send a chats message to a specific workspace and session
     */
    async sendChatMessage(
        workspaceId: number,
        sessionId: number,
        content: string,
        messageType?: string,
        ignoreRag?: boolean
    ): Promise<{ message_id: string }> {
        const { data } = await this.client.post<{ message_id: string }>(
            `/api/workspaces/${workspaceId}/chat/sessions/${sessionId}/messages`,
            { content, message_type: messageType || 'user', ignore_rag: ignoreRag }
        );
        return data;
    }

    /**
     * Cancel a chats message streaming
     */
    async cancelChatMessage(
        workspaceId: number,
        sessionId: number,
        messageId?: string
    ): Promise<{ message: string }> {
        const { data } = await this.client.post<{ message: string }>(
            `/api/workspaces/${workspaceId}/chat/sessions/${sessionId}/cancel`,
            { message_id: messageId }
        );
        return data;
    }

    /**
     * List documents in a workspace
     */
    async listDocuments(workspaceId: number): Promise<DocumentsListResponse> {
        const { data } = await this.client.get<DocumentsListResponse>(
            `/api/workspaces/${workspaceId}/documents`
        );
        return data;
    }

    /**
     * Delete a document from a workspace
     */
    async deleteDocument(workspaceId: number, docId: number): Promise<{ message: string }> {
        const { data } = await this.client.delete<{ message: string }>(
            `/api/workspaces/${workspaceId}/documents/${docId}`
        );
        return data;
    }

    /**
     * Sign up a new users
     */
    async signup(request: SignupRequest): Promise<AuthResponse> {
        const { data } = await this.client.post<AuthResponse>('/api/auth/signup', request);
        return data;
    }

    /**
     * Login a users
     */
    async login(request: LoginRequest): Promise<AuthResponse> {
        const { data } = await this.client.post<AuthResponse>('/api/auth/login', request);
        return data;
    }

    /**
     * Logout the current users
     */
    async logout(): Promise<{ message: string }> {
        const { data } = await this.client.post<{ message: string }>('/api/auth/logout');
        return data;
    }

    /**
     * Get current users information
     */
    async getCurrentUser(): Promise<UserResponse> {
        const { data } = await this.client.get<UserResponse>('/api/auth/me');
        return data;
    }

    /**
     * Update users preferences
     */
    async updatePreferences(request: UpdatePreferencesRequest): Promise<UserResponse> {
        const { data } = await this.client.patch<UserResponse>('/api/auth/preferences', request);
        return data;
    }

    /**
     * Update users profile
     */
    async updateProfile(request: { full_name?: string; email?: string }): Promise<UserResponse> {
        const { data } = await this.client.patch<UserResponse>('/api/auth/profile', request);
        return data;
    }

    /**
     * Change users password
     */
    async changePassword(request: {
        current_password: string;
        new_password: string;
    }): Promise<void> {
        await this.client.post('/api/auth/change-password', request);
    }

    /**
     * List all workspaces
     */
    async listWorkspaces(): Promise<Workspace[]> {
        const { data } = await this.client.get<Workspace[]>('/api/workspaces');
        return data;
    }

    /**
     * Get a specific workspace
     */
    async getWorkspace(workspaceId: number): Promise<Workspace> {
        const { data } = await this.client.get<Workspace>(`/api/workspaces/${workspaceId}`);
        return data;
    }

    /**
     * Create a new workspace
     */
    async createWorkspace(request: CreateWorkspaceRequest): Promise<Workspace> {
        const { data } = await this.client.post<Workspace>('/api/workspaces', request);
        return data;
    }

    /**
     * Update a workspace
     */
    async updateWorkspace(
        workspaceId: number,
        request: UpdateWorkspaceRequest
    ): Promise<Workspace> {
        const { data } = await this.client.patch<Workspace>(
            `/api/workspaces/${workspaceId}`,
            request
        );
        return data;
    }

    /**
     * Delete a workspace
     */
    async deleteWorkspace(workspaceId: number): Promise<{ message: string }> {
        const { data } = await this.client.delete<{ message: string }>(
            `/api/workspaces/${workspaceId}`
        );
        return data;
    }

    /**
     * Get RAG config for a workspace
     */
    async getRagConfig(workspaceId: number): Promise<RagConfig> {
        const { data } = await this.client.get<RagConfig>(
            `/api/workspaces/${workspaceId}/rag-config`
        );
        return data;
    }

    /**
     * Create RAG config for a workspace
     */
    async createRagConfig(
        workspaceId: number,
        request: CreateRagConfigRequest
    ): Promise<RagConfig> {
        const { data } = await this.client.post<RagConfig>(
            `/api/workspaces/${workspaceId}/rag-config`,
            request
        );
        return data;
    }

    /**
     * Update RAG config for a workspace
     */
    async updateRagConfig(
        workspaceId: number,
        request: UpdateRagConfigRequest
    ): Promise<RagConfig> {
        const { data } = await this.client.patch<RagConfig>(
            `/api/workspaces/${workspaceId}/rag-config`,
            request
        );
        return data;
    }

    /**
     * Get Vector RAG config for a workspace
     */
    async getVectorRagConfig(workspaceId: number): Promise<VectorRagConfig> {
        const { data } = await this.client.get<VectorRagConfig>(
            `/api/workspaces/${workspaceId}/vector-rag-config`
        );
        return data;
    }

    /**
     * Create Vector RAG config for a workspace
     */
    async createVectorRagConfig(
        workspaceId: number,
        request: Partial<VectorRagConfig>
    ): Promise<VectorRagConfig> {
        const { data } = await this.client.post<VectorRagConfig>(
            `/api/workspaces/${workspaceId}/vector-rag-config`,
            request
        );
        return data;
    }

    /**
     * Update Vector RAG config for a workspace
     */
    async updateVectorRagConfig(
        workspaceId: number,
        request: Partial<VectorRagConfig>
    ): Promise<VectorRagConfig> {
        const { data } = await this.client.patch<VectorRagConfig>(
            `/api/workspaces/${workspaceId}/vector-rag-config`,
            request
        );
        return data;
    }

    /**
     * Get Graph RAG config for a workspace
     */
    async getGraphRagConfig(workspaceId: number): Promise<GraphRagConfig> {
        const { data } = await this.client.get<GraphRagConfig>(
            `/api/workspaces/${workspaceId}/graph-rag-config`
        );
        return data;
    }

    /**
     * Create Graph RAG config for a workspace
     */
    async createGraphRagConfig(
        workspaceId: number,
        request: Partial<GraphRagConfig>
    ): Promise<GraphRagConfig> {
        const { data } = await this.client.post<GraphRagConfig>(
            `/api/workspaces/${workspaceId}/graph-rag-config`,
            request
        );
        return data;
    }

    /**
     * Update Graph RAG config for a workspace
     */
    async updateGraphRagConfig(
        workspaceId: number,
        request: Partial<GraphRagConfig>
    ): Promise<GraphRagConfig> {
        const { data } = await this.client.patch<GraphRagConfig>(
            `/api/workspaces/${workspaceId}/graph-rag-config`,
            request
        );
        return data;
    }

    /**
     * Get available algorithms for Vector RAG
     */
    async getVectorAlgorithms(): Promise<{
        embedding_algorithms: Array<{ value: string; label: string }>;
        chunking_algorithms: Array<{ value: string; label: string }>;
        rerank_algorithms: Array<{ value: string; label: string }>;
    }> {
        const { data } = await this.client.get('/api/algorithms/vector');
        return data;
    }

    /**
     * Get available algorithms for Graph RAG
     */
    async getGraphAlgorithms(): Promise<{
        entity_extraction_algorithms: Array<{ value: string; label: string }>;
        relationship_extraction_algorithms: Array<{ value: string; label: string }>;
        clustering_algorithms: Array<{ value: string; label: string }>;
    }> {
        const { data } = await this.client.get('/api/algorithms/graph');
        return data;
    }

    /**
     * Get users's default RAG config
     */
    async getDefaultRagConfig(): Promise<DefaultRagConfig | null> {
        try {
            const { data } = await this.client.get<DefaultRagConfig>(
                '/api/auth/default-rag-config'
            );
            return data;
        } catch (error) {
            // Return null if config doesn't exist yet
            if ((error as { response?: { status: number } }).response?.status === 404) {
                return null;
            }
            throw error;
        }
    }

    /**
     * Save users's default RAG config
     */
    async saveDefaultRagConfig(config: DefaultRagConfig): Promise<DefaultRagConfig> {
        const { data } = await this.client.put<DefaultRagConfig>(
            '/api/auth/default-rag-config',
            config
        );
        return data;
    }

    /**
     * Fetch a Wikipedia article and inject it into the RAG system.
     */
    async fetchWikipediaArticle(workspaceId: number, query: string): Promise<{ message: string }> {
        const { data } = await this.client.post<{ message: string }>(
            `/api/workspaces/${workspaceId}/documents/fetch-wikipedia`,
            { query }
        );
        return data;
    }

    /**
     * Create a new chats session for a workspace
     */
    async createChatSession(
        workspaceId: number,
        title?: string
    ): Promise<{ session_id: number; title: string }> {
        const { data } = await this.client.post<{ session_id: number; title: string }>(
            `/api/workspaces/${workspaceId}/chat/sessions`,
            { title }
        );
        return data;
    }

    /**
     * Get all chats sessions for a workspace
     */
    async getChatSessions(workspaceId: number): Promise<
        Array<{
            session_id: number;
            title: string;
            created_at: string;
            updated_at: string;
            message_count: number;
        }>
    > {
        const { data } = await this.client.get<
            Array<{
                session_id: number;
                title: string;
                created_at: string;
                updated_at: string;
                message_count: number;
            }>
        >(`/api/workspaces/${workspaceId}/chat/sessions`);
        return data;
    }

    /**
     * Delete a chats session from a workspace
     */
    async deleteChatSession(workspaceId: number, sessionId: number): Promise<{ message: string }> {
        const { data } = await this.client.delete<{ message: string }>(
            `/api/workspaces/${workspaceId}/chat/sessions/${sessionId}`
        );
        return data;
    }
}

export type DefaultRagConfig = VectorRagConfig | GraphRagConfig;

export const apiService = new ApiService();
export default apiService;
