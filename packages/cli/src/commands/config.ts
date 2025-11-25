import { Command } from 'commander';
import chalk from 'chalk';
import { getConfig, saveConfig } from '../lib/config';

export const configCommand = new Command('config').description('Manage CLI configuration');

configCommand
    .command('show')
    .description('Show current configuration')
    .action(async () => {
        const config = getConfig();
        console.log(chalk.bold('Current Configuration:'));
        console.log(JSON.stringify(config, null, 2));
    });

configCommand
    .command('set <key> <value>')
    .description('Set a configuration value')
    .action(async (key: string, value: string) => {
        try {
            const config = getConfig();

            // Parse nested keys like "api.url"
            const keys = key.split('.');
            let current: any = config;

            for (let i = 0; i < keys.length - 1; i++) {
                if (!current[keys[i]]) {
                    current[keys[i]] = {};
                }
                current = current[keys[i]];
            }

            // Parse value types
            let parsedValue: any = value;
            if (value === 'true') parsedValue = true;
            else if (value === 'false') parsedValue = false;
            else if (!isNaN(Number(value))) parsedValue = Number(value);

            current[keys[keys.length - 1]] = parsedValue;

            saveConfig(config);
            console.log(chalk.green(`✓ Set ${key} = ${parsedValue}`));
        } catch (error: any) {
            console.error(chalk.red(`Error setting config: ${error.message}`));
            process.exit(1);
        }
    });

configCommand
    .command('get <key>')
    .description('Get a configuration value')
    .action(async (key: string) => {
        const config = getConfig();

        const keys = key.split('.');
        let current: any = config;

        try {
            for (const k of keys) {
                current = current[k];
            }

            if (current === undefined) {
                console.log(chalk.yellow(`Key "${key}" not found`));
            } else {
                console.log(current);
            }
        } catch {
            console.log(chalk.yellow(`Key "${key}" not found`));
        }
    });
