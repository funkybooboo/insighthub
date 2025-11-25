import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import Table from 'cli-table3';
import inquirer from 'inquirer';
import { InsightHubApiClient } from '../lib/api';
import { getConfig } from '../lib/config';

export const workspacesCommand = new Command('workspaces').description('Manage workspaces');

workspacesCommand
    .command('list')
    .description('List all workspaces')
    .action(async () => {
        const spinner = ora('Fetching workspaces...').start();

        try {
            const config = getConfig();
            const client = new InsightHubApiClient(config);
            const { workspaces } = await client.listWorkspaces();

            spinner.succeed('Workspaces retrieved');

            if (workspaces.length === 0) {
                console.log(chalk.yellow('No workspaces found.'));
                console.log('Create your first workspace with: insighthub workspaces create <name>');
                return;
            }

            const table = new Table({
                head: [chalk.bold('ID'), chalk.bold('Name'), chalk.bold('Status'), chalk.bold('Created')],
                colWidths: [8, 25, 12, 20],
            });

            workspaces.forEach((workspace) => {
                const statusColor = workspace.status === 'ready' ? chalk.green :
                                   workspace.status === 'provisioning' ? chalk.yellow :
                                   chalk.red;
                table.push([
                    workspace.id,
                    workspace.name,
                    statusColor(workspace.status),
                    new Date(workspace.created_at).toLocaleDateString(),
                ]);
            });

            console.log('\n' + table.toString());
        } catch (error: any) {
            spinner.fail('Failed to fetch workspaces');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });

workspacesCommand
    .command('create <name>')
    .description('Create a new workspace')
    .option('-d, --description <description>', 'Workspace description')
    .option('--rag-mode <mode>', 'RAG mode (vector, graph, hybrid)', 'vector')
    .action(async (name: string, options: any) => {
        const spinner = ora('Creating workspace...').start();

        try {
            const config = getConfig();
            const client = new InsightHubApiClient(config);

            const ragConfig = {
                mode: options.ragMode,
                // Add more RAG config options as needed
            };

            const { workspace } = await client.createWorkspace(
                name,
                options.description,
                ragConfig
            );

            spinner.succeed(`Workspace "${workspace.name}" created successfully`);

            console.log(chalk.bold('\nWorkspace Details:'));
            console.log(`ID: ${workspace.id}`);
            console.log(`Name: ${workspace.name}`);
            console.log(`Status: ${chalk.yellow(workspace.status)}`);
            console.log(`Created: ${new Date(workspace.created_at).toLocaleString()}`);

            if (options.description) {
                console.log(`Description: ${options.description}`);
            }

            console.log('\nNext steps:');
            console.log('1. Upload documents: insighthub docs upload <file>');
            console.log('2. Start chatting: insighthub chat send "Hello"');
        } catch (error: any) {
            spinner.fail('Failed to create workspace');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });

workspacesCommand
    .command('info <id>')
    .description('Get workspace information')
    .action(async (id: string) => {
        const spinner = ora('Fetching workspace info...').start();

        try {
            const config = getConfig();
            const client = new InsightHubApiClient(config);
            const { workspace } = await client.getWorkspace(parseInt(id));

            spinner.succeed('Workspace info retrieved');

            console.log(chalk.bold(`\nWorkspace: ${workspace.name}`));
            console.log(`ID: ${workspace.id}`);
            console.log(`Status: ${workspace.status}`);
            console.log(`Created: ${new Date(workspace.created_at).toLocaleString()}`);
            console.log(`Updated: ${new Date(workspace.updated_at).toLocaleString()}`);

            if (workspace.description) {
                console.log(`Description: ${workspace.description}`);
            }

            if (workspace.rag_config) {
                console.log('\nRAG Configuration:');
                // Handle the union type - for now just show it's configured
                console.log('RAG: Configured');
            }
        } catch (error: any) {
            spinner.fail('Failed to fetch workspace info');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });

workspacesCommand
    .command('delete <id>')
    .description('Delete a workspace')
    .option('-f, --force', 'Skip confirmation prompt')
    .action(async (id: string, options: any) => {
        if (!options.force) {
            const { confirm } = await inquirer.prompt([
                {
                    type: 'confirm',
                    name: 'confirm',
                    message: `Are you sure you want to delete workspace ${id}? This action cannot be undone.`,
                    default: false,
                },
            ]);

            if (!confirm) {
                console.log(chalk.yellow('Deletion cancelled.'));
                return;
            }
        }

        const spinner = ora('Deleting workspace...').start();

        try {
            const config = getConfig();
            const client = new InsightHubApiClient(config);
            await client.deleteWorkspace(parseInt(id));

            spinner.succeed('Workspace deleted successfully');
        } catch (error: any) {
            spinner.fail('Failed to delete workspace');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });
