/**
 * Logging utility for the InsightHub client application.
 * Provides structured logging with configurable levels and environment-aware output.
 */

export const LogLevel = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3,
    NONE: 4,
} as const;

export type LogLevelType = typeof LogLevel[keyof typeof LogLevel];

interface LogEntry {
    level: LogLevelType;
    message: string;
    timestamp: string;
    context?: Record<string, unknown>;
    error?: Error;
}

class Logger {
    private currentLevel: LogLevelType;
    private isDevelopment: boolean;

    constructor() {
        this.isDevelopment = import.meta.env.DEV;
        // In development, show all logs; in production, only warnings and errors
        this.currentLevel = this.isDevelopment ? LogLevel.DEBUG : LogLevel.WARN;
    }

    private shouldLog(level: LogLevelType): boolean {
        return level >= this.currentLevel;
    }

    private formatMessage(entry: LogEntry): string {
        const levelName = Object.keys(LogLevel)[entry.level];
        const timestamp = entry.timestamp;
        let message = `[${timestamp}] ${levelName}: ${entry.message}`;

        if (entry.context) {
            message += ` | Context: ${JSON.stringify(entry.context)}`;
        }

        if (entry.error) {
            message += ` | Error: ${entry.error.message}`;
            if (entry.error.stack && this.isDevelopment) {
                message += `\n${entry.error.stack}`;
            }
        }

        return message;
    }

    private log(level: LogLevelType, message: string, context?: Record<string, unknown>, error?: Error): void {
        if (!this.shouldLog(level)) {
            return;
        }

        const entry: LogEntry = {
            level,
            message,
            timestamp: new Date().toISOString(),
            context,
            error,
        };

        const formattedMessage = this.formatMessage(entry);

        switch (level) {
            case LogLevel.DEBUG:
                console.debug(formattedMessage);
                break;
            case LogLevel.INFO:
                console.info(formattedMessage);
                break;
            case LogLevel.WARN:
                console.warn(formattedMessage);
                break;
            case LogLevel.ERROR:
                console.error(formattedMessage);
                break;
        }
    }

    /**
     * Log a debug message
     */
    debug(message: string, context?: Record<string, unknown>): void {
        this.log(LogLevel.DEBUG, message, context);
    }

    /**
     * Log an info message
     */
    info(message: string, context?: Record<string, unknown>): void {
        this.log(LogLevel.INFO, message, context);
    }

    /**
     * Log a warning message
     */
    warn(message: string, context?: Record<string, unknown>): void {
        this.log(LogLevel.WARN, message, context);
    }

    /**
     * Log an error message
     */
    error(message: string, error?: Error, context?: Record<string, unknown>): void {
        this.log(LogLevel.ERROR, message, context, error);
    }

    /**
     * Set the minimum log level
     */
    setLevel(level: LogLevelType): void {
        this.currentLevel = level;
    }

    /**
     * Get the current log level
     */
    getLevel(): LogLevelType {
        return this.currentLevel;
    }

    /**
     * Check if debug logging is enabled
     */
    isDebugEnabled(): boolean {
        return this.shouldLog(LogLevel.DEBUG);
    }

    /**
     * Check if info logging is enabled
     */
    isInfoEnabled(): boolean {
        return this.shouldLog(LogLevel.INFO);
    }

    /**
     * Check if warn logging is enabled
     */
    isWarnEnabled(): boolean {
        return this.shouldLog(LogLevel.WARN);
    }

    /**
     * Check if error logging is enabled
     */
    isErrorEnabled(): boolean {
        return this.shouldLog(LogLevel.ERROR);
    }
}

// Create and export a singleton logger instance
export const logger = new Logger();

// Export types for external use
export type { LogEntry };