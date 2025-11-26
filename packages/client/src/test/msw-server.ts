import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:5000';

export const server = setupServer(
    http.get(`${API_BASE_URL}/health`, () => {
        return HttpResponse.json({ status: 'ok' });
    }),

    http.get(`${API_BASE_URL}/api/workspaces`, () => {
        return HttpResponse.json([]);
    }),

    http.get(`${API_BASE_URL}/api/workspaces/:id`, ({ params }) => {
        return HttpResponse.json({ id: Number(params.id), name: 'Test Workspace' });
    }),

    http.post(`${API_BASE_URL}/api/workspaces`, () => {
        return HttpResponse.json({ id: 2, name: 'New Workspace' });
    }),

    http.patch(`${API_BASE_URL}/api/workspaces/:id`, () => {
        return HttpResponse.json({ id: 1, name: 'Updated Workspace' });
    }),

    http.delete(`${API_BASE_URL}/api/workspaces/:id`, () => {
        return HttpResponse.json({ message: 'Workspace deleted successfully' });
    }),

    http.get(`${API_BASE_URL}/api/workspaces/:id/rag-config`, () => {
        return HttpResponse.json({ embedding_model: 'nomic-embed-text' });
    }),

    http.post(`${API_BASE_URL}/api/workspaces/:id/rag-config`, () => {
        return HttpResponse.json({ embedding_model: 'openai' });
    }),

    http.patch(`${API_BASE_URL}/api/workspaces/:id/rag-config`, () => {
        return HttpResponse.json({ chunk_size: 1500 });
    }),

    http.post(`${API_BASE_URL}/api/auth/signup`, () => {
        return HttpResponse.json({ access_token: 'mock-token' });
    }),

    http.post(`${API_BASE_URL}/api/auth/login`, () => {
        return HttpResponse.json({ access_token: 'mock-token' });
    }),

    http.post(`${API_BASE_URL}/api/auth/logout`, () => {
        return HttpResponse.json({ message: 'Logged out successfully' });
    }),

    http.get(`${API_BASE_URL}/api/auth/me`, () => {
        return HttpResponse.json({ username: 'testuser', theme_preference: 'dark' });
    }),

    http.patch(`${API_BASE_URL}/api/auth/preferences`, () => {
        return HttpResponse.json({ theme_preference: 'light' });
    }),

    http.get(`${API_BASE_URL}/api/workspaces/1/documents`, () => {
        return HttpResponse.json({ documents: [], count: 0 });
    }),

    http.delete(`${API_BASE_URL}/api/workspaces/1/documents/1`, () => {
        return HttpResponse.json({ message: 'Document deleted' });
    }),

    http.post(`${API_BASE_URL}/api/workspaces/1/chat/sessions/123/messages`, () => {
        return HttpResponse.json({ message_id: 'msg-123' });
    }),

    http.post(`${API_BASE_URL}/api/workspaces/1/chat/sessions/1/cancel`, () => {
        return HttpResponse.json({ message: 'Message cancelled' });
    }),

    http.post(`${API_BASE_URL}/api/workspaces/1/chat/sessions`, () => {
        return HttpResponse.json({ session_id: 123, title: 'New Chat' });
    }),

    http.get(`${API_BASE_URL}/api/workspaces/1/chat/sessions`, () => {
        return HttpResponse.json([]);
    }),

    http.delete(`${API_BASE_URL}/api/workspaces/1/chat/sessions/123`, () => {
        return HttpResponse.json({ message: 'Session deleted' });
    }),

    http.post(`${API_BASE_URL}/api/workspaces/1/documents/fetch-wikipedia`, () => {
        return HttpResponse.json({
            message: 'Wikipedia article fetched successfully',
        });
    }),

    http.patch(`${API_BASE_URL}/api/auth/profile`, () => {
        return HttpResponse.json({
            id: 1,
            username: 'testuser',
            email: 'newemail@example.com',
            full_name: 'Updated Name',
            created_at: '2024-01-01T00:00:00Z',
        });
    }),

    http.post(`${API_BASE_URL}/api/auth/change-password`, () => {
        return new HttpResponse(null, { status: 200 });
    }),

    http.get(`${API_BASE_URL}/api/auth/default-rag-config`, () => {
        return HttpResponse.json({
            embedding_model: 'nomic-embed-text',
            retriever_type: 'vector',
            chunk_size: 1000,
            chunk_overlap: 200,
            top_k: 5,
        });
    }),

    http.put(`${API_BASE_URL}/api/auth/default-rag-config`, () => {
        return HttpResponse.json({
            embedding_model: 'nomic-embed-text',
            retriever_type: 'vector',
            chunk_size: 1000,
            chunk_overlap: 200,
            top_k: 5,
        });
    })
);
