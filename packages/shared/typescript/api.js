import axios from "axios";
export class BaseApiClient {
    constructor(baseURL, timeout = 30000) {
        this.token = null;
        this.client = axios.create({
            baseURL,
            timeout,
            headers: {
                "Content-Type": "application/json",
            },
        });
        this.setupInterceptors();
    }
    setupInterceptors() {
        // Request interceptor to add auth token
        this.client.interceptors.request.use((config) => {
            if (this.token) {
                config.headers.Authorization = `Bearer ${this.token}`;
            }
            return config;
        }, (error) => Promise.reject(error));
        // Response interceptor for error handling
        this.client.interceptors.response.use((response) => response, (error) => {
            if (error.response?.status === 401) {
                this.clearToken();
                this.handleAuthError();
            }
            return Promise.reject(error);
        });
    }
    setToken(token) {
        this.token = token;
    }
    clearToken() {
        this.token = null;
    }
    async handleResponse(response) {
        try {
            const result = await response;
            return result.data;
        }
        catch (error) {
            if (error.response) {
                const status = error.response.status;
                const message = error.response.data?.error ||
                    error.response.data?.message ||
                    error.message;
                if (status === 401) {
                    this.clearToken();
                    throw new Error("Authentication failed. Please login again.");
                }
                throw new Error(`${status}: ${message}`);
            }
            else if (error.code === "ECONNREFUSED") {
                throw new Error(`Cannot connect to InsightHub server at ${this.client.defaults.baseURL}. Is the server running?`);
            }
            else {
                throw new Error(`Request failed: ${error.message}`);
            }
        }
    }
    // ===== AUTHENTICATION METHODS =====
    async register(email, password, fullName) {
        const response = await this.handleResponse(this.client.post("/api/auth/register", {
            email,
            password,
            full_name: fullName,
        }));
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        return response;
    }
    async login(email, password) {
        const response = await this.handleResponse(this.client.post("/api/auth/login", {
            email,
            password,
        }));
        if (response.access_token) {
            this.setToken(response.access_token);
        }
        return response;
    }
    async logout() {
        const response = await this.handleResponse(this.client.post("/api/auth/logout", {}));
        this.clearToken();
        return response;
    }
    async getProfile() {
        return this.handleResponse(this.client.get("/api/auth/me"));
    }
    // ===== WORKSPACE METHODS =====
    async listWorkspaces() {
        return this.handleResponse(this.client.get("/api/workspaces"));
    }
    async createWorkspace(name, description, ragConfig) {
        return this.handleResponse(this.client.post("/api/workspaces", {
            name,
            description,
            rag_config: ragConfig,
        }));
    }
    async getWorkspace(workspaceId) {
        return this.handleResponse(this.client.get(`/api/workspaces/${workspaceId}`));
    }
    async updateWorkspace(workspaceId, updates) {
        return this.handleResponse(this.client.put(`/api/workspaces/${workspaceId}`, updates));
    }
    async deleteWorkspace(workspaceId) {
        return this.handleResponse(this.client.delete(`/api/workspaces/${workspaceId}`));
    }
    // ===== DOCUMENT METHODS =====
    async listDocuments(workspaceId) {
        return this.handleResponse(this.client.get(`/api/workspaces/${workspaceId}/documents`));
    }
    async uploadDocument(workspaceId, file, filename, mimeType) {
        const formData = new FormData();
        if (file instanceof File) {
            formData.append("file", file);
        }
        else {
            // For Node.js Buffer
            const blob = new Blob([file], {
                type: mimeType || "application/octet-stream",
            });
            formData.append("file", blob, filename);
        }
        const response = await this.handleResponse(this.client.post(`/api/workspaces/${workspaceId}/documents`, formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }));
        return response;
    }
    async getDocumentStatus(workspaceId, documentId) {
        return this.handleResponse(this.client.get(`/api/workspaces/${workspaceId}/documents/${documentId}/status`));
    }
    async deleteDocument(workspaceId, documentId) {
        return this.handleResponse(this.client.delete(`/api/workspaces/${workspaceId}/documents/${documentId}`));
    }
    // ===== CHAT METHODS =====
    async listSessions(workspaceId) {
        return this.handleResponse(this.client.get(`/api/workspaces/${workspaceId}/sessions`));
    }
    async createSession(workspaceId, title) {
        return this.handleResponse(this.client.post(`/api/workspaces/${workspaceId}/sessions`, { title }));
    }
    async getMessages(sessionId) {
        return this.handleResponse(this.client.get(`/api/sessions/${sessionId}/messages`));
    }
    async sendMessage(sessionId, content, ragMode) {
        return this.handleResponse(this.client.post(`/api/sessions/${sessionId}/messages`, {
            content,
            rag_mode: ragMode,
        }));
    }
    async deleteSession(sessionId) {
        return this.handleResponse(this.client.delete(`/api/sessions/${sessionId}`));
    }
    // ===== HEALTH CHECK =====
    async health() {
        return this.handleResponse(this.client.get("/health"));
    }
}
