import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import express, { Request, Response } from "express";
import { Server } from "http";
import { BaseApiClient } from "../../src/api";
import { AuthResponse, User, HealthResponse } from "../../src/types";

// Concrete implementation for testing
class TestApiClient extends BaseApiClient {
  handleAuthError(): void {
    // Test implementation - could emit events or call callbacks
  }

  // Expose protected client for testing
  getClient() {
    return this.client;
  }
}

describe("BaseApiClient Integration Tests", () => {
  let server: Server;
  let client: TestApiClient;
  let app: express.Express;

  beforeEach(() => {
    app = express();
    app.use(express.json());

    // Mock auth endpoints
    app.post("/api/auth/register", (req: Request, res: Response) => {
      const { email, password, full_name } = req.body;
      if (!email || !password) {
        return res.status(400).json({ error: "Email and password required" });
      }

      const response: AuthResponse = {
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

    app.post("/api/auth/login", (req: Request, res: Response) => {
      const { email, password } = req.body;
      if (email === "invalid@example.com") {
        return res.status(401).json({ error: "Invalid credentials" });
      }

      const response: AuthResponse = {
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

    app.post("/api/auth/logout", (req: Request, res: Response) => {
      res.json({ message: "Logged out successfully" });
    });

    app.get("/api/auth/me", (req: Request, res: Response) => {
      const authHeader = req.headers.authorization;
      if (!authHeader || !authHeader.startsWith("Bearer ")) {
        return res.status(401).json({ error: "Unauthorized" });
      }

      const user: User = {
        id: 1,
        email: "test@example.com",
        full_name: "Test User",
        created_at: new Date().toISOString(),
      };
      res.json({ user });
    });

    // Health endpoint
    app.get("/health", (req: Request, res: Response) => {
      const response: HealthResponse = {
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
    app.get("/api/workspaces", (req: Request, res: Response) => {
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

    app.post("/api/workspaces", (req: Request, res: Response) => {
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
    const port = (server.address() as any).port;
    client = new TestApiClient(`http://localhost:${port}`);
  });

  afterEach(() => {
    server.close();
  });

  describe("Authentication Flow", () => {
    it("should register a new user and set auth token", async () => {
      const result = await client.register(
        "newuser@example.com",
        "password123",
        "New User",
      );

      expect(result).toEqual({
        access_token: "test-token-123",
        token_type: "bearer",
        user: expect.objectContaining({
          id: 1,
          email: "newuser@example.com",
          full_name: "New User",
        }),
      });

      // Verify token was set internally
      expect((client as any).token).toBe("test-token-123");
    });

    it("should login existing user and set auth token", async () => {
      const result = await client.login("user@example.com", "password123");

      expect(result).toEqual({
        access_token: "test-token-456",
        token_type: "bearer",
        user: expect.objectContaining({
          id: 2,
          email: "user@example.com",
          full_name: "Logged In User",
        }),
      });

      expect((client as any).token).toBe("test-token-456");
    });

    it("should handle login failure", async () => {
      await expect(
        client.login("invalid@example.com", "wrongpassword"),
      ).rejects.toThrow("Authentication failed. Please login again.");
    });

    it("should get user profile with valid token", async () => {
      // First login to get token
      await client.login("user@example.com", "password123");

      const result = await client.getProfile();

      expect(result.user).toEqual(
        expect.objectContaining({
          id: 1,
          email: "test@example.com",
          full_name: "Test User",
        }),
      );
    });

    it("should handle unauthorized profile request", async () => {
      await expect(client.getProfile()).rejects.toThrow(
        "Authentication failed. Please login again.",
      );
    });

    it("should get user profile with valid token", async () => {
      // First login to get token
      await client.login("user@example.com", "password123");

      const result = await client.getProfile();

      expect(result.user).toEqual(
        expect.objectContaining({
          id: 1,
          email: "test@example.com",
          full_name: "Test User",
        }),
      );
    });

    it("should handle unauthorized profile request", async () => {
      await expect(client.getProfile()).rejects.toThrow(
        "Authentication failed. Please login again.",
      );
    });

    it("should logout and clear token", async () => {
      // First login
      await client.login("user@example.com", "password123");
      expect((client as any).token).toBe("test-token-456");

      // Then logout
      const result = await client.logout();
      expect(result).toEqual({ message: "Logged out successfully" });
      expect((client as any).token).toBeNull();
    });
  });

  describe("Workspace Operations", () => {
    beforeEach(async () => {
      // Login first for authenticated requests
      await client.login("user@example.com", "password123");
    });

    it("should list workspaces", async () => {
      const result = await client.listWorkspaces();

      expect(result.workspaces).toHaveLength(1);
      expect(result.workspaces[0]).toEqual(
        expect.objectContaining({
          id: 1,
          name: "Test Workspace",
          status: "ready",
        }),
      );
    });

    it("should create a new workspace", async () => {
      const result = await client.createWorkspace(
        "New Workspace",
        "Description of new workspace",
      );

      expect(result.workspace).toEqual(
        expect.objectContaining({
          name: "New Workspace",
          description: "Description of new workspace",
          status: "provisioning",
        }),
      );
      expect(result.workspace.id).toBeDefined();
    });

    it("should handle unauthorized workspace operations", async () => {
      // Clear token to simulate unauthorized request
      (client as any).token = null;

      await expect(client.listWorkspaces()).rejects.toThrow(
        "Authentication failed. Please login again.",
      );
    });
  });

  describe("Health Check", () => {
    it("should return health status", async () => {
      const result = await client.health();

      expect(result).toEqual({
        status: "healthy",
        version: "1.0.0",
        services: {
          database: "connected",
          redis: "connected",
        },
      });
    });
  });

  describe("Error Handling", () => {
    it("should handle connection refused", async () => {
      const badClient = new TestApiClient("http://localhost:9999"); // Non-existent port

      await expect(badClient.health()).rejects.toThrow(
        "Cannot connect to InsightHub server at http://localhost:9999. Is the server running?",
      );
    });

    // Note: Axios doesn't throw on invalid JSON by default, so this test is omitted
  });

  describe("Request Configuration", () => {
    it("should use custom timeout", async () => {
      const customClient = new TestApiClient("http://localhost:3000", 5000);
      expect(customClient.getClient().defaults.timeout).toBe(5000);
    });

    it("should set proper headers", () => {
      expect(client.getClient().defaults.headers["Content-Type"]).toBe(
        "application/json",
      );
    });
  });
});
