import { AxiosInstance, AxiosResponse } from "axios";
import { User, AuthResponse, Workspace, UpdateWorkspaceRequest, Document, UploadResponse, DocumentsListResponse, ChatSession, ChatMessage, ChatResponse, HealthResponse } from "./types";
export declare abstract class BaseApiClient {
    protected client: AxiosInstance;
    protected token: string | null;
    constructor(baseURL: string, timeout?: number);
    protected setupInterceptors(): void;
    protected abstract handleAuthError(): void;
    protected setToken(token: string): void;
    protected clearToken(): void;
    protected handleResponse<T>(response: Promise<AxiosResponse>): Promise<T>;
    register(email: string, password: string, fullName?: string): Promise<AuthResponse>;
    login(email: string, password: string): Promise<AuthResponse>;
    logout(): Promise<{
        message: string;
    }>;
    getProfile(): Promise<{
        user: User;
    }>;
    listWorkspaces(): Promise<{
        workspaces: Workspace[];
    }>;
    createWorkspace(name: string, description?: string, ragConfig?: any): Promise<{
        workspace: Workspace;
    }>;
    getWorkspace(workspaceId: number): Promise<{
        workspace: Workspace;
    }>;
    updateWorkspace(workspaceId: number, updates: UpdateWorkspaceRequest): Promise<{
        workspace: Workspace;
    }>;
    deleteWorkspace(workspaceId: number): Promise<{
        message: string;
    }>;
    listDocuments(workspaceId: number): Promise<DocumentsListResponse>;
    uploadDocument(workspaceId: number, file: File | Buffer, filename: string, mimeType?: string): Promise<UploadResponse>;
    getDocumentStatus(workspaceId: number, documentId: string): Promise<{
        document: Document;
    }>;
    deleteDocument(workspaceId: number, documentId: string): Promise<{
        message: string;
    }>;
    listSessions(workspaceId: number): Promise<{
        sessions: ChatSession[];
        count: number;
    }>;
    createSession(workspaceId: number, title: string): Promise<{
        session: ChatSession;
    }>;
    getMessages(sessionId: string): Promise<{
        messages: ChatMessage[];
        count: number;
    }>;
    sendMessage(sessionId: string, content: string, ragMode?: "vector" | "graph" | "hybrid"): Promise<ChatResponse>;
    deleteSession(sessionId: string): Promise<{
        message: string;
    }>;
    health(): Promise<HealthResponse>;
}
