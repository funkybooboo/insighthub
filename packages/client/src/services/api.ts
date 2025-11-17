/**
 * API service for communicating with the InsightHub backend.
 */

import axios, { type AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface ChatRequest {
    message: string;
    session_id?: number;
    rag_type?: string;
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
     * Upload a document (PDF or TXT) to the server
     */
    async uploadDocument(file: File): Promise<UploadResponse> {
        const formData = new FormData();
        formData.append('file', file);

        const { data } = await this.client.post<UploadResponse>('/api/documents/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return data;
    }

    /**
     * Send a chat message and get a response from the RAG system
     */
    async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
        const { data } = await this.client.post<ChatResponse>('/api/chat', request);
        return data;
    }

    /**
     * List all uploaded documents
     */
    async listDocuments(): Promise<DocumentsListResponse> {
        const { data } = await this.client.get<DocumentsListResponse>('/api/documents');
        return data;
    }

    /**
     * Delete a document by ID
     */
    async deleteDocument(docId: number): Promise<{ message: string }> {
        const { data } = await this.client.delete<{ message: string }>(`/api/documents/${docId}`);
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
}

export const apiService = new ApiService();
export default apiService;
