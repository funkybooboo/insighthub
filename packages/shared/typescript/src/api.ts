import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  User,
  AuthResponse,
  LoginRequest,
  SignupRequest,
  Workspace,
  CreateWorkspaceRequest,
  UpdateWorkspaceRequest,
  Document,
  UploadResponse,
  DocumentsListResponse,
  ChatSession,
  ChatMessage,
  ChatRequest,
  ChatResponse,
  HealthResponse,
} from './types';

export abstract class BaseApiClient {
  protected client: AxiosInstance;
  protected token: string | null = null;

  constructor(baseURL: string, timeout: number = 30000) {
    this.client = axios.create({
      baseURL,
      timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  protected setupInterceptors(): void {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.clearToken();
          this.handleAuthError();
        }
        return Promise.reject(error);
      }
    );
  }

  protected abstract handleAuthError(): void;

  protected setToken(token: string): void {
    this.token = token;
  }

  protected clearToken(): void {
    this.token = null;
  }

  protected async handleResponse<T>(response: Promise<AxiosResponse>): Promise<T> {
    try {
      const result = await response;
      return result.data as T;
    } catch (error: any) {
      if (error.response) {
        const status = error.response.status;
        const message = error.response.data?.error || error.response.data?.message || error.message;

        if (status === 401) {
          this.clearToken();
          throw new Error('Authentication failed. Please login again.');
        }

        throw new Error(`${status}: ${message}`);
      } else if (error.code === 'ECONNREFUSED') {
        throw new Error(`Cannot connect to InsightHub server at ${this.client.defaults.baseURL}. Is the server running?`);
      } else {
        throw new Error(`Request failed: ${error.message}`);
      }
    }
  }

  // ===== AUTHENTICATION METHODS =====

  async register(email: string, password: string, fullName?: string): Promise<AuthResponse> {
    const response = await this.handleResponse<AuthResponse>(
      this.client.post('/api/auth/register', {
        email,
        password,
        full_name: fullName,
      })
    );

    if (response.access_token) {
      this.setToken(response.access_token);
    }

    return response;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.handleResponse<AuthResponse>(
      this.client.post('/api/auth/login', {
        email,
        password,
      })
    );

    if (response.access_token) {
      this.setToken(response.access_token);
    }

    return response;
  }

  async logout(): Promise<{ message: string }> {
    const response = await this.handleResponse<{ message: string }>(
      this.client.post('/api/auth/logout', {})
    );

    this.clearToken();
    return response;
  }

  async getProfile(): Promise<{ user: User }> {
    return this.handleResponse<{ user: User }>(
      this.client.get('/api/auth/me')
    );
  }

  // ===== WORKSPACE METHODS =====

  async listWorkspaces(): Promise<{ workspaces: Workspace[] }> {
    return this.handleResponse<{ workspaces: Workspace[] }>(
      this.client.get('/api/workspaces')
    );
  }

  async createWorkspace(name: string, description?: string, ragConfig?: any): Promise<{ workspace: Workspace }> {
    return this.handleResponse<{ workspace: Workspace }>(
      this.client.post('/api/workspaces', {
        name,
        description,
        rag_config: ragConfig,
      })
    );
  }

  async getWorkspace(workspaceId: number): Promise<{ workspace: Workspace }> {
    return this.handleResponse<{ workspace: Workspace }>(
      this.client.get(`/api/workspaces/${workspaceId}`)
    );
  }

  async updateWorkspace(workspaceId: number, updates: UpdateWorkspaceRequest): Promise<{ workspace: Workspace }> {
    return this.handleResponse<{ workspace: Workspace }>(
      this.client.put(`/api/workspaces/${workspaceId}`, updates)
    );
  }

  async deleteWorkspace(workspaceId: number): Promise<{ message: string }> {
    return this.handleResponse<{ message: string }>(
      this.client.delete(`/api/workspaces/${workspaceId}`)
    );
  }

  // ===== DOCUMENT METHODS =====

  async listDocuments(workspaceId: number): Promise<DocumentsListResponse> {
    return this.handleResponse<DocumentsListResponse>(
      this.client.get(`/api/workspaces/${workspaceId}/documents`)
    );
  }

  async uploadDocument(workspaceId: number, file: File | Buffer, filename: string, mimeType?: string): Promise<UploadResponse> {
    const formData = new FormData();

    if (file instanceof File) {
      formData.append('file', file);
    } else {
      // For Node.js Buffer
      const blob = new Blob([file], { type: mimeType || 'application/octet-stream' });
      formData.append('file', blob, filename);
    }

    const response = await this.handleResponse<UploadResponse>(
      this.client.post(`/api/workspaces/${workspaceId}/documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    );

    return response;
  }

  async getDocumentStatus(workspaceId: number, documentId: string): Promise<{ document: Document }> {
    return this.handleResponse<{ document: Document }>(
      this.client.get(`/api/workspaces/${workspaceId}/documents/${documentId}/status`)
    );
  }

  async deleteDocument(workspaceId: number, documentId: string): Promise<{ message: string }> {
    return this.handleResponse<{ message: string }>(
      this.client.delete(`/api/workspaces/${workspaceId}/documents/${documentId}`)
    );
  }

  // ===== CHAT METHODS =====

  async listSessions(workspaceId: number): Promise<{ sessions: ChatSession[]; count: number }> {
    return this.handleResponse<{ sessions: ChatSession[]; count: number }>(
      this.client.get(`/api/workspaces/${workspaceId}/sessions`)
    );
  }

  async createSession(workspaceId: number, title: string): Promise<{ session: ChatSession }> {
    return this.handleResponse<{ session: ChatSession }>(
      this.client.post(`/api/workspaces/${workspaceId}/sessions`, { title })
    );
  }

  async getMessages(sessionId: string): Promise<{ messages: ChatMessage[]; count: number }> {
    return this.handleResponse<{ messages: ChatMessage[]; count: number }>(
      this.client.get(`/api/sessions/${sessionId}/messages`)
    );
  }

  async sendMessage(sessionId: string, content: string, ragMode?: 'vector' | 'graph' | 'hybrid'): Promise<ChatResponse> {
    return this.handleResponse<ChatResponse>(
      this.client.post(`/api/sessions/${sessionId}/messages`, {
        content,
        rag_mode: ragMode,
      })
    );
  }

  async deleteSession(sessionId: string): Promise<{ message: string }> {
    return this.handleResponse<{ message: string }>(
      this.client.delete(`/api/sessions/${sessionId}`)
    );
  }

  // ===== HEALTH CHECK =====

  async health(): Promise<HealthResponse> {
    return this.handleResponse<HealthResponse>(
      this.client.get('/health')
    );
  }
}