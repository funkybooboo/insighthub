import { Command } from 'commander';

export const chatCommand = new Command('chat').description('Chat with documents');

chatCommand
    .command('send <message>')
    .description('Send a chat message')
    .action(async (message: string) => {
        console.log(`Chat not yet implemented. Message: ${message}`);
    });
