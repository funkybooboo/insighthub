import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import Table from 'cli-table3';
import inquirer from 'inquirer';
import * as fs from 'fs-extra';
import * as path from 'path';
import mime from 'mime-types';
import { InsightHubApiClient } from '../lib/api';
import { getConfig } from '../lib/config';

export const docsCommand = new Command('docs').description('Manage documents');

docsCommand
    .command('list')
    .description('List documents in workspace')
    .option('-w, --workspace <id>', 'Workspace ID (uses default if not specified)')
    .action(async (options: any) => {
        const spinner = ora('Fetching documents...').start();

        try {
            const config = getConfig();
            const client = new InsightHubApiClient(config);

            // Use specified workspace or default
            const workspaceId = options.workspace || config.workspace.default;
            if (!workspaceId) {
                spinner.fail('No workspace specified');
                console.error(chalk.red('Please specify a workspace with --workspace or set a default workspace'));
                console.log('Use: insighthub workspaces list  # to see available workspaces');
                process.exit(1);
            }

            const { documents, count } = await client.listDocuments(parseInt(workspaceId));

            spinner.succeed(`${count} documents found`);

            if (documents.length === 0) {
                console.log(chalk.yellow('No documents found in this workspace.'));
                console.log('Upload your first document with: insighthub docs upload <file>');
                return;
            }

            const table = new Table({
                head: [chalk.bold('ID'), chalk.bold('Name'), chalk.bold('Status'), chalk.bold('Size'), chalk.bold('Uploaded')],
                colWidths: [36, 25, 12, 10, 20],
            });

            documents.forEach((doc) => {
                const statusColor = doc.status === 'ready' ? chalk.green :
                                   doc.status === 'failed' ? chalk.red :
                                   chalk.yellow;
                const size = doc.file_size ? `${(doc.file_size / 1024).toFixed(1)}KB` : 'N/A';
                table.push([
                    doc.id.substring(0, 8) + '...',
                    doc.filename.length > 24 ? doc.filename.substring(0, 21) + '...' : doc.filename,
                    statusColor(doc.status),
                    size,
                    new Date(doc.created_at).toLocaleDateString(),
                ]);
            });

            console.log(`\nDocuments in workspace ${workspaceId}:`);
            console.log(table.toString());
        } catch (error: any) {
            spinner.fail('Failed to fetch documents');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });

docsCommand
    .command('upload <file>')
    .description('Upload a document to workspace')
    .option('-w, --workspace <id>', 'Workspace ID (uses default if not specified)')
    .action(async (filePath: string, options: any) => {
        const spinner = ora('Uploading document...').start();

        try {
            // Validate file exists
            if (!await fs.pathExists(filePath)) {
                spinner.fail('File not found');
                console.error(chalk.red(`File does not exist: ${filePath}`));
                process.exit(1);
            }

            // Get file info
            const stats = await fs.stat(filePath);
            const filename = path.basename(filePath);
            const mimeType = mime.lookup(filename) || 'application/octet-stream';

            // Validate file size (50MB limit)
            const maxSize = 50 * 1024 * 1024;
            if (stats.size > maxSize) {
                spinner.fail('File too large');
                console.error(chalk.red(`File size (${(stats.size / 1024 / 1024).toFixed(1)}MB) exceeds limit (50MB)`));
                process.exit(1);
            }

            const config = getConfig();
            const client = new InsightHubApiClient(config);

            // Use specified workspace or default
            const workspaceId = options.workspace || config.workspace.default;
            if (!workspaceId) {
                spinner.fail('No workspace specified');
                console.error(chalk.red('Please specify a workspace with --workspace or set a default workspace'));
                console.log('Use: insighthub workspaces list  # to see available workspaces');
                process.exit(1);
            }

            // Read file
            const fileBuffer = await fs.readFile(filePath);

            // Upload
            const result = await client.uploadDocument(
                parseInt(workspaceId),
                fileBuffer,
                filename,
                mimeType
            );

            spinner.succeed(`Document "${filename}" uploaded successfully`);

            console.log(chalk.bold('\nUpload Details:'));
            console.log(`Document ID: ${result.document.id}`);
            console.log(`Filename: ${result.document.filename}`);
            console.log(`Size: ${(stats.size / 1024).toFixed(1)}KB`);
            console.log(`Status: ${chalk.yellow(result.document.status)}`);
            console.log(`Workspace: ${workspaceId}`);

            console.log('\nThe document will be processed automatically.');
            console.log('Check status with: insighthub docs status <document-id>');
        } catch (error: any) {
            spinner.fail('Failed to upload document');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });

docsCommand
    .command('status <documentId>')
    .description('Check document processing status')
    .option('-w, --workspace <id>', 'Workspace ID (uses default if not specified)')
    .action(async (documentId: string, options: any) => {
        const spinner = ora('Checking document status...').start();

        try {
            const config = getConfig();
            const client = new InsightHubApiClient(config);

            // Use specified workspace or default
            const workspaceId = options.workspace || config.workspace.default;
            if (!workspaceId) {
                spinner.fail('No workspace specified');
                console.error(chalk.red('Please specify a workspace with --workspace or set a default workspace'));
                process.exit(1);
            }

            const { document } = await client.getDocumentStatus(parseInt(workspaceId), documentId);

            spinner.succeed('Document status retrieved');

            const statusColor = document.status === 'ready' ? chalk.green :
                               document.status === 'failed' ? chalk.red :
                               chalk.yellow;

            console.log(chalk.bold(`\nDocument: ${document.filename}`));
            console.log(`ID: ${document.id}`);
            console.log(`Status: ${statusColor(document.status)}`);
            console.log(`Size: ${document.file_size ? `${(document.file_size / 1024).toFixed(1)}KB` : 'N/A'}`);
            console.log(`Uploaded: ${new Date(document.created_at).toLocaleString()}`);

            if (document.status === 'ready') {
                console.log('\nDocument is ready for chat queries!');
                console.log('Try: insighthub chat send "What is this document about?"');
            } else if (document.status !== 'failed' && document.status !== 'pending') {
                console.log('\nDocument is still being processed. Check back in a few moments.');
            }
        } catch (error: any) {
            spinner.fail('Failed to check document status');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });

docsCommand
    .command('delete <documentId>')
    .description('Delete a document')
    .option('-w, --workspace <id>', 'Workspace ID (uses default if not specified)')
    .option('-f, --force', 'Skip confirmation prompt')
    .action(async (documentId: string, options: any) => {
        if (!options.force) {
            const { confirm } = await inquirer.prompt([
                {
                    type: 'confirm',
                    name: 'confirm',
                    message: `Are you sure you want to delete document ${documentId}? This action cannot be undone.`,
                    default: false,
                },
            ]);

            if (!confirm) {
                console.log(chalk.yellow('Deletion cancelled.'));
                return;
            }
        }

        const spinner = ora('Deleting document...').start();

        try {
            const config = getConfig();
            const client = new InsightHubApiClient(config);

            // Use specified workspace or default
            const workspaceId = options.workspace || config.workspace.default;
            if (!workspaceId) {
                spinner.fail('No workspace specified');
                console.error(chalk.red('Please specify a workspace with --workspace or set a default workspace'));
                process.exit(1);
            }

            await client.deleteDocument(parseInt(workspaceId), documentId);

            spinner.succeed('Document deleted successfully');
        } catch (error: any) {
            spinner.fail('Failed to delete document');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });
