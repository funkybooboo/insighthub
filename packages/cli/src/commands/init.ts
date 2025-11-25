import { Command } from 'commander';
import chalk from 'chalk';
import inquirer from 'inquirer';
import { InsightHubApiClient } from '../lib/api';
import { getConfig, saveConfig } from '../lib/config';

export const initCommand = new Command('init').description(
    'Initialize InsightHub CLI configuration'
);

initCommand.action(async () => {
    console.log(chalk.bold('InsightHub CLI Setup'));
    console.log("Let's configure your CLI to connect to InsightHub.\n");

    const config = getConfig();

    // Check if already configured
    if (config.api.url !== 'http://localhost:5000' || config.workspace.default) {
        const { reconfigure } = await inquirer.prompt([
            {
                type: 'confirm',
                name: 'reconfigure',
                message: 'CLI appears to be already configured. Reconfigure?',
                default: false,
            },
        ]);

        if (!reconfigure) {
            console.log(chalk.yellow('Setup cancelled.'));
            return;
        }
    }

    // API URL configuration
    const { apiUrl } = await inquirer.prompt([
        {
            type: 'input',
            name: 'apiUrl',
            message: 'InsightHub API URL:',
            default: config.api.url,
            validate: (input: string) => {
                try {
                    new URL(input);
                    return true;
                } catch {
                    return 'Please enter a valid URL';
                }
            },
        },
    ]);

    // Test connection
    console.log('\nTesting connection...');
    const testConfig = { ...config, api: { ...config.api, url: apiUrl } };
    const testClient = new InsightHubApiClient(testConfig);

    try {
        await testClient.health();
        console.log(chalk.green('Connection successful!'));
    } catch (error: any) {
        console.log(chalk.yellow(`Could not connect to ${apiUrl}`));
        console.log(`   Error: ${error.message}`);

        const { continue: shouldContinue } = await inquirer.prompt([
            {
                type: 'confirm',
                name: 'continue',
                message: 'Continue with setup anyway?',
                default: true,
            },
        ]);

        if (!shouldContinue) {
            console.log(chalk.yellow('Setup cancelled.'));
            return;
        }
    }

    // Default workspace (optional)
    const { setDefaultWorkspace } = await inquirer.prompt([
        {
            type: 'confirm',
            name: 'setDefaultWorkspace',
            message: 'Would you like to set a default workspace?',
            default: false,
        },
    ]);

    let defaultWorkspace;
    if (setDefaultWorkspace) {
        const { workspaceName } = await inquirer.prompt([
            {
                type: 'input',
                name: 'workspaceName',
                message: 'Default workspace name:',
            },
        ]);
        defaultWorkspace = workspaceName;
    }

    // Save configuration
    const newConfig = {
        api: { ...config.api, url: apiUrl },
        workspace: { ...config.workspace, default: defaultWorkspace },
    };

    saveConfig(newConfig);

    console.log(chalk.green('\nInsightHub CLI configured successfully!'));
    console.log('\nYou can now use commands like:');
    console.log('  - insighthub health check    - Test server connection');
    console.log('  - insighthub workspaces list - List your workspaces');
    console.log('  - insighthub docs upload     - Upload documents');

    if (defaultWorkspace) {
        console.log(`\nDefault workspace set to: ${chalk.cyan(defaultWorkspace)}`);
    }
});
