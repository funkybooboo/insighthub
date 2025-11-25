"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const bun_test_1 = require("bun:test");
const express_1 = __importDefault(require("express"));
const api_1 = require("../../src/api");
// Concrete implementation for testing
class TestApiClient extends api_1.BaseApiClient {
    handleAuthError() {
        // Test implementation - could emit events or call callbacks
    }
    // Expose protected client for testing
    getClient() {
        return this.client;
    }
}
(0, bun_test_1.describe)("BaseApiClient Integration Tests", () => {
    let server;
    let client;
    let app;
    (0, bun_test_1.beforeEach)(() => {
        app = (0, express_1.default)();
        app.use(express_1.default.json());
        // Mock auth endpoints
        app.post("/api/auth/register", (req, res) => {
            const { email, password, full_name } = req.body;
            if (!email || !password) {
                return res.status(400).json({ error: "Email and password required" });
            }
            const response = {
                access_token: "test-token-123",
                token_type: "bearer",
                user: {
                    id: 1,
                    email,
                    full_name: full_name || "Test User",
                    created_at: new Date().toISOString(),
                },
            };
            res.json(response);
        });
        app.post("/api/auth/login", (req, res) => {
            const { email, password } = req.body;
            if (email === "invalid@example.com") {
                return res.status(401).json({ error: "Invalid credentials" });
            }
            const response = {
                access_token: "test-token-456",
                token_type: "bearer",
                user: {
                    id: 2,
                    email,
                    full_name: "Logged In User",
                    created_at: new Date().toISOString(),
                },
            };
            res.json(response);
        });
        app.post("/api/auth/logout", (req, res) => {
            res.json({ message: "Logged out successfully" });
        });
        app.get("/api/auth/me", (req, res) => {
            const authHeader = req.headers.authorization;
            if (!authHeader || !authHeader.startsWith("Bearer ")) {
                return res.status(401).json({ error: "Unauthorized" });
            }
            const user = {
                id: 1,
                email: "test@example.com",
                full_name: "Test User",
                created_at: new Date().toISOString(),
            };
            res.json({ user });
        });
        // Health endpoint
        app.get("/health", (req, res) => {
            const response = {
                status: "healthy",
                version: "1.0.0",
                services: {
                    database: "connected",
                    redis: "connected",
                },
            };
            res.json(response);
        });
        // Mock workspace endpoints
        app.get("/api/workspaces", (req, res) => {
            const authHeader = req.headers.authorization;
            if (!authHeader) {
                return res.status(401).json({ error: "Unauthorized" });
            }
            res.json({
                workspaces: [
                    {
                        id: 1,
                        name: "Test Workspace",
                        description: "A test workspace",
                        status: "ready",
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                    },
                ],
            });
        });
        app.post("/api/workspaces", (req, res) => {
            const authHeader = req.headers.authorization;
            if (!authHeader) {
                return res.status(401).json({ error: "Unauthorized" });
            }
            const { name, description } = req.body;
            res.json({
                workspace: {
                    id: Date.now(),
                    name,
                    description,
                    status: "provisioning",
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString(),
                },
            });
        });
        server = app.listen(0); // Random available port
        const port = server.address().port;
        client = new TestApiClient(`http://localhost:${port}`);
    });
    (0, bun_test_1.afterEach)(() => {
        server.close();
    });
    (0, bun_test_1.describe)("Authentication Flow", () => {
        (0, bun_test_1.it)("should register a new user and set auth token", async () => {
            const result = await client.register("newuser@example.com", "password123", "New User");
            (0, bun_test_1.expect)(result).toEqual({
                access_token: "test-token-123",
                token_type: "bearer",
                user: bun_test_1.expect.objectContaining({
                    id: 1,
                    email: "newuser@example.com",
                    full_name: "New User",
                }),
            });
            // Verify token was set internally
            (0, bun_test_1.expect)(client.token).toBe("test-token-123");
        });
        (0, bun_test_1.it)("should login existing user and set auth token", async () => {
            const result = await client.login("user@example.com", "password123");
            (0, bun_test_1.expect)(result).toEqual({
                access_token: "test-token-456",
                token_type: "bearer",
                user: bun_test_1.expect.objectContaining({
                    id: 2,
                    email: "user@example.com",
                    full_name: "Logged In User",
                }),
            });
            (0, bun_test_1.expect)(client.token).toBe("test-token-456");
        });
        (0, bun_test_1.it)("should handle login failure", async () => {
            await (0, bun_test_1.expect)(client.login("invalid@example.com", "wrongpassword")).rejects.toThrow("Authentication failed. Please login again.");
        });
        (0, bun_test_1.it)("should get user profile with valid token", async () => {
            // First login to get token
            await client.login("user@example.com", "password123");
            const result = await client.getProfile();
            (0, bun_test_1.expect)(result.user).toEqual(bun_test_1.expect.objectContaining({
                id: 1,
                email: "test@example.com",
                full_name: "Test User",
            }));
        });
        (0, bun_test_1.it)("should handle unauthorized profile request", async () => {
            await (0, bun_test_1.expect)(client.getProfile()).rejects.toThrow("Authentication failed. Please login again.");
        });
        (0, bun_test_1.it)("should get user profile with valid token", async () => {
            // First login to get token
            await client.login("user@example.com", "password123");
            const result = await client.getProfile();
            (0, bun_test_1.expect)(result.user).toEqual(bun_test_1.expect.objectContaining({
                id: 1,
                email: "test@example.com",
                full_name: "Test User",
            }));
        });
        (0, bun_test_1.it)("should handle unauthorized profile request", async () => {
            await (0, bun_test_1.expect)(client.getProfile()).rejects.toThrow("Authentication failed. Please login again.");
        });
        (0, bun_test_1.it)("should logout and clear token", async () => {
            // First login
            await client.login("user@example.com", "password123");
            (0, bun_test_1.expect)(client.token).toBe("test-token-456");
            // Then logout
            const result = await client.logout();
            (0, bun_test_1.expect)(result).toEqual({ message: "Logged out successfully" });
            (0, bun_test_1.expect)(client.token).toBeNull();
        });
    });
    (0, bun_test_1.describe)("Workspace Operations", () => {
        (0, bun_test_1.beforeEach)(async () => {
            // Login first for authenticated requests
            await client.login("user@example.com", "password123");
        });
        (0, bun_test_1.it)("should list workspaces", async () => {
            const result = await client.listWorkspaces();
            (0, bun_test_1.expect)(result.workspaces).toHaveLength(1);
            (0, bun_test_1.expect)(result.workspaces[0]).toEqual(bun_test_1.expect.objectContaining({
                id: 1,
                name: "Test Workspace",
                status: "ready",
            }));
        });
        (0, bun_test_1.it)("should create a new workspace", async () => {
            const result = await client.createWorkspace("New Workspace", "Description of new workspace");
            (0, bun_test_1.expect)(result.workspace).toEqual(bun_test_1.expect.objectContaining({
                name: "New Workspace",
                description: "Description of new workspace",
                status: "provisioning",
            }));
            (0, bun_test_1.expect)(result.workspace.id).toBeDefined();
        });
        (0, bun_test_1.it)("should handle unauthorized workspace operations", async () => {
            // Clear token to simulate unauthorized request
            client.token = null;
            await (0, bun_test_1.expect)(client.listWorkspaces()).rejects.toThrow("Authentication failed. Please login again.");
        });
    });
    (0, bun_test_1.describe)("Health Check", () => {
        (0, bun_test_1.it)("should return health status", async () => {
            const result = await client.health();
            (0, bun_test_1.expect)(result).toEqual({
                status: "healthy",
                version: "1.0.0",
                services: {
                    database: "connected",
                    redis: "connected",
                },
            });
        });
    });
    (0, bun_test_1.describe)("Error Handling", () => {
        (0, bun_test_1.it)("should handle connection refused", async () => {
            const badClient = new TestApiClient("http://localhost:9999"); // Non-existent port
            await (0, bun_test_1.expect)(badClient.health()).rejects.toThrow("Cannot connect to InsightHub server at http://localhost:9999. Is the server running?");
        });
        // Note: Axios doesn't throw on invalid JSON by default, so this test is omitted
    });
    (0, bun_test_1.describe)("Request Configuration", () => {
        (0, bun_test_1.it)("should use custom timeout", async () => {
            const customClient = new TestApiClient("http://localhost:3000", 5000);
            (0, bun_test_1.expect)(customClient.getClient().defaults.timeout).toBe(5000);
        });
        (0, bun_test_1.it)("should set proper headers", () => {
            (0, bun_test_1.expect)(client.getClient().defaults.headers["Content-Type"]).toBe("application/json");
        });
    });
});
