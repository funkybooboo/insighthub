import * as fs from 'fs-extra';
import * as path from 'path';
import * as os from 'os';
import { CliConfig } from './types';

const defaultConfig: CliConfig = {
  api: {
    url: 'http://localhost:5000',
    timeout: 30000,
    retries: 3,
  },
  workspace: {
    autoCreate: false,
  },
  output: {
    format: 'table',
    color: true,
  },
  chat: {
    streaming: true,
    showSources: true,
    saveHistory: true,
  },
  upload: {
    chunkSize: '10MB',
    parallel: 3,
    autoProcess: true,
  },
};

let currentConfig: CliConfig = { ...defaultConfig };

export function getConfigPath(): string {
  return path.join(os.homedir(), '.insighthub', 'config.json');
}

export function loadConfig(cliOptions?: any): CliConfig {
  // Load environment variables
  // Note: In Node.js environments, dotenv would be handled by the consuming package

  // Load config file
  const configPath = getConfigPath();
  if (fs.existsSync(configPath)) {
    try {
      const fileConfig = fs.readJsonSync(configPath);
      currentConfig = { ...defaultConfig, ...fileConfig };
    } catch (error) {
      console.warn(`Warning: Could not load config file at ${configPath}`);
    }
  }

  // Override with CLI options
  if (cliOptions) {
    if (cliOptions.apiUrl) currentConfig.api.url = cliOptions.apiUrl;
    if (cliOptions.workspace) currentConfig.workspace.default = cliOptions.workspace;
    if (cliOptions.noColor !== undefined) currentConfig.output.color = !cliOptions.noColor;
  }

  // Override with environment variables
  if (process.env.INSIGHTHUB_API_URL) currentConfig.api.url = process.env.INSIGHTHUB_API_URL;
  if (process.env.INSIGHTHUB_DEFAULT_WORKSPACE) currentConfig.workspace.default = process.env.INSIGHTHUB_DEFAULT_WORKSPACE;
  if (process.env.INSIGHTHUB_OUTPUT_FORMAT) currentConfig.output.format = process.env.INSIGHTHUB_OUTPUT_FORMAT as any;
  if (process.env.INSIGHTHUB_NO_COLOR) currentConfig.output.color = false;

  return currentConfig;
}

export function saveConfig(config: Partial<CliConfig>): void {
  const configPath = getConfigPath();
  const configDir = path.dirname(configPath);

  fs.ensureDirSync(configDir);

  const existingConfig = fs.existsSync(configPath) ? fs.readJsonSync(configPath) : {};
  const newConfig = { ...existingConfig, ...config };

  fs.writeJsonSync(configPath, newConfig, { spaces: 2 });
}

export function getConfig(): CliConfig {
  return currentConfig;
}

export function resetConfig(): void {
  currentConfig = { ...defaultConfig };
  const configPath = getConfigPath();
  if (fs.existsSync(configPath)) {
    fs.removeSync(configPath);
  }
}