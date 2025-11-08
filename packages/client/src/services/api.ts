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

class ApiService {
    private client: AxiosInstance;

    constructor(baseURL: string = API_BASE_URL) {
        this.client = axios.create({
            baseURL,
            headers: {
                'Content-Type': 'application/json',
            },
        });
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
}

export const apiService = new ApiService();
export default apiService;
