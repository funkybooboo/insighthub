import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import {
  loadConfig,
  getConfig,
  resetConfig,
  getConfigPath,
} from "../../src/config";

describe("Configuration Integration Tests", () => {
  // Store original environment
  const originalEnv = { ...process.env };

  beforeEach(() => {
    // Clear test environment variables first
    delete process.env.INSIGHTHUB_API_URL;
    delete process.env.INSIGHTHUB_DEFAULT_WORKSPACE;
    delete process.env.INSIGHTHUB_OUTPUT_FORMAT;
    delete process.env.INSIGHTHUB_NO_COLOR;

    // Reset config state after clearing env vars
    resetConfig();
  });

  afterEach(() => {
    // Restore original environment
    process.env = { ...originalEnv };

    // Reset config state
    resetConfig();
  });

  describe("Configuration Loading", () => {
    it("should load configuration with expected structure", () => {
      resetConfig();
      const config = loadConfig();

      // Test that config has the expected structure and types
      expect(typeof config.api.url).toBe("string");
      expect(typeof config.api.timeout).toBe("number");
      expect(typeof config.workspace.autoCreate).toBe("boolean");
      expect(["table", "json", "yaml"]).toContain(config.output.format);
      expect(typeof config.output.color).toBe("boolean");
      expect(typeof config.api.retries).toBe("number");
    });

    it("should merge CLI options with defaults", () => {
      resetConfig();
      const cliOptions = {
        apiUrl: "http://cli-option:7000",
        workspace: "cli-workspace",
        noColor: true,
      };

      const config = loadConfig(cliOptions);

      expect(config.api.url).toBe("http://cli-option:7000");
      expect(config.workspace.default).toBe("cli-workspace");
      expect(config.output.color).toBe(false);
      // Other defaults should remain
      expect(config.api.timeout).toBe(30000);
    });
  });

  describe("Environment Variable Integration", () => {
    it("should load environment variables when set before first load", () => {
      resetConfig();
      // Set environment variables for this test
      process.env.INSIGHTHUB_API_URL = "http://env-test:8080";
      process.env.INSIGHTHUB_NO_COLOR = "true";

      const config = loadConfig();

      expect(config.api.url).toBe("http://env-test:8080");
      expect(config.output.color).toBe(false);
    });
  });

  describe("CLI Options Integration", () => {
    it("should apply CLI options", () => {
      resetConfig();
      const cliOptions = {
        apiUrl: "http://cli-test:9000",
        noColor: true,
      };

      const config = loadConfig(cliOptions);

      expect(config.api.url).toBe("http://cli-test:9000");
      expect(config.output.color).toBe(false);
    });

    it("should apply CLI options on each call", () => {
      resetConfig();
      const cliOptions = {
        apiUrl: "http://cli:6000",
      };

      const config = loadConfig(cliOptions);

      expect(config.api.url).toBe("http://cli:6000");
    });
  });

  describe("Configuration State", () => {
    it("should provide access to current config", () => {
      resetConfig();
      const config = loadConfig();
      const current = getConfig();

      expect(current).toBe(config);
    });

    it("should allow config reset", () => {
      // Test that reset function exists and can be called
      expect(() => resetConfig()).not.toThrow();
    });
  });

  describe("Config Path", () => {
    it("should return valid config path", () => {
      const configPath = getConfigPath();
      expect(typeof configPath).toBe("string");
      expect(configPath.length).toBeGreaterThan(0);
      expect(configPath).toContain("config.json");
    });
  });
});
