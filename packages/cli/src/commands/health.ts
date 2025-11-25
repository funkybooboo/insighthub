import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { InsightHubApiClient } from '../lib/api';
import { getConfig } from '../lib/config';

export const healthCommand = new Command('health').description('Check system health and status');

healthCommand
    .command('check')
    .description('Check InsightHub server health')
    .action(async () => {
        const spinner = ora('Checking server health...').start();

        try {
            const config = getConfig();
            const client = new InsightHubApiClient(config);
            const health = await client.health();

            spinner.succeed('Server is healthy');

            console.log(chalk.bold('\nHealth Status:'));
            console.log(`Status: ${chalk.green('OK')}`);
            console.log(`Timestamp: ${new Date().toISOString()}`);

            if (health.version) {
                console.log(`Version: ${health.version}`);
            }

            if (health.services) {
                console.log(chalk.bold('\nServices:'));
                for (const [service, status] of Object.entries(health.services)) {
                    const statusColor = status === 'healthy' ? chalk.green : chalk.red;
                    console.log(`${service}: ${statusColor(status)}`);
                }
            }
        } catch (error: any) {
            spinner.fail('Health check failed');
            console.error(chalk.red(`Error: ${error.message}`));

            if (error.message.includes('Cannot connect')) {
                console.log(chalk.yellow('\nSuggestions:'));
                console.log('• Make sure the InsightHub server is running');
                console.log('• Check the API URL with: insighthub config get api.url');
                console.log('• Start the server with: task server');
            }

            process.exit(1);
        }
    });
