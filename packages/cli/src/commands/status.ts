import { Command } from 'commander';
import chalk from 'chalk';
import Table from 'cli-table3';
import { InsightHubApiClient } from '../lib/api';
import { getConfig } from '../lib/config';

export const statusCommand = new Command('status').description(
    'Show system status and information'
);

statusCommand.action(async () => {
    const config = getConfig();
    const client = new InsightHubApiClient(config);

    console.log(chalk.bold('InsightHub System Status\n'));

    // Configuration status
    console.log(chalk.bold('Configuration:'));
    console.log(`  API URL: ${chalk.cyan(config.api.url)}`);
    console.log(
        `  Default Workspace: ${config.workspace.default ? chalk.cyan(config.workspace.default) : chalk.gray('None')}`
    );
    console.log(`  Output Format: ${chalk.cyan(config.output.format)}`);
    console.log(
        `  Color Output: ${config.output.color ? chalk.green('Enabled') : chalk.red('Disabled')}`
    );

    // Server connection status
    console.log(chalk.bold('\nServer Connection:'));
    try {
        const health = await client.health();
        console.log(`  Status: ${chalk.green('Connected')}`);
        console.log(`  Response Time: ${chalk.cyan('OK')}`);

        if (health.version) {
            console.log(`  Version: ${chalk.cyan(health.version)}`);
        }
    } catch (error: any) {
        console.log(`  Status: ${chalk.red('Disconnected')}`);
        console.log(`  Error: ${chalk.red(error.message)}`);
    }

    // Authentication status
    console.log(chalk.bold('\nAuthentication:'));
    try {
        const profile = await client.getProfile();
        console.log(`  Status: ${chalk.green('Authenticated')}`);
        console.log(`  User: ${chalk.cyan(profile.user.email)}`);
        if (profile.user.full_name) {
            console.log(`  Name: ${chalk.cyan(profile.user.full_name)}`);
        }
    } catch {
        console.log(`  Status: ${chalk.red('Not authenticated')}`);
        console.log(`  Note: ${chalk.yellow('Run "insighthub init" to configure authentication')}`);
    }

    // Workspaces summary
    console.log(chalk.bold('\nWorkspaces:'));
    try {
        const workspaces = await client.listWorkspaces();
        if (workspaces.workspaces.length === 0) {
            console.log(`  Count: ${chalk.yellow('0')} ${chalk.gray('(No workspaces found)')}`);
        } else {
            console.log(`  Count: ${chalk.cyan(workspaces.workspaces.length)}`);

            const table = new Table({
                head: ['Name', 'RAG Type', 'Documents', 'Sessions'],
                colWidths: [20, 10, 10, 10],
                style: {
                    head: ['cyan'],
                    border: ['gray'],
                },
            });

            workspaces.workspaces.slice(0, 5).forEach((workspace) => {
                // Determine RAG type based on config structure
                let ragType = 'unknown';
                if (workspace.rag_config) {
                    if ('embedding_algorithm' in workspace.rag_config) {
                        ragType = 'vector';
                    } else if ('entity_extraction_algorithm' in workspace.rag_config) {
                        ragType = 'graph';
                    }
                }

                table.push([
                    workspace.name,
                    ragType,
                    workspace.document_count || 0,
                    workspace.session_count || 0,
                ]);
            });

            console.log(table.toString());

            if (workspaces.workspaces.length > 5) {
                console.log(chalk.gray(`  ... and ${workspaces.workspaces.length - 5} more`));
            }
        }
    } catch (error: any) {
        console.log(`  Error: ${chalk.red(error.message)}`);
    }

    // Quick actions
    console.log(chalk.bold('\nQuick Actions:'));
    console.log(`  ${chalk.cyan('insighthub init')}     - Configure CLI`);
    console.log(`  ${chalk.cyan('insighthub health check')} - Test server connection`);
    console.log(`  ${chalk.cyan('insighthub workspaces list')} - List all workspaces`);
    console.log(`  ${chalk.cyan('insighthub docs upload <file>')} - Upload documents`);
});
