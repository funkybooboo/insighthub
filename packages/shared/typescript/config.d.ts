import { CliConfig } from "./types";
export declare function getConfigPath(): string;
export declare function loadConfig(cliOptions?: any): CliConfig;
export declare function saveConfig(config: Partial<CliConfig>): void;
export declare function getConfig(): CliConfig;
export declare function resetConfig(): void;
