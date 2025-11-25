/**
 * API service for communicating with the InsightHub backend.
 */

import axios, { type AxiosInstance } from 'axios';
import type {
    Workspace,
    RagConfig,
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
    CreateRagConfigRequest,
    UpdateRagConfigRequest,
    VectorRagConfig,
    GraphRagConfig,
    ChatRequest,
} from '@insighthub/shared-typescript';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

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
                return config;
            },
            (error) => Promise.reject(error)
        );

        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                if (error.response?.status === 401) {
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
     * Send a chat message to a specific workspace and session
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
     * Cancel a chat message streaming
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
     * Sign up a new user
     */
    async signup(request: SignupRequest): Promise<AuthResponse> {
        const { data } = await this.client.post<AuthResponse>('/api/auth/signup', request);
        return data;
    }

    /**
     * Login a user
     */
    async login(request: LoginRequest): Promise<AuthResponse> {
        const { data } = await this.client.post<AuthResponse>('/api/auth/login', request);
        return data;
    }

    /**
     * Logout the current user
     */
    async logout(): Promise<{ message: string }> {
        const { data } = await this.client.post<{ message: string }>('/api/auth/logout');
        return data;
    }

    /**
     * Get current user information
     */
    async getCurrentUser(): Promise<UserResponse> {
        const { data } = await this.client.get<UserResponse>('/api/auth/me');
        return data;
    }

    /**
     * Update user preferences
     */
    async updatePreferences(request: UpdatePreferencesRequest): Promise<UserResponse> {
        const { data } = await this.client.patch<UserResponse>('/api/auth/preferences', request);
        return data;
    }

    /**
     * Update user profile
     */
    async updateProfile(request: { full_name?: string; email?: string }): Promise<UserResponse> {
        const { data } = await this.client.patch<UserResponse>('/api/auth/profile', request);
        return data;
    }

    /**
     * Change user password
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
     * Get user's default RAG config
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
     * Save user's default RAG config
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
     * Create a new chat session for a workspace
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
     * Get all chat sessions for a workspace
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
     * Delete a chat session from a workspace
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
