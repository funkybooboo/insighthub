import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';
import { InsightHubApiClient } from '../lib/api';
import { getConfig } from '../lib/config';

export const chatCommand = new Command('chat').description('Chat with documents');

chatCommand
    .command('send <message>')
    .description('Send a chat message and get response')
    .option('-w, --workspace <id>', 'Workspace ID (uses default if not specified)')
    .option('-s, --session <id>', 'Chat session ID (creates new if not specified)')
    .option('--rag-mode <mode>', 'RAG mode (vector, graph, hybrid)', 'vector')
    .option('--stream', 'Stream response in real-time', true)
    .action(async (message: string, options: any) => {
        const spinner = ora('Sending message...').start();

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

            let sessionId = options.session;

            // Create new session if not specified
            if (!sessionId) {
                spinner.text = 'Creating chat session...';
                const { session } = await client.createSession(parseInt(workspaceId), `CLI Chat ${new Date().toISOString()}`);
                sessionId = session.id;
            }

            // Send message
            spinner.text = 'Getting response...';
            const response = await client.sendMessage(sessionId, message, options.ragMode);

            spinner.succeed('Response received');

            console.log(chalk.bold('\nResponse:'));
            console.log(response.message);

            console.log(chalk.gray(`\nSession: ${sessionId}`));
        } catch (error: any) {
            spinner.fail('Failed to send message');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });

chatCommand
    .command('interactive')
    .description('Start interactive chat session')
    .option('-w, --workspace <id>', 'Workspace ID (uses default if not specified)')
    .option('--rag-mode <mode>', 'RAG mode (vector, graph, hybrid)', 'vector')
    .action(async (options: any) => {
        console.log(chalk.bold('InsightHub Interactive Chat'));
        console.log(chalk.gray('Type "exit" or "quit" to end the session\n'));

        const config = getConfig();
        const client = new InsightHubApiClient(config);

        // Use specified workspace or default
        const workspaceId = options.workspace || config.workspace.default;
        if (!workspaceId) {
            console.error(chalk.red('Please specify a workspace with --workspace or set a default workspace'));
            console.log('Use: insighthub workspaces list  # to see available workspaces');
            process.exit(1);
        }

        // Create session
        const spinner = ora('Creating chat session...').start();
        const { session } = await client.createSession(parseInt(workspaceId), `CLI Interactive ${new Date().toISOString()}`);
        spinner.succeed(`Session created: ${session.id}`);

        let messageCount = 0;

        while (true) {
            const { message } = await inquirer.prompt([
                {
                    type: 'input',
                    name: 'message',
                    message: chalk.cyan('You:'),
                    validate: (input: string) => input.trim().length > 0 || 'Please enter a message',
                },
            ]);

            const trimmedMessage = message.trim();

            if (['exit', 'quit', 'q'].includes(trimmedMessage.toLowerCase())) {
                console.log(chalk.yellow('Goodbye!'));
                break;
            }

            const msgSpinner = ora('Thinking...').start();

            try {
                const response = await client.sendMessage(session.id, trimmedMessage, options.ragMode);
                msgSpinner.succeed('Response received');

                console.log(chalk.bold('\nAssistant:'));
                console.log(response.message);

                messageCount++;
                console.log(chalk.gray(`\n--- Message ${messageCount} ---\n`));
            } catch (error: any) {
                msgSpinner.fail('Failed to get response');
                console.error(chalk.red(`Error: ${error.message}`));
            }
        }
    });

chatCommand
    .command('sessions')
    .description('List chat sessions')
    .option('-w, --workspace <id>', 'Workspace ID (uses default if not specified)')
    .action(async (options: any) => {
        const spinner = ora('Fetching chat sessions...').start();

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

            const { sessions, count } = await client.listSessions(parseInt(workspaceId));

            spinner.succeed(`${count} sessions found`);

            if (sessions.length === 0) {
                console.log(chalk.yellow('No chat sessions found.'));
                console.log('Start a conversation with: insighthub chat send "Hello"');
                return;
            }

            console.log(`\nChat sessions in workspace ${workspaceId}:`);
            sessions.forEach((session) => {
                console.log(`- ${chalk.bold(session.title)} (${session.id})`);
                console.log(`  Created: ${new Date(session.created_at).toLocaleString()}`);
                console.log(`  Messages: ${session.message_count || 0}`);
                console.log('');
            });
        } catch (error: any) {
            spinner.fail('Failed to fetch sessions');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });

chatCommand
    .command('history <sessionId>')
    .description('Show chat session history')
    .action(async (sessionId: string) => {
        const spinner = ora('Fetching chat history...').start();

        try {
            const config = getConfig();
            const client = new InsightHubApiClient(config);

            const { messages, count } = await client.getMessages(sessionId);

            spinner.succeed(`${count} messages found`);

            if (messages.length === 0) {
                console.log(chalk.yellow('No messages in this session.'));
                return;
            }

            console.log(chalk.bold(`\nChat History (Session: ${sessionId})\n`));

            messages.forEach((message) => {
                const role = message.role === 'user' ? chalk.cyan('You') : chalk.green('Assistant');
                const timestamp = new Date(message.created_at).toLocaleTimeString();

                console.log(`${role} [${timestamp}]:`);
                console.log(`${message.content}\n`);
            });
        } catch (error: any) {
            spinner.fail('Failed to fetch chat history');
            console.error(chalk.red(`Error: ${error.message}`));
            process.exit(1);
        }
    });
