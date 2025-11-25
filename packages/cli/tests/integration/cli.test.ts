import { execSync } from 'child_process';
import { describe, it, expect } from 'vitest';

describe('CLI Integration Tests', () => {
    it('should show help when no command is provided', () => {
        const output = execSync('bun run src/cli.ts --help', { encoding: 'utf8' });
        expect(output).toContain('insighthub');
        expect(output).toContain('help');
    });

    it('should show version information', () => {
        const output = execSync('bun run src/cli.ts --version', { encoding: 'utf8' });
        expect(output).toContain('0.1.0');
    });
});
