"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const bun_test_1 = require("bun:test");
const config_1 = require("../../src/config");
(0, bun_test_1.describe)("Configuration Integration Tests", () => {
    // Store original environment
    const originalEnv = { ...process.env };
    (0, bun_test_1.beforeEach)(() => {
        // Reset config state
        (0, config_1.resetConfig)();
        // Clear test environment variables
        delete process.env.INSIGHTHUB_API_URL;
        delete process.env.INSIGHTHUB_DEFAULT_WORKSPACE;
        delete process.env.INSIGHTHUB_OUTPUT_FORMAT;
        delete process.env.INSIGHTHUB_NO_COLOR;
    });
    (0, bun_test_1.afterEach)(() => {
        // Restore original environment
        process.env = { ...originalEnv };
        // Reset config state
        (0, config_1.resetConfig)();
    });
    (0, bun_test_1.describe)("Configuration Loading", () => {
        (0, bun_test_1.it)("should load default configuration", () => {
            const config = (0, config_1.loadConfig)();
            (0, bun_test_1.expect)(config.api.url).toBe("http://localhost:5000");
            (0, bun_test_1.expect)(config.api.timeout).toBe(30000);
            (0, bun_test_1.expect)(config.workspace.autoCreate).toBe(false);
            (0, bun_test_1.expect)(config.output.format).toBe("table");
            (0, bun_test_1.expect)(config.output.color).toBe(true);
        });
        (0, bun_test_1.it)("should merge CLI options with defaults", () => {
            const cliOptions = {
                apiUrl: "http://cli-option:7000",
                workspace: "cli-workspace",
                noColor: true,
            };
            const config = (0, config_1.loadConfig)(cliOptions);
            (0, bun_test_1.expect)(config.api.url).toBe("http://cli-option:7000");
            (0, bun_test_1.expect)(config.workspace.default).toBe("cli-workspace");
            (0, bun_test_1.expect)(config.output.color).toBe(false);
            // Other defaults should remain
            (0, bun_test_1.expect)(config.api.timeout).toBe(30000);
        });
    });
    (0, bun_test_1.describe)("Environment Variable Integration", () => {
        (0, bun_test_1.it)("should load environment variables when set before first load", () => {
            // Set env vars before loading
            process.env.INSIGHTHUB_API_URL = "http://env-test:8080";
            process.env.INSIGHTHUB_NO_COLOR = "true";
            // Reset to force reload
            (0, config_1.resetConfig)();
            const config = (0, config_1.loadConfig)();
            (0, bun_test_1.expect)(config.api.url).toBe("http://env-test:8080");
            (0, bun_test_1.expect)(config.output.color).toBe(false);
        });
    });
    (0, bun_test_1.describe)("CLI Options Integration", () => {
        (0, bun_test_1.it)("should apply CLI options", () => {
            const cliOptions = {
                apiUrl: "http://cli-test:9000",
                noColor: true,
            };
            const config = (0, config_1.loadConfig)(cliOptions);
            (0, bun_test_1.expect)(config.api.url).toBe("http://cli-test:9000");
            (0, bun_test_1.expect)(config.output.color).toBe(false);
        });
        (0, bun_test_1.it)("should apply CLI options on each call", () => {
            const cliOptions = {
                apiUrl: "http://cli:6000",
            };
            const config = (0, config_1.loadConfig)(cliOptions);
            (0, bun_test_1.expect)(config.api.url).toBe("http://cli:6000");
        });
    });
    (0, bun_test_1.describe)("Configuration State", () => {
        (0, bun_test_1.it)("should provide access to current config", () => {
            const config = (0, config_1.loadConfig)();
            const current = (0, config_1.getConfig)();
            (0, bun_test_1.expect)(current).toBe(config);
        });
        (0, bun_test_1.it)("should allow config reset", () => {
            // Test that reset function exists and can be called
            (0, bun_test_1.expect)(() => (0, config_1.resetConfig)()).not.toThrow();
        });
    });
    (0, bun_test_1.describe)("Config Path", () => {
        (0, bun_test_1.it)("should return valid config path", () => {
            const configPath = (0, config_1.getConfigPath)();
            (0, bun_test_1.expect)(typeof configPath).toBe("string");
            (0, bun_test_1.expect)(configPath.length).toBeGreaterThan(0);
            (0, bun_test_1.expect)(configPath).toContain("config.json");
        });
    });
});
