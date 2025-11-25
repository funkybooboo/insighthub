"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.getConfigPath = getConfigPath;
exports.loadConfig = loadConfig;
exports.saveConfig = saveConfig;
exports.getConfig = getConfig;
exports.resetConfig = resetConfig;
const fs = __importStar(require("fs-extra"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const defaultConfig = {
    api: {
        url: "http://localhost:5000",
        timeout: 30000,
        retries: 3,
    },
    workspace: {
        autoCreate: false,
    },
    output: {
        format: "table",
        color: true,
    },
    chat: {
        streaming: true,
        showSources: true,
        saveHistory: true,
    },
    upload: {
        chunkSize: "10MB",
        parallel: 3,
        autoProcess: true,
    },
};
let currentConfig = { ...defaultConfig };
function getConfigPath() {
    return path.join(os.homedir(), ".insighthub", "config.json");
}
function loadConfig(cliOptions) {
    // Load environment variables
    // Note: In Node.js environments, dotenv would be handled by the consuming package
    // Load config file
    const configPath = getConfigPath();
    if (fs.existsSync(configPath)) {
        try {
            const fileConfig = fs.readJsonSync(configPath);
            currentConfig = { ...defaultConfig, ...fileConfig };
        }
        catch (error) {
            console.warn(`Warning: Could not load config file at ${configPath}`);
        }
    }
    // Override with CLI options
    if (cliOptions) {
        if (cliOptions.apiUrl)
            currentConfig.api.url = cliOptions.apiUrl;
        if (cliOptions.workspace)
            currentConfig.workspace.default = cliOptions.workspace;
        if (cliOptions.noColor !== undefined)
            currentConfig.output.color = !cliOptions.noColor;
    }
    // Override with environment variables
    if (process.env.INSIGHTHUB_API_URL)
        currentConfig.api.url = process.env.INSIGHTHUB_API_URL;
    if (process.env.INSIGHTHUB_DEFAULT_WORKSPACE)
        currentConfig.workspace.default = process.env.INSIGHTHUB_DEFAULT_WORKSPACE;
    if (process.env.INSIGHTHUB_OUTPUT_FORMAT)
        currentConfig.output.format = process.env.INSIGHTHUB_OUTPUT_FORMAT;
    if (process.env.INSIGHTHUB_NO_COLOR)
        currentConfig.output.color = false;
    return currentConfig;
}
function saveConfig(config) {
    const configPath = getConfigPath();
    const configDir = path.dirname(configPath);
    fs.ensureDirSync(configDir);
    const existingConfig = fs.existsSync(configPath)
        ? fs.readJsonSync(configPath)
        : {};
    const newConfig = { ...existingConfig, ...config };
    fs.writeJsonSync(configPath, newConfig, { spaces: 2 });
}
function getConfig() {
    return currentConfig;
}
function resetConfig() {
    currentConfig = { ...defaultConfig };
    const configPath = getConfigPath();
    if (fs.existsSync(configPath)) {
        fs.removeSync(configPath);
    }
}
